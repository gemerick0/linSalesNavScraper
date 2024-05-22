"""
This is meant to be run as a CLI script.
It will scrap the search results of a LinkedIn Sales Navigator search.

Example usage:
python lksn_search_scraper.py --search-url "https://www.linkedin.com/sales/search/people?query=(spellCorrectionEnabled%3Atrue%2Ckeywords%3Ascraping)"
"""
import argparse
import os
import json
import subprocess
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from general_lk_utils import (
    remove_url_parameter,
    get_lk_credentials,
    enter_ids_on_lk_signin,
    get_lk_url_from_sales_lk_url,
    get_lk_company_url_from_sales_lk_url,
)

SCROLL_TO_BOTTOM_COMMAND = (
    "document.getElementById('search-results-container').scrollTop+=100000;"
)
LK_CREDENTIALS_PATH = "./lk_credentials.json"


def get_profile_link_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.flex.flex-wrap.align-items-center > div.artdeco-entity-lockup__title.ember-view > a"
    els = result_el.select(selector)
    link_to_profile = ""
    if len(els) > 0:
        link_to_profile = els[0]["href"]
    return {"link_to_profile": link_to_profile}


def get_name_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.flex.flex-wrap.align-items-center > div.artdeco-entity-lockup__title.ember-view > a > span"
    els = result_el.select(selector)
    name = ""
    if len(els) > 0:
        el_contents = els[0].contents
        if len(el_contents) > 0:
            name = el_contents[0].strip()
    return {"name": name}


def get_search_url(search_url_base, page=1):
    url = search_url_base + f"&page={page}"
    return url


def get_role_info_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.artdeco-entity-lockup__subtitle.ember-view.t-14 > span"
    els = result_el.select(selector)
    role_name = ""
    if len(els) > 0:
        el_contents = els[0].contents

        if len(el_contents) > 0:
            role_name = el_contents[0].strip()
    return {"role_name": role_name}


def get_location_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content > div.artdeco-entity-lockup__caption > span"
    els = result_el.select(selector)
    location = ""
    if len(els) > 0:
        el_contents = els[0].contents
        if len(el_contents) > 0:
            location = el_contents[0].strip()
    return {"location": location}


def get_company_info_from_result_el(result_el):
    selector = "div > div > div.flex.justify-space-between.full-width > div.flex.flex-column > div.mb3 > div > div.artdeco-entity-lockup__content.ember-view > div.artdeco-entity-lockup__subtitle.ember-view.t-14 > a"
    els = result_el.select(selector)
    link_to_company = ""
    company_name = ""
    if len(els) > 0:
        link_to_company = els[0]["href"]
        el_contents = els[0].contents
        if len(el_contents) > 0:
            company_name = el_contents[0].strip()
    return {"link_to_company": link_to_company, "company_name": company_name}


def get_info_from_result_el(result_el):
    r = []
    r.append(get_name_from_result_el(result_el))
    r.append(get_profile_link_from_result_el(result_el))
    r.append(get_location_from_result_el(result_el))
    r.append(get_role_info_from_result_el(result_el))
    r.append(get_company_info_from_result_el(result_el))

    info = {}

    for obj in r:
        for k in obj.keys():
            info[k] = obj[k]
    return info


