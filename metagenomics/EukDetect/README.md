# EukDetect Pipeline for Fungal Metagenomic Analysis

This repository contains the configuration scripts and workflow documentation for eukaryotic metagenomic profiling using **EukDetect**. 

*Note: This pipeline was executed using **EukDetect v1.3**. A newer version (v2.0.0) is currently available and maintained at the official [EukDetect GitHub repository](https://github.com/allind/EukDetect).*

## System Requirements & Environment

The classification was performed on a dedicated workstation:
* **OS:** Ubuntu 20.04.6 LTS x86-64
* **System:** Dell Precision 7920 Tower
* **CPU:** Intel Xeon Silver 4214R (48 threads) @ 3.500GHz
* **RAM:** 64 GB

---

## Part 1: Configuration Automation

EukDetect requires specific YAML configuration files based on read type and length. We developed `create_configfile.sh` to automate this process for diverse datasets containing both Single-End (SE) and Paired-End (PE) reads.

### Script: `create_configfile.sh`
**Description:** Automates the creation of EukDetect `.yml` configuration files. It scans the input sequences, drops samples with fewer than 10,000 reads to ensure quality, and generates distinct YAML files grouped by read length and sequencing layout (PE vs SE).

**Usage:**
```bash
./create_configfile.sh <LIST_FILE> <FASTQ_DIR> [OUTPUT_DIR]
```

* **Inputs:**
  * `<LIST_FILE>`: A tab-separated text file with two columns (`ID` and `LENGTH`). Example of `summary_id_length.tsv` from the food dataset in the current directory.
  * `<FASTQ_DIR>`: Absolute path to the directory containing the `.fastq.gz` files.
  * `[OUTPUT_DIR]`: (Optional) Directory to save the generated configuration files.
* **Outputs:** Automatically generated YAML files, such as:
  * `your_configfile151_PAIRED.yml`
  * `your_configfile151_SINGLE.yml`

---

## Part 2: Execution Workflow

Once the marker genes database is downloaded (~ 3 GB) and the configuration files are generated, EukDetect is executed in `runall` mode. We allocate 20 cores per run to balance speed and system stability.

**Usage:**
```bash
eukdetect --mode runall --configfile <CONFIG_FILE.YML> --cores 20
```

---

## Part 3: Output Data Structure

The primary output file utilized for downstream statistical analysis and Jupyter Notebook integration is the filtered hits table containing eukaryotic fractions and taxonomic lineages.

**Output Example:** `<SAMPLE_ID>_filtered_hits_eukfrac.txt`

```text
Lineage	Rank	Name	TaxID	RPKS	Euk_fraction	Reads	Amt_marker_sequence
phylum-Ascomycota	phylum	Ascomycota	4890	0.0111	100.0	4	359693
phylum-Ascomycota|class-Eurotiomycetes	class	Eurotiomycetes	147545	0.0111	100.0	4	359693
phylum-Ascomycota|class-Eurotiomycetes|order-Eurotiales	order	Eurotiales	5042	0.0111	100.0	4	359693
phylum-Ascomycota|class-Eurotiomycetes|order-Eurotiales|family-Aspergillaceae	family	Aspergillaceae	1131492	0.0111	100.0	4	359693
phylum-Ascomycota|class-Eurotiomycetes|order-Eurotiales|family-Aspergillaceae|genus-Penicillium	genus	Penicillium	5073	0.0111	100.0	4	359693
phylum-Ascomycota|class-Eurotiomycetes|order-Eurotiales|family-Aspergillaceae|genus-Penicillium|species-Penicillium_chrysogenum	species	Penicillium chrysogenum	5076	0.0111	100.0	4	359693
```

*These tables are subsequently collected, parsed, and merged to form the final abundance matrices.*
