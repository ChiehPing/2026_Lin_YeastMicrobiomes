#!/bin/bash

# USE:
# ./create_configfile.sh /abs/path/to/list.txt /abs/path/to/fastq_dir [output_dir]
# list.txt: file with columns ID<TAB>LENGTH
# /path/to/fastq_dir: .fastq.gz dir
# output_dir (opzional): dir where to save the config files

LIST_FILE="$1"
FQ_DIR="$2"
OUT_DIR="${3:-.}"

if [[ ! -f "$LIST_FILE" ]]; then
  echo "Error: list file not found: $LIST_FILE" >&2
  exit 1
fi
if [[ ! -d "$FQ_DIR" ]]; then
  echo "Error: fastq.gz dir not found: $FQ_DIR" >&2
  exit 1
fi
mkdir -p "$OUT_DIR"

has_enough_reads() {
  local fq="$1"
  local limit=10000
  if [[ -f "$fq" ]]; then
    local lines
    lines=$(zcat -f "$fq" 2>/dev/null | head -n $((limit*4)) | wc -l)
    local reads=$((lines/4))
    if (( reads >= limit )); then
      return 0
    fi
  fi
  return 1
}

mapfile -t LENGTHS < <(awk '{print $2}' "$LIST_FILE" | sort -u)

for LENGTH in "${LENGTHS[@]}"; do
  TMP_PAIRED=$(mktemp)
  TMP_SINGLE=$(mktemp)

  while IFS= read -r SAMPLE; do
    SAMPLE_TRIM=$(printf '%s' "$SAMPLE" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    [[ -z "$SAMPLE_TRIM" ]] && continue

    if [[ -f "$FQ_DIR/${SAMPLE_TRIM}_1.fastq.gz" && -f "$FQ_DIR/${SAMPLE_TRIM}_2.fastq.gz" ]]; then
      if has_enough_reads "$FQ_DIR/${SAMPLE_TRIM}_1.fastq.gz"; then
        printf '  %s:\n' "$SAMPLE_TRIM" >> "$TMP_PAIRED"
      fi
      #printf '  %s:\n' "$SAMPLE_TRIM" >> "$TMP_PAIRED"
    elif [[ -f "$FQ_DIR/${SAMPLE_TRIM}_1.fastq.gz" ]]; then
      if has_enough_reads "$FQ_DIR/${SAMPLE_TRIM}_1.fastq.gz"; then
        printf '  %s:\n' "$SAMPLE_TRIM" >> "$TMP_SINGLE"
      fi
    elif [[ -f "$FQ_DIR/${SAMPLE_TRIM}.fastq.gz" ]]; then
      if has_enough_reads "$FQ_DIR/${SAMPLE_TRIM}.fastq.gz"; then
        printf '  %s:\n' "$SAMPLE_TRIM" >> "$TMP_SINGLE"
      fi
      #printf '  %s:\n' "$SAMPLE_TRIM" >> "$TMP_SINGLE"
    else
      printf 'WARNING: fastq not found for %s in %s\n' "$SAMPLE_TRIM" "$FQ_DIR" >&2
    fi
  done < <(awk -v len="$LENGTH" '$2==len{print $1}' "$LIST_FILE")

  if [[ -s "$TMP_PAIRED" ]]; then
    OUTFILE="$OUT_DIR/your_configfile${LENGTH}_PAIRED.yml"
    cat > "$OUTFILE" <<EOF
#Config file for eukdetect. Copy and edit for analysis

#Directory where EukDetect output should be written
output_dir: ""

#Indicate whether reads are paired (true) or single (false)
paired_end: true

#filename excluding sample name. no need to edit if paired_end = false
fwd_suffix: "_1.fastq.gz"

#filename excludign sample name. no need to edit if paired_end = false
rev_suffix: "_2.fastq.gz"

#file name excluding sample name. no need to edit if paired_end = true
se_suffix: "_1.fastq.gz"

#length of your reads. pre-trimming reads not recommended
readlen: ${LENGTH}

#full path to directory with raw fastq files
fq_dir: "$FQ_DIR"

#full path to folder with eukdetect database files
database_dir: "/lib/EukDetect/eukdb"

#name of database. Default is original genomes only database name
database_prefix: "ncbi_eukprot_met_arch_markers.fna"

#full path to eukdetect installation folder
eukdetect_dir: "/lib/EukDetect"

#list sample names here. fastqs must correspond to {samplename}{se_suffix} for SE reads or {samplename}{fwd_suffix} and {samplename}{rev_suffix} for PE
#each sample name should be preceded by 2 spaces and followed by a colon character
samples:
$(cat "$TMP_PAIRED")
EOF
    echo "Creato: $OUTFILE"
  fi

  if [[ -s "$TMP_SINGLE" ]]; then
    OUTFILE="$OUT_DIR/your_configfile${LENGTH}_SINGLE.yml"
    cat > "$OUTFILE" <<EOF
#Config file for eukdetect. Copy and edit for analysis

#Directory where EukDetect output should be written
output_dir: ""

#Indicate whether reads are paired (true) or single (false)
paired_end: false

#filename excluding sample name. no need to edit if paired_end = false
fwd_suffix: "_1.fastq.gz"

#filename excludign sample name. no need to edit if paired_end = false
rev_suffix: "_2.fastq.gz"

#file name excluding sample name. no need to edit if paired_end = true
se_suffix: "_1.fastq.gz"

#length of your reads. pre-trimming reads not recommended
readlen: ${LENGTH}

#full path to directory with raw fastq files
fq_dir: "$FQ_DIR"

#full path to folder with eukdetect database files
database_dir: "/lib/EukDetect/eukdb"

#name of database. Default is original genomes only database name
database_prefix: "ncbi_eukprot_met_arch_markers.fna"

#full path to eukdetect installation folder
eukdetect_dir: "/lib/EukDetect"

#list sample names here. fastqs must correspond to {samplename}{se_suffix} for SE reads or {samplename}{fwd_suffix} and {samplename}{rev_suffix} for PE
#each sample name should be preceded by 2 spaces and followed by a colon character
samples:
$(cat "$TMP_SINGLE")
EOF
    echo "Creato: $OUTFILE"
  fi

  rm -f "$TMP_PAIRED" "$TMP_SINGLE"
done
