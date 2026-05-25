# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 14:39:50 2025

@author: PING
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 24 16:20:23 2025

@author: PING
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

##Change the input and output path here!!
inputfile=r'D:\B303\PlantMycobiome\___manuscript\Metabarcoding\yeastlisted_uniq.txt'
outputfile=r'D:\B303\PlantMycobiome\___manuscript\Metabarcoding\yeastlisted_uniq_isyeast.txt'

driver = webdriver.Chrome()
driver.implicitly_wait(0.5)
# Open the website
driver.get("https://theyeasts.org/species-search")


# Wait for the page to load
time.sleep(3)
ITS1_ITS2_genus=pd.read_csv(inputfile, sep=',')

req=[]
search_query=ITS1_ITS2_genus['taxa'].values.tolist()
for taxa in search_query:
    try:
        # Locate and interact with the search box
        print(f"Searching for {taxa}...")
        search_box = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "mat-chip-list-input-0"))
        )
        search_box.clear()
        search_box.send_keys(taxa)
        search_box.send_keys(Keys.ENTER)
        print(f"Submitted search for {taxa}")

        # Wait for results to load (look for "Search result" text or table)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Search result')] | //table"))
        )
        print(f"Results section detected for {taxa}")
        time.sleep(5)  # Extra buffer for table rendering

        # Find all <a> elements with class containing "info"
        elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.mat-tooltip-trigger.text-overflow"))
        )
        print(f"Found {len(elements)} species links for {taxa}")

        taxa_results = []
        # if len(elements) >5:
        #     n=5
        # else:
        #     n=len(elements)
        for element in elements[1:len(elements)]:
            try:
                text = element.text.strip()
                if not text:
                    text = element.get_attribute("innerText").strip()
                if text:
                    taxa_results.append(text)
                else:
                    print(f"Empty text in element for {taxa}")
            except Exception as e:
                print(f"Error extracting text for {taxa}: {str(e)}")

        if taxa_results:
                if taxa in taxa_results:
                    req.append({'taxa': taxa, 'result': taxa,'result num':len(elements), 'isyeast': 'Y'})
                else:
                    req.append({'taxa': taxa, 'result': taxa_results[0],'result num':len(elements), 'isyeast': 'tbc'})
        else:
            req.append({'taxa': taxa, 'result': 'No results found','result num':len(elements), 'isyeast': 'N'})
            print(f"No results for {taxa}")

    except TimeoutException as e:
        print(f"Timeout for {taxa}: {str(e)}")
        req.append({'taxa': taxa, 'result': 'Timeout','result num':len(elements), 'isyeast': 'N'})
        # Debug: Check for similar elements
        try:
            alt_elements = driver.find_elements(By.CSS_SELECTOR, "div.mat-tooltip-trigger")
            print(f"Alternative mat-tooltip-trigger elements found: {len(alt_elements)}")
            if alt_elements:
                print(f"Sample text: {alt_elements[0].text.strip()}")
        except:
            print("No alternative elements found")
        print(f"Page source (first 500 chars) for {taxa}: {driver.page_source[:500]}")
    except NoSuchElementException as e:
        print(f"Element not found for {taxa}: {str(e)}")
        req.append({'taxa': taxa, 'result': 'Not found','result num':len(elements), 'isyeast': 'N'})
    except Exception as e:
        print(f"Error for {taxa}: {str(e)}")
        req.append({'taxa': taxa, 'result': f'Error: {str(e)}','result num':len(elements), 'isyeast': 'N'})
    finally:
        time.sleep(1)
df = pd.DataFrame(req)
df.to_csv(outputfile,index=False)

driver.quit()