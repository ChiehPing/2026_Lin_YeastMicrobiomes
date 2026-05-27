#!/usr/bin/env bash

dir_id="$1"
categories_file="$2"
file_output="$3"
tmp_file=$(mktemp)

echo -e "File_ID\treads_length\tName\tRank\tLineage\tTaxid\tmacrocategory\tcategory\ttype\tsubtype\thighest_taxa\tgenus\tisyeast\tsubphylum" > "$tmp_file"

awk -F'\t' 'NR>1 {
    ids[$10]=$3"\t"$4"\t"$5"\t"$6;
    ids[$11]=$3"\t"$4"\t"$5"\t"$6;
    ids[$12]=$3"\t"$4"\t"$5"\t"$6;
    ids[$13]=$3"\t"$4"\t"$5"\t"$6;
    ids[$14]=$3"\t"$4"\t"$5"\t"$6;
} END {
    for (i in ids) print i"\t"ids[i];
}' "$categories_file" > id_to_categories.tsv

find "$dir_id" -type f -name "*_filtered_hits_table.txt" | while IFS= read -r file; do
    filename=$(basename "$file")
    file_id="${filename%%_filtered_hits_table.txt}"

    cat_line=$(grep -m1 -w "$file_id" /home/alberto/analysis_EukDetect/food_metagenomes_2500_study/other/tmp/id_to_categories.tsv || echo -e "${file_id}\tNA\tNA\tNA\tNA")
    macrocategory=$(echo "$cat_line" | cut -f2)
    category=$(echo "$cat_line" | cut -f3)
    type=$(echo "$cat_line" | cut -f4)
    subtype=$(echo "$cat_line" | cut -f5)

    if [ ! -s "$file" ]; then
        echo -e "${file_id}\tNA\tNA\tNA\tNA\tNA\t${macrocategory}\t${category}\t${type}\t${subtype}\tNA\tNA\tNA\tNA" >> "$tmp_file"
        continue
    fi

    dos2unix -q "$file" 2>/dev/null || true
    first_line=$(head -n1 "$file" | tr -d '\r')
    if echo "$first_line" | grep -qi "empty read count file"; then
        echo -e "${file_id}\tNA\tNA\tNA\tNA\tNA\t${macrocategory}\t${category}\t${type}\t${subtype}\tNA\tNA\tNA\tNA" >> "$tmp_file"
        continue
    fi

    n_lines=$(wc -l < "$file")
    if [ "$n_lines" -le 1 ]; then
        echo -e "${file_id}\tNA\tNA\tNA\tNA\tNA\t${macrocategory}\t${category}\t${type}\t${subtype}\tNA\tNA\tNA\tNA" >> "$tmp_file"
        continue
    fi

    awk -v id="$file_id" -v m="$macrocategory" -v c="$category" -v t="$type" -v s="$subtype" 'BEGIN{FS=OFS="\t"}
        NR>1 && NF>=4 {
            name=$1; rank=$2; lineage=$3; taxid=$4;
            if (name == "" && rank == "" && lineage == "" && taxid == "") next;
            print id, "NA", name, rank, lineage, taxid, m, c, t, s, "NA", "NA", "NA", "NA";
        }' "$file" >> "$tmp_file"

    if [ "$(tail -n1 "$tmp_file" | cut -f1)" != "$file_id" ]; then
        echo -e "${file_id}\tNA\tNA\tNA\tNA\tNA\t${macrocategory}\t${category}\t${type}\t${subtype}\tNA\tNA\tNA\tNA" >> "$tmp_file"
    fi
done

awk -F'\t' 'NR==1 {print; next} {
    if ($5 == "NA" || $5 == "") {print; next}
    if ($4 == "species") {print}
}' "$tmp_file" > "$file_output"

rm -f "$tmp_file"
rm -f id_to_categories.tsv
