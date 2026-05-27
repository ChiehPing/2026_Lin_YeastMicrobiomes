import pandas as pd
from ete4 import NCBITaxa
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

df = pd.read_csv(
    input_file,
    sep="\t",
    dtype=str,
    keep_default_na=False,
    na_values=[]
)

ncbi = NCBITaxa()

def get_subphylum(taxid):
    try:
        taxid = str(taxid).strip()
        if not taxid or taxid.upper() == "NA":
            return "NA"
        lineage = ncbi.get_lineage(int(taxid))
        ranks = ncbi.get_rank(lineage)
        names = ncbi.get_taxid_translator(lineage)
        for tid in lineage:
            if ranks.get(tid, "").lower() == "subphylum":
                return names[tid]
        return "NA"
    except Exception:
        return "NA"

df["subphylum"] = df.apply(
    lambda row: get_subphylum(row["Taxid"]) if str(row["subphylum"]).strip().upper() == "NA" else row["subphylum"],
    axis=1
)

df.to_csv(output_file, sep="\t", index=False, na_rep="NA")
