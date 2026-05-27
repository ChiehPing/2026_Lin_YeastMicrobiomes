#!/bin/bash
set -euo pipefail

source "$(conda info --base)/etc/profile.d/conda.sh"

#####################################
# CONFIG
#####################################
DB_NAME="$1"
FASTQ_DIR="$2"
OUT_DIR="$3"
TMP_DIR="$4"
THREADS=40
JOBS=1
LEN_MIN=10000
CONF=0.4
LEVEL="S"      # taxonomic level for Bracken (S = species)
USE_BRACKEN=1 #can take 0 | 1 value
NLEN_FIX=0 #0 -> it computes the median_len; != 0 -> fix length

mkdir -p "$OUT_DIR" "$TMP_DIR"

#####################################
# DB IN RAM (/dev/shm)
#####################################
DB_RAM="/dev/shm/db"
DB_USED="$DB_RAM"

ID_FILE="$OUT_DIR/sample_ids.txt"

echo ">>> Unique IDs list"
ls "$FASTQ_DIR"/*.fastq.gz | sed -E 's/(_[12])?\.fastq\.gz$//' | xargs -n1 basename | sort -u > "$ID_FILE"

echo ">>> File ID generated: $ID_FILE"
cat "$ID_FILE"

#####################################
# ERROR DIR
#####################################
ERROR_DIR="$OUT_DIR/error"
ERROR_LOG="$OUT_DIR/error.log"
mkdir -p "$ERROR_DIR"
: > "$ERROR_LOG"

process_sample() {
    local id="$1"
    echo ">>> Processing sample: $id"

    local OUT_PREFIX="$OUT_DIR/$id"
    local LOG_FILE="${OUT_PREFIX}.log"
    local fq1="${FASTQ_DIR}/${id}_1.fastq.gz"
    local fq2="${FASTQ_DIR}/${id}_2.fastq.gz"
    local fq_single="${FASTQ_DIR}/${id}.fastq.gz"
    local TMP_FASTQ="${TMP_DIR}/${id}.fastq"

    if [[ -f "${OUT_PREFIX}.bracken.${LEVEL}.report" ]]; then
        echo ">>> SKIP $id: data already analyzed."
        exit 0
    fi

    {
      if [[ -f "$fq1" && -f "$fq2" ]]; then
	  echo "Paired-end found: check the number of reads in $fq1 and $fq2..."
          len1=$(zcat "$fq1" | awk 'NR % 4 == 2 {n++; sum += length($0)} END {print n, sum}')
          len2=$(zcat "$fq2" | awk 'NR % 4 == 2 {n++; sum += length($0)} END {print n, sum}')

          count1=$(echo "$len1" | cut -d' ' -f1)
          count2=$(echo "$len2" | cut -d' ' -f1)

	  if (( count1 < LEN_MIN || count2 < LEN_MIN )); then
              echo ">>> SKIP $id: number of reads too low (_1: $count1, _2: $count2)"
              return 0
          fi

          echo "Paired-end found, generating interleave..."
          conda run -n seqfu seqfu interleave -1 "$fq1" -2 "$fq2" > "$TMP_FASTQ"

      elif [[ -f "$fq1" && ! -f "$fq2" ]]; then
	  echo "Only $fq1 found: check number of reads..."
          len1=$(zcat "$fq1" | awk 'NR % 4 == 2 {n++; sum += length($0)} END {print n, sum}')
          count1=$(echo "$len1" | cut -d' ' -f1)

	  if (( count1 < LEN_MIN )); then
              echo ">>> SKIP $id: number of reads too low ($count1)"
              return 0
          fi

          echo "Solo $fq1 trovato"
          zcat "$fq1" > "$TMP_FASTQ"

      elif [[ -f "$fq_single" ]]; then
	        echo "Single-end found ($fq_single): check number of reads..."
          len1=$(zcat "$fq_single" | awk 'NR % 4 == 2 {n++; sum += length($0)} END {print n, sum}')
          count1=$(echo "$len1" | cut -d' ' -f1)

	  if (( count1 < LEN_MIN )); then
              echo ">>> SKIP $id: number of reads too low ($count1)"
              return 0
          fi

          echo "Single-end found."
          zcat "$fq_single" > "$TMP_FASTQ"

      else
          echo "$id : no valid fastq.gz file found." >> "$ERROR_LOG"
          return 0
      fi

      echo ">>> Compute reads mean length for $id..."
      local rlen=$(cat "$TMP_FASTQ" | awk 'NR % 4 == 2 {n++; sum += length($0)} END {if(n>0) print int(sum/n); else print 0}')
      local approx_len

      if (( NLEN_FIX == 0 )); then
         approx_len=$(awk -v r="$rlen" 'BEGIN {
           if (r <= 50) print 50;
           else if (r <= 60) print 50;
           else if (r <= 85) print 75;
           else if (r <= 125) print 100;
           else if (r <= 185) print 150;
           else if (r <= 225) print 200;
           else if (r <= 285) print 250;
           else print 300;
         }')

      else
         approx_len=$NLEN_FIX
      fi

      echo ">>> approx: $approx_len bp"

      conda run -n kraken2 kraken2 --db "$DB_USED" \
                --threads "$((THREADS_PER_JOB))" \
                --memory-mapping \
	              --unclassified-out "${OUT_PREFIX}.k2.unc.fastq" \
	              --classified-out "${OUT_PREFIX}.k2.c.fastq" \
                --output "${OUT_PREFIX}.k2" \
                --report "${OUT_PREFIX}.k2.report" \
                --confidence "${CONF}" \
                --use-names "$TMP_FASTQ" 2> "${LOG_FILE}"


      if (( USE_BRACKEN == 1 )); then

         echo ">>> Analysis with Bracken."
         conda run -n kraken2 bracken -d "$DB_NAME" \
           -i "${OUT_PREFIX}.k2.report" \
           -o "${OUT_PREFIX}.bracken.out" \
           -w "${OUT_PREFIX}.bracken.${LEVEL}.report" \
           -r "$approx_len" \
           -l "$LEVEL" \
           -t "$((THREADS_PER_JOB))"

      fi

      # === CLEANUP ===
      rm -f "$TMP_FASTQ"
      rm -f "${OUT_PREFIX}.k2"

    } || {
        echo ">>> ERROR with file $id, move the files in $ERROR_DIR"
        mv ${OUT_PREFIX}* "$ERROR_DIR"/ 2>/dev/null || true
        rm -f "$TMP_FASTQ"
        return 1
    }
}

export -f process_sample
export FASTQ_DIR OUT_DIR TMP_DIR ERROR_DIR ERROR_LOG DB_USED DB_NAME CONF LEVEL THREADS USE_BRACKEN NLEN_FIX

THREADS_PER_JOB=$(( THREADS / JOBS ))

echo ">>> Parallel start -> parallel jobs:  $JOBS, thread/job: $THREADS_PER_JOB "
export THREADS_PER_JOB

parallel -j "$JOBS" process_sample :::: "$ID_FILE"
