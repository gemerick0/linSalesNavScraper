from asyncio import subprocess
from selenium import webdriver
import seleniumwire.undetected_chromedriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from general_lk_utils import enter_ids_on_lk_signin, get_lk_credentials, get_listP, get_lk_url_from_sales_lk_url
import time
import pyperclip
import re
from selenium.webdriver.common.by import By
from random import randint
import random
import requests
import json
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures
import os
from pandas.errors import DataError
import pandas as pd

SCRAPEOPS_API_KEY = 'b7c14682-a15e-48d9-a133-6b91cc022d6d'


def get_user_agent_list():
    response = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=' + SCRAPEOPS_API_KEY)
    json_response = response.json()
    return json_response.get('result', [])


def get_random_user_agent(user_agent_list):
    random_index = randint(0, len(user_agent_list) - 1)
    return user_agent_list[random_index]


## Retrieve User-Agent List From ScrapeOps
user_agent_list = get_user_agent_list()

cookies = get_listP('./cookies.json')
cookies = str(cookies)
baserow_api_token = "wMWVhs8wuDQBLauICWYxXeN1LCE6eUwI"
leads_table_id = "292983"
baserow_url = "https://api.baserow.io/api/database/rows/table/"
headers = {"Authorization": f"Token {baserow_api_token}", "Content-Type": "application/json"}
emailNotEmptyFilters = {"filter_type": "AND", "filters": [{"type": "not_empty", "field": 2097243, "value": ""}],
                        "groups": []}
# To input
total_pages = 1024  # adjust this every time you add more leads
start_page = 800  # this is added to skip the first pages for speed. Put to 0 if more complex searches are needed

# 3. Get all leads data
audience_id = int(input("Enter the audience id: "))
print("Step 3: Getting all leads data...")


