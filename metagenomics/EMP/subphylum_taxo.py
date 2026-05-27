from ete4 import NCBITaxa
import pandas as pd
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

df = pd.read_csv(input_file, sep="\t", dtype=str)

df["subphylum"] = df.get("subphylum", "NA")

ncbi = NCBITaxa()

for idx, row in df.iterrows():
    if pd.isna(row.get("Lineage")) or pd.isna(row.get("Name")) or row.get("Lineage") in ["", "NA"] or row.get("Name") in ["", "NA"]:
        continue

    if (not pd.isna(row.get("highest_taxa")) and row.get("highest_taxa") != "NA" and
        not pd.isna(row.get("genus")) and row.get("genus") != "NA" and
        not pd.isna(row.get("isyeast")) and row.get("isyeast") != "NA"):
        try:
            if not pd.isna(row.get("Taxid")) and row.get("Taxid") != "NA" and str(row.get("Taxid")).strip():
                taxid = int(row["Taxid"])
            else:
                name2taxid = ncbi.get_name_translator([row["Name"]])
                if row["Name"] in name2taxid and name2taxid[row["Name"]]:
                    taxid = name2taxid[row["Name"]][0]
                else:
                    taxid = None

            if taxid:
                lineage = ncbi.get_lineage(taxid)
                ranks = ncbi.get_rank(lineage)
                names = ncbi.get_taxid_translator(lineage)

                subphylum_list = [names[t] for t in lineage if ranks[t] == "subphylum"]
                if subphylum_list:
                    df.at[idx, "subphylum"] = subphylum_list[0]
        except Exception as e:
            print(f"Error with line {idx}, TaxID/Name {row['Taxid']}/{row['Name']}: {e}")
            df.at[idx, "subphylum"] = "NA"

df.to_csv(output_file, sep="\t", index=False)
