from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
from random import randint
import sys
import logging

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='./temp/myapp.log',
                    filemode='a')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)


def get_page(year):
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox(
        options=opts, executable_path="/usr/local/bin/geckodriver")
    # chrome_options = Options()
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    # # chrome_options.binary_location("/usr/lib/chromium/")
    # driver = webdriver.Chrome(options=chrome_options)

    logging.info('Firefox web driver set!')

    url = "https://www.mymtaalerts.com/archive"
    driver.get(url)
    logging.info('Web driver retrieved URL: {}'.format(url))

    table_id = "ctl00_ContentPlaceHolder1_gridMessages_ctl00"
    timeout = 30

    try:
        logging.info(
            'Trying to wait for table with ID "{}" to appear'.format(table_id))
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, table_id)))
        logging.info('Successfully loaded webpage!')
    except TimeoutException:
        logging.error("Exception occured and webdriver is exiting.")
        driver.quit()

    start_date_input_id = "ctl00_ContentPlaceHolder1_dtpStartDate_dateInput"
    select_start_date = driver.find_element_by_id(start_date_input_id)
    start_date = "01/01/{}".format(year)
    select_start_date.send_keys(start_date)
    logging.info(
        "Start date for the scraper is: {}. Start date set.".format(start_date))

    stop_date_input_id = "ctl00_ContentPlaceHolder1_dtpStopDate_dateInput"
    select_stop_date = driver.find_element_by_id(stop_date_input_id)
    end_date = "12/31/{}".format(year)
    select_stop_date.send_keys(end_date)
    logging.info(
        "End date for the scraper is: {}. End date set.".format(end_date))

    select_stop_date = Select(driver.find_element_by_css_selector(
        'select#ctl00_ContentPlaceHolder1_ddlAgency'))
    select_stop_date.select_by_visible_text("NYCT Subway")
    logging.info("NYCT Subway set as agency.".format(start_date))

    submit_button = "ctl00_ContentPlaceHolder1_btnGetData"
    driver.find_element_by_id(submit_button).click()

    next_page_button = driver.find_element_by_xpath(
        "//button[contains(@title,'Next Page')]")
    last_page_command = "return false;"
    is_not_last_page_of_results = False if next_page_button.get_attribute(
        'onclick') == last_page_command else True

    while is_not_last_page_of_results:
        logging.info("Still going! Not the end of results yet.")
        html = driver.page_source
        time.sleep(randint(5, 15))
        logging.info("Saving data for {}".format(year))
        save_data(html, year)
        logging.info("Data saved! Attempting next page.")
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