def fetch_page_baserow_table_data(url, headers, table_id, page, page_size=100, attempt=1):
    """Fetch a single page of data from the Baserow table with retry on 429."""
    request_url = f"{url}{table_id}/?page={page}&size={page_size}"
    response = requests.get(request_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('results', [])
    elif response.status_code == 429:
        if attempt <= 5:  # Max retry attempts
            sleep_time = attempt * 2  # Exponential backoff
            print(f"Rate limit hit, retrying page {page} after {sleep_time} seconds...")
            time.sleep(sleep_time)
            return fetch_page_baserow_table_data(url, headers, table_id, page, page_size, attempt + 1)
        else:
            print(f"Failed to fetch page {page} after {attempt} attempts.")
            return []
    else:
        print(f"Error fetching page {page}: {response.status_code}")
        return []


def fetch_all_baserow_table_data_concurrently(url, headers, table_id, total_pages, start_page, max_workers=10):
    """Fetch all rows from the Baserow table using concurrent requests with rate limiting, starting from a specified page."""
    all_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Preparing a list of page numbers to fetch, starting from 'start_page'
        page_numbers = list(range(start_page, total_pages + 1))
        # Create a future to page mapping
        futures = [executor.submit(fetch_page_baserow_table_data, url, headers, table_id, page) for page in
                   page_numbers]
        for future in concurrent.futures.as_completed(futures):
            data = future.result()
            all_data.extend(data)
    print("Step 3 Completed: All leads data fetched.")

    return all_data


listOfDicts = fetch_all_baserow_table_data_concurrently(baserow_url, headers, leads_table_id, total_pages, start_page)
filtered_data = [row for row in listOfDicts if any(d.get('id') == audience_id for d in row.get('field_2109937', []))]
# 4. Convert the data to a pandas DataFrame
dfData = pd.json_normalize(filtered_data)
# Transform dfData into an xlsx file
emptyEmails = dfData.query('field_2097243.isna() & field_2097278 == "True"')
emptyEmails.reset_index(inplace=True)
emptyEmails = emptyEmails.loc[500:1000]
pLink = emptyEmails['field_2097250'].tolist()
print(pLink)
print(emptyEmails)
print("Step 4: Data converted to pandas DataFrame.")


def gInt01_05():
    return random.uniform(0.3, 0.8)


def gInt05_1():
    return random.uniform(0.7, 1.2)


def gInt1_3():
    return random.uniform(1, 3)


def gInt3_6():
    return random.uniform(3, 6)


def gInt6_11():
    return random.uniform(6, 11)


def choose_random_action(driver):
    action = random.choice(["scroll_up", "scroll_down", "click_link", "wait", "go_link"])
    if action == "scroll_up":
        start_num = gInt6_11() * 10
        end_num = gInt3_6() * 100
        pixels = round(random.uniform(start_num, end_num))
        driver.execute_script(f"window.scrollBy(0, -{pixels})")
        time_to_wait = gInt3_6()
        time.sleep(time_to_wait)
    elif action == "scroll_down":
        start_num = gInt6_11() * 10
        end_num = gInt3_6() * 100
        pixels = round(random.uniform(start_num, end_num))
        driver.execute_script(f"window.scrollBy(0, {pixels})")
        time_to_wait = gInt3_6()
        time.sleep(time_to_wait)
    elif action == "go_link":
        try:
            lisLinks = driver.find_elements(By.TAG_NAME, "a")
            link = lisLinks[random.randint(0, len(lisLinks) - 1)]
            driver.get(link.get_attribute("href"))
        except:
            time_to_wait = gInt3_6()
            time.sleep(time_to_wait)
    elif action == "click_link":
        try:
            lisButtons = driver.find_elements(By.TAG_NAME, "button")
            btn = lisButtons[random.randint(0, len(lisButtons) - 1)]
            btn.click()
        except:
            time_to_wait = gInt3_6()
            time.sleep(time_to_wait)
    else:
        time_to_wait = gInt3_6()
        time.sleep(time_to_wait)


csv_file_path = "./Google-ads-agency-6.csv"
column_name = "Links"


def enter_linkedIn_profiles_from_baserow(pLink):
    lk_credentials_path = "./lk_credentials.json"
    lk_credentials = get_lk_credentials(lk_credentials_path)

    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--excludeSwitches=enable-automation")
    #chrome_options.add_argument(f"--user-agent={get_random_user_agent(user_agent_list)}")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    options = {
        'proxy': {
            'http': 'http://lQCYsxPldLqGW2M:4rxuqrH5gcaLvAT@host:207.135.201.116:42510'
        }
    }
    chrome_options.accept_insecure_certs = True
    chrome_options.add_argument(r'--load-extension=C:\Users\gabee\anaconda3\envs\linkedinSalesNavScraper\Kaspr')
    driver = uc.Chrome(seleniumwire_options=options, options=chrome_options, driver_executable_path='./chromedriver.exe')
    driver.maximize_window()
    driver.get("https://www.linkedin.com/login/")
    time.sleep(3)
    driver.add_cookie({"name": "li_at", "value": "AQEDATkqLvsEp_AvAAABj5lUdi4AAAGPvWD6Lk0ADFg9gNn35xSO_2nGfyFaw2vGgcngJk2DsHBKLaPUBUHFpP_K-wJT3Q66aCYCvPhfbsY0lBvqGaUtxDCQEHXqKJ7XqJQ-knUa6XEt7pZKMJM7fDZV"})
    """enter_ids_on_lk_signin(driver, lk_credentials['TESmail'], lk_credentials['TESpassword'])
    if "checkpoint/challenge" in driver.current_url:
        print(
            "It looks like you need to complete a double factor authentification. Please do so and press enter when you are done."
        )
        input()"""
    time.sleep(gInt3_6())
    driver.get("https://app.kaspr.io/signin?utm_source=Widget&utm_medium=Connect")
    time.sleep(4)
    kUser = driver.find_element(By.XPATH, "//input[@type='text']")
    time.sleep(0.3)
    kUser.send_keys(lk_credentials["kgEmail"])
    time.sleep(0.2)
    kBtn = driver.find_element(By.TAG_NAME, "button")
    time.sleep(0.4)
    kBtn.click()
    time.sleep(2)
    kPword = driver.find_element(By.XPATH, "//input[@type='password']")
    kPword.send_keys(lk_credentials["kgPassword"])
    kBtn = driver.find_element(By.TAG_NAME, "button")
    time.sleep(0.3)
    kBtn.click()
    time.sleep(3)
    lastRow = 0
    for i in range(10):
        for index, row in emptyEmails[lastRow:lastRow+50].iterrows():
            profile_url = row['field_2097250']
            driver.get(profile_url)
            time.sleep(3)
            if "/login" in driver.current_url:
                print(
                    "It looks like you need to complete a double factor authentification. Please do so and press enter when you are done."
                )
                input()
            try:
                kasprBtn = driver.find_element(By.XPATH, "//div[@id='KasprPluginBtn']/button")
                kasprBtn.click()
                time.sleep(5)
            except:
                pass
            try:
                kasprCntBtn = driver.find_element(By.XPATH, "//button[normalize-space()='Reveal contact details']")
                time.sleep(1)
                kasprCntBtn.click()
            except:
                pass
            try:
                time.sleep(2)
                emailW = driver.find_element(By.XPATH, "//span[@class='star']//span[@class='to-clipboard']")
                email = emailW.text
            except:
                email = ""
            print("Email: " + email)

            # Update email immediately in Baserow
            row_id = row['id']
            response = requests.patch(
                f"https://api.baserow.io/api/database/rows/table/292983/{row_id}/",
                headers={
                    "Authorization": f"Token {baserow_api_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "field_2097243": email
                }
            )
            if response.status_code == 200:
                print(f"Successfully updated email for row {row_id}")
            else:
                print(f"Failed to update email for row {row_id}: {response.status_code}")
            choose_random_action(driver)
        lastRow = lastRow + 50
        time.sleep(600)
    driver.quit()
    return


enter_linkedIn_profiles_from_baserow(pLink)