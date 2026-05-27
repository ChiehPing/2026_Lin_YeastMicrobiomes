#!/bin/bash

set -euo pipefail
shopt -s nullglob

logs_dir="$1"
map_file="$2"
output="$3"

declare -A id2sample

while IFS= read -r line; do
  [[ -z "${line//[[:space:]]/}" ]] && continue
  [[ "${line#"${line%%[![:space:]]*}"}" == sample_name* ]] && continue

  sample_name=$(awk '{print $1}' <<<"$line")
  run_field=$(awk '{print $2}' <<<"$line")

  run_field=$(echo "$run_field" | tr -d '[:space:]')

  IFS=',' read -ra ids <<< "$run_field"
  for id in "${ids[@]}"; do
    id="${id//[[:space:]]/}"
    [[ -z "$id" ]] && continue

    if [[ -n "${id2sample[$id]:-}" && "${id2sample[$id]}" != "$sample_name" ]]; then
      printf 'Warning: accession %s already mapped in %s (nuovo: %s). Takes the first.\n' \
        "$id" "${id2sample[$id]}" "$sample_name" >&2
      continue
    fi
    id2sample["$id"]="$sample_name"
  done
done < <(tail -n +2 "$map_file")

printf 'ID\tsample_name\ttotal\tclassified\tunclassified\n' > "$output"

for file in "$logs_dir"/*.log; do
  [ -e "$file" ] || continue

  id=$(basename "$file" .log)

  total=$(grep -oE '([0-9]+) sequences' "$file" 2>/dev/null | head -n1 | grep -oE '[0-9]+' || true)
  classified=$(grep -oE '([0-9]+) sequences classified' "$file" 2>/dev/null | head -n1 | grep -oE '[0-9]+' || true)
  unclassified=$(grep -oE '([0-9]+) sequences unclassified' "$file" 2>/dev/null | head -n1 | grep -oE '[0-9]+' || true)

  total=${total:-NA}
  classified=${classified:-NA}
  unclassified=${unclassified:-NA}

  sample_name=${id2sample[$id]:-NA}

  printf '%s\t%s\t%s\t%s\t%s\n' "$id" "$sample_name" "$total" "$classified" "$unclassified" >> "$output"
done

echo "File created: $output"
