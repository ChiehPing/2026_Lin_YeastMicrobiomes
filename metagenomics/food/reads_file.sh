#!/bin/bash

set -euo pipefail
shopt -s nullglob

if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <cartella_logs> <file_output>"
    exit 1
fi

logs_dir="$1"
output="$2"

printf 'ID\ttotal\tclassified\tunclassified\n' > "$output"

log_files=("$logs_dir"/*.log)

if [ ${#log_files[@]} -eq 0 ]; then
    echo "No .log file found in $logs_dir."
    exit 0
fi

for file in "${log_files[@]}"; do
    id=$(basename "$file" .log)

    if [[ ! -s "$file" ]]; then
        printf '%s\tNA\tNA\tNA\n' "$id" >> "$output"
        continue
    fi

    total=$(awk '/sequences .* processed/ {print $1; exit}' "$file")
    classified=$(awk '/sequences classified/ {print $1; exit}' "$file")
    unclassified=$(awk '/sequences unclassified/ {print $1; exit}' "$file")

    total=${total:-NA}
    classified=${classified:-NA}
    unclassified=${unclassified:-NA}

    printf '%s\t%s\t%s\t%s\n' "$id" "$total" "$classified" "$unclassified" >> "$output"
done

echo "File created: $output"
