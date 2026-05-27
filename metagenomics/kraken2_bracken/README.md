# Taxonomic Classification Pipeline (Kraken2 + Bracken)

This repository contains the scripts and documentation for a high-performance taxonomic classification pipeline optimized for fungal genomes. The core script, `k2_b_classification.sh`, automates sequence quality checks, interleaving, taxonomic assignment with **Kraken2**, and abundance estimation with **Bracken**.

## System Requirements & Environment

The pipeline was developed and optimized for high-performance computing environments. 

**Reference Hardware:**
* **OS:** Ubuntu 24.04.3 LTS x86-64
* **CPU:** AMD EPYC 9374F (128 threads) @ 3.850GHz
* **RAM:** 512 GB (Crucial for in-RAM database loading)

**Software Dependencies:**
* `kraken2` and `bracken` (Conda environment)
* `seqfu` (for FASTQ interleaving)
* `vmtouch` (for RAM caching control)
* GNU `parallel`

---

## Database Construction

The classification relies on a custom fungal database built by combining the standard RefSeq Fungi database with manually curated FASTA files from the JGI MycoCosm portal (`fungi_refseq_JGI.fa`). 

### 1. Download Taxonomy
```bash
conda run -n kraken2 k2 download-taxonomy \
    --db $DB_NAME \
    --log $LOG_TAXONOMY
```

### 2. Add Custom Genomes to Library
```bash
kraken2-build --add-to-library fungi_refseq_JGI.fa \
    --db $DB_NAME \
    --threads 40
```

### 3. Build the Final Database
```bash
kraken2-build --build \
    --db $DB_NAME \
    --threads 40
```

---

## RAM Optimization (Database Preloading)

To maximize I/O speed and fully leverage the server's memory, the Kraken2 database is loaded directly into the RAM disk (`/dev/shm`). `vmtouch` is used to lock the `.k2d` files into memory.

**1. Load Database into RAM:**
```bash
# Copy DB files to RAM disk, then lock them in memory
vmtouch -vt /dev/shm/db/*.k2d
```

**2. Evict and Cleanup (Post-Analysis):**
```bash
# Evict files from RAM cache
vmtouch -ve /dev/shm/db/*.k2d

# Manually remove the files from the RAM disk
rm -rf /dev/shm/db/*.k2d
```

---

## Script Usage: `k2_b_classification.sh`

This script processes multiple FASTQ files (single-end or paired-end) in parallel. It dynamically calculates the median read length for each sample to optimize Bracken's abundance estimation.

### Execution
```bash
./k2_b_classification.sh <DB_NAME> <FASTQ_DIR> <OUT_DIR> <TMP_DIR>
```

### Positional Arguments

| Argument | Description |
| :--- | :--- |
| `$1` (`DB_NAME`) | Path to the Kraken2/Bracken database folder. |
| `$2` (`FASTQ_DIR`) | Directory containing the input `.fastq.gz` files. |
| `$3` (`OUT_DIR`) | Directory where classification reports and logs will be saved. |
| `$4` (`TMP_DIR`) | Temporary directory for interleaving and intermediate files. |

### Internal Configuration Flags
You can modify these variables at the top of the script to adjust the pipeline's behavior:

* **`THREADS=40`**: Total number of threads allocated for the script.
* **`JOBS=1`**: Number of samples to process simultaneously via GNU Parallel.
* **`LEN_MIN=10000`**: Minimum number of reads required to process a sample. Files below this threshold are skipped.
* **`CONF=0.4`**: Confidence score threshold for Kraken2.
* **`LEVEL="S"`**: Taxonomic level for Bracken abundance estimation (S = Species, G = Genus).
* **`USE_BRACKEN=1`**: Toggle Bracken analysis (1 = Yes, 0 = No).
* **`NLEN_FIX=0`**: If `0`, the script dynamically calculates read length for Bracken. If set to a specific number (e.g., `150`), it forces a fixed length.

### Pipeline Workflow

1.  **Sample Discovery:** Scans `$FASTQ_DIR` for paired (`_1` / `_2`), single, or pre-interleaved `.fastq.gz` files and generates a unique ID list.
2.  **Quality Check:** Verifies if the sequence depth exceeds the `LEN_MIN` threshold.
3.  **Interleaving:** Uses `seqfu` to generate a temporary interleaved FASTQ for paired-end samples.
4.  **Length Calculation:** Automatically computes the mean read length and maps it to the closest standard Bracken k-mer length (50, 75, 100, 150, 200, 250, or 300 bp).
5.  **Kraken2 Classification:** Runs Kraken2 using memory mapping against the in-RAM database. Output files include `.k2.report`, `.k2.c.fastq` (classified), and `.k2.unc.fastq` (unclassified).
6.  **Bracken Re-estimation:** Generates species-level abundance reports based on Kraken2 classifications.
7.  **Cleanup & Error Handling:** Temporary files are deleted upon successful execution. Failed samples are safely moved to the `error/` subdirectory.
