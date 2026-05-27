import os
import sys
import re
from ete4 import NCBITaxa

def create_kraken_matrix_with_subphylum(input_folder, mapping_file, output_file):
    mapping = []
    sample_names = []

    print(f"Reading mapping file: {mapping_file}")
    with open(mapping_file, 'r') as f:
        header = f.readline()
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) < 2:
                parts = line.strip().split()

            if len(parts) >= 2:
                id_file = parts[0]
                sample_name = parts[1]
                mapping.append((id_file, sample_name))
                sample_names.append(sample_name)

    species_data = {}
    target_ranks = {'K', 'P', 'C', 'O', 'F', 'G', 'S'}

    print(f"Reading {len(mapping)} samples...")
    for file_id, sample_name in mapping:
        bracken_path = os.path.join(input_folder, f"{file_id}.bracken.S.report")
        kraken_path = os.path.join(input_folder, f"{file_id}.k2.report")

        target_file = None
        if os.path.exists(bracken_path):
            target_file = bracken_path
        elif os.path.exists(kraken_path):
            target_file = kraken_path
        else:
            print(f"Warning: No report for ID {file_id}.")
            continue

        stack = []
        with open(target_file, 'r') as f:
            for line in f:
                if not line.strip(): continue

                parts = line.rstrip('\n').split('\t')

                if len(parts) < 6:
                    match = re.match(r'^\s*([\d\.]+)\s+(\d+)\s+(\d+)\s+([A-Za-z0-9_]+)\s+(\d+)\s+(.*)$', line.rstrip('\n'))
                    if match:
                        parts = match.groups()
                    else:
                        continue

                reads_all = float(parts[1])
                rank = parts[3]
                taxid = parts[4]
                name_field = parts[5]

                indent = len(name_field) - len(name_field.lstrip(' '))
                clean_name = name_field.strip()

                while stack and stack[-1][0] >= indent:
                    stack.pop()

                stack.append((indent, rank, clean_name))

                if rank == 'S':
                    tax_dict = {r: '' for r in target_ranks}
                    for lvl_ind, lvl_rank, lvl_name in stack:
                        if lvl_rank in target_ranks:
                            tax_dict[lvl_rank] = lvl_name

                    if taxid not in species_data:
                        species_data[taxid] = {
                            'taxonomy': tax_dict,
                            'abundances': {}
                        }

                    species_data[taxid]['abundances'][sample_name] = reads_all

    print("\nInitialization NCBI database ETE4 ...")
    ncbi = NCBITaxa()

    def get_subphylum_from_taxid(taxid):
        try:
            if not taxid or taxid in ["", "NA"]:
                return "NA"
            tid = int(float(taxid))
            lineage = ncbi.get_lineage(tid)
            ranks = ncbi.get_rank(lineage)
            names = ncbi.get_taxid_translator(lineage)
            for t in lineage:
                if ranks.get(t) == "subphylum":
                    return names[t]
            return "NA"
        except Exception as e:
            return "NA"

    subphylum_cache = {}
    for taxid in species_data.keys():
        subphylum_cache[taxid] = get_subphylum_from_taxid(taxid)

    with open(output_file, 'w') as f:
        headers = ['taxid'] + sample_names + ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'subphylum']
        f.write('\t'.join(headers) + '\n')

        for taxid, data in species_data.items():
            row = [taxid]

            for sample in sample_names:
                row.append(str(data['abundances'].get(sample, 0.0)))

            tax = data['taxonomy']
            row.extend([
                tax['K'],
                tax['P'],
                tax['C'],
                tax['O'],
                tax['F'],
                tax['G'],
                tax['S'],
                subphylum_cache[taxid]
            ])

            f.write('\t'.join(row) + '\n')

    print("End.")


if __name__ == '__main__':
    FOLDER_REPORT = "results"
    LIST_HITS     = "reads_earth_microbiomes_k2_B.tsv"
    OUTPUT_TSV    = "kraken_absolute_isyeast_subphylum.tsv"

    create_kraken_matrix_with_subphylum(FOLDER_REPORT, LIST_HITS, OUTPUT_TSV)
