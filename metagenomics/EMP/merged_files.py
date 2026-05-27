import os
import argparse
import pandas as pd

def parse_filtered_hits(folder_path, metadata_file, taxonomy_file, output_file):
    results = []

    # load metadata file (run_accession, sample_accession, experiment_accession, study_accession, sample_name)
    metadata_df = pd.read_csv(metadata_file, sep="\t", dtype=str)

    # Load taxonomy file and keep only sample_name + empo_1-4
    taxonomy_df = pd.read_csv(taxonomy_file, sep="\t", dtype=str)
    keep_cols = ["sample_name", "empo_1", "empo_2", "empo_3", "empo_4"]
    taxonomy_df = taxonomy_df[[col for col in keep_cols if col in taxonomy_df.columns]]

    for filename in os.listdir(folder_path):
        if filename.endswith("_filtered_hits_table.txt"):
            file_id = filename.split("_")[0]
            file_path = os.path.join(folder_path, filename)

            try:
                df = pd.read_csv(file_path, sep="\t", dtype=str)
            except pd.errors.EmptyDataError:
                print(f"Empty file: {filename}, skip.")
                continue

            if df.empty:
                print(f"Empty file: {filename}, skip.")
                continue

            df = df[df["Rank"] == "species"]

            if df.empty:
                print(f"No 'species' line in {filename}, skip.")
                continue

            df.insert(0, "File_ID", file_id)

            meta_match = metadata_df[
                (metadata_df["run_accession"] == file_id) |
                (metadata_df["sample_accession"] == file_id) |
                (metadata_df["experiment_accession"] == file_id) |
                (metadata_df["study_accession"] == file_id)
            ]

            if not meta_match.empty:
                sample_name = meta_match["sample_name"].values[0]
                df["sample_name"] = sample_name
            else:
                df["sample_name"] = None
                print(f"No match for {file_id} in the metadata file.")

            results.append(df)

    if results:
        final_df = pd.concat(results, ignore_index=True)

        final_df = final_df.merge(taxonomy_df, on="sample_name", how="left")

        final_df.to_csv(output_file, sep="\t", index=False)
    else:
        print("No valid file found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse filtered hits and merge with metadata/taxonomy info.")
    parser.add_argument("folder", help="Dir with file *_filtered_hits_table.txt")
    parser.add_argument("metadata", help="Metadata file with run_accession, sample_accession, experiment_accession, study_accession, sample_name")
    parser.add_argument("taxonomy", help="Taxonomy file with sample_name, empo_1-4")
    parser.add_argument("-o", "--output", default="merged_filtered_hits_with_metadata.tsv", help="Output file")

    args = parser.parse_args()

    parse_filtered_hits(args.folder, args.metadata, args.taxonomy, args.output)
