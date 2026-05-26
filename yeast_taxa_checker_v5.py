# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 14:39:50 2025
Updated: headless mode, estimated runtime, total runtime summary,
         auto-save on interrupt / periodic checkpoint save
 
@author: PING
"""
 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import timedelta
import pandas as pd
import time
 
# ── Paths ──────────────────────────────────────────────────────────────────────
## Change the input and output path here!!
inputfile  = r'D:\path\to\your\input_file.txt'
outputfile = r'D:\path\to\your\output_file.txt'
 
# ── Settings ───────────────────────────────────────────────────────────────────
SECONDS_PER_TAXA  = 7   # Estimated seconds per taxon (adjust if needed)
AUTOSAVE_EVERY    = 10  # Save a checkpoint every N taxa (0 to disable)
 
# ── Headless mode prompt ───────────────────────────────────────────────────────
print("=" * 60)
headless_input = input("Run in headless mode? (browser window hidden) [y/n]: ").strip().lower()
headless = headless_input == 'y'
if headless:
    print("[INFO] Headless mode enabled — browser will run in the background.")
else:
    print("[INFO] Visible mode — browser window will open.")
print("=" * 60)
 
# ── Load input & estimate runtime ─────────────────────────────────────────────
ITS1_ITS2_genus = pd.read_csv(inputfile, sep=',')
search_query    = ITS1_ITS2_genus['taxa'].values.tolist()
n_taxa          = len(search_query)
 
eta = timedelta(seconds=n_taxa * SECONDS_PER_TAXA)
print(f"\n[INFO] There are {n_taxa} taxa in the file, which will take approximately {eta} to complete.")
if AUTOSAVE_EVERY:
    print(f"[INFO] Auto-save enabled — checkpoint saved every {AUTOSAVE_EVERY} taxa.")
print("=" * 60)
 
# ── Helper: save whatever has been collected so far ───────────────────────────
def save_progress(records, path, label=""):
    if records:
        pd.DataFrame(records).to_csv(path, index=False)
        print(f"  [SAVE] {label}{len(records)} records written to {path}")
    else:
        print("  [SAVE] Nothing to save yet.")
 
# ── Launch browser ─────────────────────────────────────────────────────────────
chrome_options = Options()
if headless:
    chrome_options.add_argument("--headless=new")   # Chrome ≥ 112
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
 
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(0.5)
driver.get("https://theyeasts.org/species-search")
time.sleep(3)
 
# ── Main search loop ───────────────────────────────────────────────────────────
req        = []
start_time = time.time()
 
try:
    for i, taxa in enumerate(search_query, start=1):
        elements = []   # reset so exception handlers don't reference a stale value
        try:
            print(f"[{i}/{n_taxa}] Searching for {taxa}...")
            search_box = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.ID, "mat-chip-list-input-0"))
            )
            search_box.clear()
            search_box.send_keys(taxa)
            search_box.send_keys(Keys.ENTER)
            print(f"  Submitted search for {taxa}")
 
            # Wait for results to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Search result')] | //table"))
            )
            print(f"  Results section detected for {taxa}")
            time.sleep(5)  # Extra buffer for table rendering
 
            elements = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.mat-tooltip-trigger.text-overflow"))
            )
            print(f"  Found {len(elements)} species links for {taxa}")
 
            taxa_results = []
            for element in elements[1:]:
                try:
                    text = element.text.strip()
                    if not text:
                        text = element.get_attribute("innerText").strip()
                    if text:
                        taxa_results.append(text)
                    else:
                        print(f"  Empty text in element for {taxa}")
                except Exception as e:
                    print(f"  Error extracting text for {taxa}: {str(e)}")
 
            if taxa_results:
                if taxa in taxa_results:
                    req.append({'taxa': taxa, 'result': taxa, 'result num': len(elements), 'isyeast': 'Y'})
                else:
                    req.append({'taxa': taxa, 'result': taxa_results[0], 'result num': len(elements), 'isyeast': 'tbc'})
            else:
                req.append({'taxa': taxa, 'result': 'No results found', 'result num': len(elements), 'isyeast': 'N'})
                print(f"  No results for {taxa}")
 
        except TimeoutException as e:
            print(f"  Timeout for {taxa}: {str(e)}")
            req.append({'taxa': taxa, 'result': 'Timeout', 'result num': len(elements), 'isyeast': 'N'})
            try:
                alt_elements = driver.find_elements(By.CSS_SELECTOR, "div.mat-tooltip-trigger")
                print(f"  Alternative mat-tooltip-trigger elements found: {len(alt_elements)}")
                if alt_elements:
                    print(f"  Sample text: {alt_elements[0].text.strip()}")
            except:
                print("  No alternative elements found")
            print(f"  Page source (first 500 chars) for {taxa}: {driver.page_source[:500]}")
 
        except NoSuchElementException as e:
            print(f"  Element not found for {taxa}: {str(e)}")
            req.append({'taxa': taxa, 'result': 'Not found', 'result num': len(elements), 'isyeast': 'N'})
 
        except Exception as e:
            print(f"  Error for {taxa}: {str(e)}")
            req.append({'taxa': taxa, 'result': f'Error: {str(e)}', 'result num': len(elements), 'isyeast': 'N'})
 
        finally:
            time.sleep(1)
 
        # ── Periodic checkpoint save ───────────────────────────────────────────
        if AUTOSAVE_EVERY and i % AUTOSAVE_EVERY == 0:
            save_progress(req, outputfile, label=f"Checkpoint [{i}/{n_taxa}] — ")
 
except KeyboardInterrupt:
    # Ctrl+C or manual window close triggers this
    print("\n[INTERRUPTED] Script stopped early — saving collected results...")
 
finally:
    # Always runs: normal finish, Ctrl+C, or crash
    save_progress(req, outputfile, label="Final — ")
    try:
        driver.quit()
    except Exception:
        pass  # Browser may already be closed
 
# ── Total runtime summary ──────────────────────────────────────────────────────
elapsed = timedelta(seconds=int(time.time() - start_time))
 
print("\n" + "=" * 60)
print(f"[DONE] Processed {len(req)} of {n_taxa} taxa.")
print(f"[DONE] Total runtime: {elapsed}")
print(f"[DONE] Results saved to: {outputfile}")
print("=" * 60)
