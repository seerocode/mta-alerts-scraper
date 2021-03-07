from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import numpy as np
from numpy import random
import time
from random import randint
import sys


def get_page(year):
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)

    url = "https://www.mymtaalerts.com/archive"
    driver.get(url)

    table_id = "ctl00_ContentPlaceHolder1_gridMessages_ctl00"
    timeout = 30

    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, table_id)))
    except TimeoutException:
        driver.quit()

    start_date_input_id = "ctl00_ContentPlaceHolder1_dtpStartDate_dateInput"
    select_start_date = driver.find_element_by_id(start_date_input_id)
    start_date = "01/01/{}".format(year)
    print(start_date)

    select_start_date.send_keys(start_date)

    stop_date_input_id = "ctl00_ContentPlaceHolder1_dtpStopDate_dateInput"
    select_stop_date = driver.find_element_by_id(stop_date_input_id)
    end_date = "12/31/{}".format(year)
    select_stop_date.send_keys(end_date)

    select_stop_date = Select(driver.find_element_by_css_selector(
        'select#ctl00_ContentPlaceHolder1_ddlAgency'))
    select_stop_date.select_by_visible_text("NYCT Subway")

    submit_button = "ctl00_ContentPlaceHolder1_btnGetData"
    driver.find_element_by_id(submit_button).click()

    next_page_button = driver.find_element_by_xpath(
        "//button[contains(@title,'Next Page')]")
    last_page_command = "return false;"
    is_not_last_page_of_results = False if next_page_button.get_attribute(
        'onclick') == last_page_command else True

    while is_not_last_page_of_results:
        html = driver.page_source
        time.sleep(randint(5, 15))
        save_data(html, year)
        next_page_button.click()

        try:
            WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((By.ID, table_id)))
        except TimeoutException:
            driver.quit()

        next_page_button = driver.find_element_by_xpath(
            "//button[contains(@title,'Next Page')]")


def save_data(html, year):
    soup = BeautifulSoup(html, 'lxml')

    table_id = "ctl00_ContentPlaceHolder1_gridMessages_ctl00"
    table = soup.find('table', id=table_id)

    df = pd.read_html(str(table), displayed_only=False)
    alerts = df[0]
    alerts.columns = ['{}'.format(x[2]) for x in alerts.columns]

    values = ["escalator", "elevator"]
    filtered_alerts = alerts[alerts['Subject'].str.contains(
        '|'.join(values), na=False, case=False)]

    print(filtered_alerts)
    if filtered_alerts.size > 0:
        filtered_alerts.to_csv("alerts-{}".format(year) + '.csv', mode='a')
    else:
        print("No NYCT Subway data found for dates")


def main():
    user_input = len(sys.argv[1])
    if user_input < 1:
        SystemExit("Please enter a year")
    get_page(sys.argv[1])


if __name__ == "__main__":
    main()
