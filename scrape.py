import os
import time
import re
import csv
from selenium import webdriver
from lxml import html
from tabulate import tabulate
from dotenv import load_dotenv


def login(driver, username, password):
    '''
    Log-in to the authenticated website
    '''
    u = driver.find_element_by_name("_username")
    u.send_keys(username)
    p = driver.find_element_by_name("_password")
    p.send_keys(password)
    p.submit()


def get_runs(runs_list):
    '''
    Get runs list well formatted
    '''
    # runs_list = runs_html.cssselect(
    #     "body > app-account > div > app-my-runs > div > div > div:nth-child(2) > div:nth-child(2) > div > div.container.runs")
    page_runs_list = driver.find_elements_by_css_selector(
        "body > app-account > div > app-my-runs > div > div > div:nth-child(2) > div:nth-child(2) > div > div.container.runs")
    for run in page_runs_list:
        date = run.find_element_by_css_selector("div.operation-date").text
        distance = run.find_element_by_css_selector(
            "div.row.align-items-center > div:nth-child(2) > div > div").text
        distance = float(
            re.search(r'\d+,\d+', distance).group().replace(',', '.'))
        duration = run.find_element_by_css_selector(
            "div.row.align-items-center > div:nth-child(3) > div > div").text
        duration_digits = re.search(r"(\d+)min\ (\d+)sec", duration)
        # If duration is less than 1 minute it will display only seconds
        if duration_digits is None:
            duration_digits = re.search(r"(\d+)sec", duration)
            duration = int(duration_digits.group(1))
        else:
            duration = int(duration_digits.group(1)) * 60 + \
                int(duration_digits.group(2))
        runs_list.append([date, distance, duration])
    return runs_list


def get_max_page_number(pagination_links):
    '''
    Get the maximum page number from a list of pagination links
    '''
    max_page = 0
    for link in pagination_links:
        # Check page number only if there are digits in the link text
        s = link.text.strip()
        if any(c.isdigit() for c in s):
            digits = [int(c) for c in s.split() if c.isdigit()]
            page = digits[0]
            if page > max_page:
                max_page = page
    return max_page


def format_runs_csv(runs_list, headers):
    '''
    Format runs into csv format for analysis
    '''
    with open('./runs.csv', 'w+') as f:
        w = csv.writer(f)
        w.writerow(headers)
        for run in runs_list:
            w.writerow(run)


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("https://www.velib-metropole.fr/login")

    # Log-in
    load_dotenv()
    login(driver, username=os.getenv("VELIB_USERNAME"),
          password=os.getenv("VELIB_PASSWORD"))

    # Go to page for my runs
    driver.get("https://www.velib-metropole.fr/private/account#/my-runs")
    # Leave some time for JS to generate the HTML elements we need
    time.sleep(3)
    driver.get("https://www.velib-metropole.fr/private/account#/my-runs")
    runs_list = []

    # Get pagination links
    pagination_links = driver.find_elements_by_css_selector(
        "ul.pagination > li > a")
    max_page_number = get_max_page_number(pagination_links)

    # Always click on the "next" pagination link until exhausting the pages to scrape
    for i in range(max_page_number):
        pagination_links = driver.find_elements_by_css_selector(
            "ul.pagination > li > a")
        runs_list = get_runs(runs_list)
        print("Got page {0} runs".format(i + 1))
        # time.sleep(1)
        if i < max_page_number - 1:
            pagination_links[len(pagination_links) - 2].click()
            time.sleep(2)  # leave time for JS to re-generate HTML

    # Write results in a pretty table
    headers = ["date", "distance", "duration"]
    print(tabulate(runs_list, headers=headers))

    # Format runs into a CSV file
    format_runs_csv(runs_list, headers)
