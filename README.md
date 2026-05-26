# Yeast Species Checker — README

---

## Overview

This script automates querying the [The Yeast Trust Database](https://theyeasts.org/species-search) using Selenium. Given a list of fungal taxa names, it searches each one and determines whether it is a confirmed yeast species, a non-yeast, or requires manual review.

---

## Requirements

### Python packages

Install all dependencies via pip:

```bash
pip install selenium pandas
```

or via conda
```bash
conda install -c conda-forge selenium pandas
```

---

## Input File

A **CSV file** with a column named `taxa` containing the fungal taxa names to search.

**Example (`input_file.txt`):**

```
taxa
Saccharomyces cerevisiae
Candida albicans
Aspergillus niger
```

> Despite the `.txt` extension, the file must be **comma-delimited** (CSV format) or one column only.

---

## Configuration

Edit the two path variables near the top of the script before running:

```python
#line23
inputfile  = r'D:\path\to\your\input_file.txt'
#line24
outputfile = r'D:\path\to\your\output_file.txt'
```

To control how often a checkpoint is saved during the run:

```python
AUTOSAVE_EVERY = 10  # Save every 10 taxa (set to 0 to disable)
```

---

## Output File

A **CSV file** with the following columns:

| Column | Description |
|---|---|
| `taxa` | The original taxon name from the input |
| `result` | The matched or top result returned by the database |
| `result num` | Total number of result entries found on the page |
| `isyeast` | Classification label (see below) |

### `isyeast` label key

| Value | Meaning |
|---|---|
| `Y` | Confirmed yeast — the exact taxon name was found in the database results |
| `tbc` | To be confirmed — results were returned, but the exact name was not among them |
| `N` | Not a yeast — no results found, or a timeout/error occurred |

---

## How It Works

1. Prompts whether to run in headless mode (browser hidden) or visible mode. Suggest to enter 'n' to better track the running status.
2. Loads the input file and prints an estimated completion time (7 sec approx per taxa).
3. Opens Chrome and navigates to the TheYeasts.org species search page. (default: max 15 sec. This may be changed at line 82).
4. For each taxon in the input list:
   - Types the taxon name into the search box and submits.
   - Waits for the results table to load. (default: max 15 sec. This may be changed at line 91).
   - Extracts all species names returned by the search.
   - Checks whether the queried taxon is an exact match in the results.
   - Records the outcome with a progress counter `[i/n]`.
   - Saves a checkpoint to the output file every `AUTOSAVE_EVERY` taxa.
5. On normal finish, Ctrl+C, or any crash — saves all collected results before exiting.
6. Prints the total runtime summary.

---

## Headless Mode

At startup, the script asks:

```
Run in headless mode? (browser window hidden) [y/n]:
```

| Choice | Behaviour |
|---|---|
| `y` | Chrome runs invisibly in the background — useful for unattended runs |
| `n` | Browser window opens visibly (for better tracking) |

> Headless mode uses `--headless=new` (requires Chrome ≥ 112) and sets a 1920×1080 virtual window so the page renders correctly.

---

## Runtime Estimates

After loading the input file, the script prints:

```
[INFO] There are 42 taxa in the file, which will take approximately 0:04:54 to complete.
```

The estimate assumes **7 seconds per taxon** (5 s render buffer + ~2 s overhead). However, it'll depends on your connection and website loading.

At the end of the run, the actual elapsed time is printed:

```
[DONE] Finished processing 42 taxa.
[DONE] Total runtime: 0:05:12
[DONE] Results saved to: D:\...\output_file.txt
```

---

## Error Handling

The script handles:

- **TimeoutException** — page or element did not load within the wait period; logged as `isyeast: N` with result `Timeout`
- **NoSuchElementException** — expected element not found on page; logged as `isyeast: N` with result `Not found`
- **General exceptions** — any other error is caught and the error message is stored in the `result` column

---

## Interrupt-Safe Saving

The script is designed to never lose collected data:

- **Ctrl+C / KeyboardInterrupt** — caught explicitly; triggers an immediate save before exiting.
- **`try/finally` block** — wraps the entire loop, so even unexpected crashes save whatever has been collected.
- **Periodic checkpoints** — every `AUTOSAVE_EVERY` taxa (default: 10), the output file is overwritten with the latest results. Adjust in Settings at the top of the script, or set to `0` to disable.

> Note: closing the browser window manually mid-run does **not** send a KeyboardInterrupt on all systems. The `finally` block will still attempt to save, but if Python itself is killed (e.g. via Task Manager), in-memory results may be lost. The periodic checkpoint is the best protection against this case.

---

## Usage Notes

- If running in visible mode, do not close, enter or scroll the browser window manually during the run.
- A `time.sleep(5)` buffer is included after each search to allow the JavaScript table to fully render. Adjust this at line 96 if you experience missed results on a slower connection.
- The script processes taxa **sequentially**; runtime scales linearly with the number of input taxa.

---

## Example Run

```bash
python yeast_taxa_checker_v5.py
```

Console output during a run:

```
============================================================
Run in headless mode? (browser window hidden) [y/n]: y
[INFO] Headless mode enabled — browser will run in the background.
============================================================

[INFO] There are 42 taxa in the file, which will take approximately 0:04:54 to complete.
[INFO] Auto-save enabled — checkpoint saved every 10 taxa.
============================================================
[1/42] Searching for Saccharomyces cerevisiae...
  Submitted search for Saccharomyces cerevisiae
  Results section detected for Saccharomyces cerevisiae
  Found 4 species links for Saccharomyces cerevisiae
[2/42] Searching for Aspergillus niger...
  ...
[10/42] Searching for Rhodotorula mucilaginosa...
  ...
  [SAVE] Checkpoint [10/42] — 10 records written to ...\output_file.txt
  ...

--- user presses Ctrl+C at taxon 25 ---

[INTERRUPTED] Script stopped early — saving collected results...
  [SAVE] Final — 25 records written to ...\output_file.txt

============================================================
[DONE] Processed 25 of 42 taxa.
[DONE] Total runtime: 0:02:57
[DONE] Results saved to: D:\...\output_file.txt
============================================================
```

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---|---|---|
| `WebDriverException` on launch | ChromeDriver version mismatch | Update ChromeDriver to match your Chrome version |
| `TimeoutException` for every taxon | Slow internet or site layout changed | Increase `WebDriverWait` timeout values |
| All taxa return `tbc` | Search logic mismatch | Verify that the `taxa` column name in the input file is spelled correctly |
| Headless mode fails to find elements | Chrome version below 112 | Replace `--headless=new` with `--headless` in the Chrome options in line 62 |
