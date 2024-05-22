import pandas as pd

from general_lk_utils import (
    get_lk_credentials,
    get_listP,
    enter_ids_on_lk_signin
)
import csv
from time import sleep
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
cList = get_listP("./links.json")["links"][1]["linkCompanies"]
fields = ['Overview', 'Industry', 'Specialties']
sel = Selector(text=driver.page_source)
filEname = "./companiesScraped.csv"
df = pd.DataFrame(columns=fields)
# What we need from the profile


for companies in cList:
    if companies is not None:
        driver.get(companies + '/about')
        sel = Selector(text=driver.page_source)
        sleep(2)
        driver.execute_script("window.scrollBy(0, 300)")
        sleep(0.2)
        try:
            overview = driver.find_element(By.XPATH, "//h2[normalize-space()='Overview']/following-sibling::p[1]")
        except:
            pass
        if overview:
            overview = overview.text
        else:
            overview = 'No Result'
        print(overview)
        driver.execute_script("window.scrollBy(0, 300)")
        sleep(0.2)
        try:
            industry = driver.find_element(By.XPATH,
            "//dt[normalize-space()='Industry']/following-sibling::dd[1]")
        except:
            pass
        if industry:
            industry = industry.text
        else:
            industry = 'No Result'
        print(industry)

        try:
            specialties = driver.find_element(By.XPATH,
            "//dt[normalize-space()='Specialties']/following-sibling::dd")
        except:
            pass
        if specialties:
            specialties = specialties.text
        else:
            specialties = 'No Result'
        print(specialties)
        dict = {"Overview": overview, "Industry": industry, "Specialties": specialties}
        df = pd.concat([df, pd.DataFrame(dict)])
        specialties = None
        overview = None
        industry = None
