

from general_lk_utils import (
    get_lk_credentials,
    get_listP,
    enter_ids_on_lk_signin
)
import csv
import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from parsel import Selector
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

LK_CREDENTIALS_PATH = "./lk_credentials.json"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
lk_credentials = get_lk_credentials(LK_CREDENTIALS_PATH)
email = lk_credentials['email']
pword = lk_credentials['password']
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get('https://www.linkedin.com/login')
sleep(2)
enter_ids_on_lk_signin(driver, lk_credentials['email'], lk_credentials['password'])
if "checkpoint/challenge" in driver.current_url:
    print(
        "It looks like you need to complete a double factor authentification. Please do so and press enter when you are done."
    )
    input()
pList = get_listP("./links.json")["links"][0]["linkProfiles"]
fields = ['Headline', 'Summary', 'JobDescription']
sel = Selector(text=driver.page_source)
filEname = "./profilesScraped.csv"
# What we need from the profile


with open(filEname, 'w', encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(fields)
    for profiles in pList:
        driver.get(profiles)
        sleep(3)
        headline = driver.find_element(By.XPATH, '//*[starts-with(@class, "text-body-medium break-words")]')
        if headline:
            headline = headline.text
        else:
            headline = 'No Result'
        driver.execute_script("window.scrollBy(0, 500)")
        try:
            seeSummary = driver.find_element(By.XPATH, "//div[contains(@class,'display-flex ph5 pv3')]")
        except:
            summary = 'No Result'
        else:
            """try:
                seeSummBtn = seeSummary.find_element(By.TAG_NAME, "button")
                seeSummBtn.click()
            except:
                pass
            time.sleep(0.5)"""
            #try:
            summary = driver.find_element(By.XPATH, '//div[@class = "display-flex ph5 pv3"]//span[@aria-hidden = "true"]')
            summary = summary.text
            """except:
                pass
            if summary:
                summary = summary.text
            else:
                summary = 'No Result'"""
        print("Headline: " + headline)
        print("Summary: " + summary)
        for i in range(10):
            try:
                jobPart = driver.find_element(By.XPATH, "(//section[@data-view-name='profile-card']//div[@data-view-name='profile-component-entity']//li//ul//li//button)[1]")
                jobPart = jobPart.find_element(By.XPATH, "./ancestor::div[1]")
                jobDescription = jobPart.find_element(By.XPATH, "./span[@aria-hidden='true']")
                jobPart = jobPart.text
                break
            except:
                driver.execute_script("window.scrollBy(0, 400)")
                time.sleep(0.1)
        if not jobPart:
            jobPart = "No Result"
        print("jobDescription:"+jobPart)
        writer.writerow([headline, summary, jobPart])
        jobPart = None
