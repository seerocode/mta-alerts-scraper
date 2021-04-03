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
from sqlalchemy import create_engine
from tqdm import tqdm

########## LOGGING ##########
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%m-%d-%Y %H:%M:%S',
                    filename='./app.log',
                    filemode='w')

# Create a new database file:
engine = create_engine('sqlite:///alerts.db', echo=True)
sqlite_connection = engine.connect()


def scrape(year):
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox(
        options=opts, executable_path="/usr/local/bin/geckodriver")

    logging.info('Firefox web driver set!')

    url = "https://www.mymtaalerts.com/archive"
    driver.get(url)
    logging.info('Web driver retrieved URL: {}'.format(url))

    alerts_table_id = "ctl00_ContentPlaceHolder1_gridMessages_ctl00"
    timeout = 30

    try:
        logging.info(
            'Waiting for table with ID "{}" to render...'.format(alerts_table_id))
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, alerts_table_id)))
        logging.info('Successfully loaded alerts table!')
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

    # Wait for page to load
    time.sleep(10)

    pages_holder = driver.find_element_by_xpath(
        "//div[contains(@class, 'rgInfoPart')]")
    pages_html = BeautifulSoup(pages_holder.get_attribute('innerHTML'), 'lxml')
    number_of_pages = int(pages_html.select(
        'strong:nth-child(2)')[0].get_text())

    for page in tqdm(range(number_of_pages)):
        logging.info("You are on page number {}".format(page + 1))
        html = driver.page_source
        time.sleep(randint(5, 15))
        save_data(html)

        next_page_button = driver.find_element_by_xpath(
            "//button[contains(@title,'Next Page')]")
        next_page_button.click()
        time.sleep(15)

    sqlite_connection.close()
    driver.quit()
    print("Data scraping for {} complete!".format(year))


def save_data(html):
    soup = BeautifulSoup(html, 'lxml')

    table_id = "ctl00_ContentPlaceHolder1_gridMessages_ctl00"
    table = soup.find('table', id=table_id)

    df = pd.read_html(str(table), displayed_only=False)
    alerts = df[0]
    alerts.columns = ['{}'.format(x[2]) for x in alerts.columns]

    values = ["escalator", "elevator"]
    filtered_alerts = alerts[alerts['Subject'].str.contains(
        '|'.join(values), na=False, case=False)]

    if filtered_alerts.size > 0:
        filtered_alerts.to_sql(
            "mtaalerts", sqlite_connection, if_exists='append')
        logging.info("Saved found alerts to database.")
    else:
        logging.info("No NYCT Subway data found for dates.")


def main():
    user_input = len(sys.argv)
    if user_input < 2:
        print("Please enter a year.")
        SystemExit()
    else:
        scrape(sys.argv[1])


if __name__ == "__main__":
    main()