def get_result_els(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    full_results_selector = "#search-results-container > div > ol > li"
    all_results_el = soup.select(full_results_selector)
    return all_results_el


def get_all_info_from_page_source(page_source):
    print("Getting all result elements...")
    result_els = get_result_els(page_source)
    n = len(result_els)
    print(f"Found {n} elements.")

    print("Getting the info for all elements...")
    infos = []
    for i in tqdm(range(n)):
        new_info = get_info_from_result_el(result_els[i])
        infos.append(new_info)
    return infos


def get_all_info_from_search_url(
    driver, url, wait_after_page_loaded=3, wait_after_scroll_down=2
):
    driver.get(url)
    print(f"Waiting for {wait_after_page_loaded}s...")
    time.sleep(wait_after_page_loaded)

    # Chrome must be unzoomed so that the whole page fits in the screen in 2 times
    try:
        driver.execute_script(SCROLL_TO_BOTTOM_COMMAND)
    except:
        print("There was an error scrolling down")
    print(f"Waiting for {wait_after_scroll_down}s...")
    time.sleep(wait_after_scroll_down)
    page_source = driver.page_source
    page_parsed_info = get_all_info_from_page_source(page_source)
    return page_parsed_info


def scrap_lksn_pages(
    driver,
    page_list,
    get_search_url,
    wait_time_between_pages=3,
    wait_after_page_loaded=3,
    wait_after_scroll_down=2,
):
    total_info = []
    for p in page_list:
        print(f"Waiting for {wait_time_between_pages}s...")
        time.sleep(wait_time_between_pages)

        print(f"Getting new page: {p}.")
        info = get_all_info_from_search_url(
            driver,
            get_search_url(p),
            wait_after_page_loaded=wait_after_page_loaded,
            wait_after_scroll_down=wait_after_scroll_down,
        )
        total_info += info
    return total_info


if __name__ == "__main__":
    # Parse the arguments
    parser = argparse.ArgumentParser(description="Scrap LinkedIn Sales Navigator")
    parser.add_argument(
        "--search-url",
        type=str,
        help="The url of the search page to scrap",
        required=True,
    )
    parser.add_argument(
        "--start-page",
        type=int,
        help="The page to start scrapping from",
        required=False,
        default=1,
    )
    parser.add_argument(
        "--end-page",
        type=int,
        help="The page to end scrapping at",
        required=False,
        default=1,
    )
    parser.add_argument(
        "--wait-time-between-pages",
        type=int,
        help="The time in seconds to wait between pages",
        required=False,
        default=5,
    )
    parser.add_argument(
        "--wait-after-page-loaded",
        type=int,
        help="The time in seconds to wait after the page is loaded",
        required=False,
        default=3,
    )
    parser.add_argument(
        "--wait-after-scroll-down",
        type=int,
        help="The time in seconds to wait after scrolling down",
        required=False,
        default=3,
    )
    parser.add_argument(
        "--save-format",
        type=str,
        help="The format to save the data in (xlsx or csv)",
        required=False,
        default="csv",
    )
    args = parser.parse_args()

    # Get the arguments
    search_url = args.search_url
    start_page = args.start_page
    end_page = args.end_page
    wait_time_between_pages = args.wait_time_between_pages
    wait_after_page_loaded = args.wait_after_page_loaded
    wait_after_scroll_down = args.wait_after_scroll_down
    save_format = args.save_format
    search_url_base = remove_url_parameter(search_url, "page")

    print("Starting the driver...")
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    # Start the webdriver without any logs
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.get("https://www.linkedin.com/login/")

    print("Inputting the credentials...")
    lk_credentials = get_lk_credentials(LK_CREDENTIALS_PATH)
    enter_ids_on_lk_signin(driver, lk_credentials["email"], lk_credentials["password"])

    if "checkpoint/challenge" in driver.current_url:
        print(
            "It looks like you need to complete a double factor authentification. Please do so and press enter when you are done."
        )
        input()

    driver.get(search_url)

    print(
        "Manual actions needed: go to the browser window and unzoom the page so that the whole page fits in the screen in 2 times. Then press enter here."
    )
    driver.execute_script("document.body.style.zoom = '0.2'")
    input()

    print("Starting the scraping...")

    lksnSearchInfos = scrap_lksn_pages(
        driver,
        page_list=range(start_page, end_page + 1),
        get_search_url=lambda x: get_search_url(search_url_base, x),
        wait_time_between_pages=wait_time_between_pages,
        wait_after_page_loaded=wait_after_page_loaded,
        wait_after_scroll_down=wait_after_scroll_down,
    )

    df = pd.DataFrame(lksnSearchInfos)
    df["linkedin_url"] = df.link_to_profile.apply(get_lk_url_from_sales_lk_url)
    df["company_link"] = df.link_to_company.apply(get_lk_company_url_from_sales_lk_url)
    linkProfiles = {
        "linkProfiles": df["linkedin_url"].tolist()
    }
    linkCompanies = {
        "linkCompanies": df["company_link"].tolist()
    }
    p_link_file_name = r"C:\\Users\gabee\anaconda3\envs\linkedinSalesNavScraper\links.json"
    with open(p_link_file_name, 'w') as file:
        file_data = {
            'links': []
        }
        file_data['links'].append(linkProfiles)
        file_data['links'].append(linkCompanies)
        json.dump(file_data, file, indent=4)

    if save_format == "csv":
        file_name = f"{str(int(time.time()*1000))}_lk_salesnav_export.csv"
        df.to_csv(
            f"./lksn_data/{file_name}",
            index=False,
        )
        print(f"Saved to ./lksn_data/{file_name}")
    else:
        # save_format=="xlsx"
        file_name = f"{str(int(time.time()*1000))}_lk_salesnav_export.xlsx"
        df.to_excel(
            f"./lksn_data/{file_name}",
            index=False,
        )
        print(f"Saved to ./lksn_data/{file_name}")

    driver.close()
    subprocess.run(["python", "liProfiles.py"])
    subprocess.run(["python", "liCompanies.py"])
