import pandas as pd
import sys

if len(sys.argv) != 7:
    print("Use: python3 merge_all_final.py <file_a.tsv> <file_b.tsv> <reads_length.tsv> <samples.tsv> <output.tsv>")
    sys.exit(1)

file_a_path = sys.argv[1]
file_b_path = sys.argv[2]
reads_path = sys.argv[3]
samples_path = sys.argv[4]
empo_file_path = sys.argv[5]
output_path = sys.argv[6]

file_a = pd.read_csv(file_a_path, sep="\t")
file_b = pd.read_csv(file_b_path, sep="\t")
reads = pd.read_csv(reads_path, sep="\t")
samples = pd.read_csv(samples_path, sep="\t")
empo_file = pd.read_csv(empo_file_path, sep="\t")

common_cols = [col for col in file_a.columns if col in file_b.columns]
if not common_cols:
    print("No columns shared between file_a and file_b, impossible to merge.")
    sys.exit(1)

extra_cols = [c for c in ['highest_taxa', 'genus', 'isyeast'] if c in file_b.columns]

merged = pd.merge(
    file_a,
    file_b[common_cols + extra_cols],
    on=common_cols,
    how='left'
)

if 'ID' not in reads.columns or 'reads_length' not in reads.columns:
    print("Reads file must have columns 'ID' and 'reads_length'")
    sys.exit(1)

reads_renamed = reads.rename(columns={"ID": "File_ID"})
merged = pd.merge(merged, reads_renamed, on="File_ID", how="left")

missing_ids = reads_renamed[~reads_renamed["File_ID"].isin(merged["File_ID"])]

if not missing_ids.empty:
    extra_rows = pd.DataFrame(columns=merged.columns)
    for _, row in missing_ids.iterrows():
        new_row = {col: "NA" for col in merged.columns}
        new_row["File_ID"] = row["File_ID"]
        new_row["reads_length"] = row["reads_length"]
        extra_rows = pd.concat([extra_rows, pd.DataFrame([new_row])], ignore_index=True)

    merged = pd.concat([merged, extra_rows], ignore_index=True)

if not {'sample_name', 'run_accession'}.issubset(samples.columns):
    print("Samples file must have 'sample_name' and 'run_accession'")
    sys.exit(1)

id_to_sample = {}
for _, row in samples.iterrows():
    sample_name = str(row['sample_name'])
    run_accessions = str(row['run_accession']).split(',')
    for rid in run_accessions:
        rid = rid.strip()
        if rid:
            id_to_sample[rid] = sample_name

def update_sample_name(row):
    if row["sample_name"] == "NA" and row["File_ID"] in id_to_sample:
        return id_to_sample[row["File_ID"]]
    return row["sample_name"]

merged["sample_name"] = merged.apply(update_sample_name, axis=1)

empo_cols = ['empo_1', 'empo_2', 'empo_3', 'empo_4']
if not {'sample_name'}.issubset(empo_file.columns):
    print("EMPO file must have the column 'sample_name'")
    sys.exit(1)

empo_map = empo_file.set_index('sample_name')[empo_cols].to_dict(orient='index')

def update_empo(row):
    sname = row['sample_name']
    if sname in empo_map:
        for col in empo_cols:
            if col in row and (row[col] in [None, "NA", ""]):
                row[col] = empo_map[sname][col]
    return row

merged = merged.apply(update_empo, axis=1)

cols = merged.columns.tolist()
if "reads_length" in cols and "File_ID" in cols:
    cols.insert(cols.index("File_ID") + 1, cols.pop(cols.index("reads_length")))
    merged = merged[cols]

merged = merged.fillna("NA")

cols_to_drop = [
    "Observed_markers",
    "Read_counts",
    "Percent_observed_markers",
    "Total_marker_coverage",
    "Percent_identity"
]

merged = merged.drop(columns=[c for c in cols_to_drop if c in merged.columns], errors="ignore")

merged.to_csv(output_path, sep="\t", index=False)
