import re
import time as time_module
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
USERNAME = "your_username"
PASSWORD = "your_password"


def check_if_element_exists(driver: webdriver, by_type: By, selector):
    """
    Check if an element exists on the page.
    """
    try:
        driver.find_element(by_type, selector)
        return True
    except NoSuchElementException:
        return False


def login(driver: webdriver, username: str, password: str):
    """
    Log into the website using the given username and password.
    """
    # Navigate to the login page
    driver.get("https://yad2.co.il/login")

    # Find the username and password input fields
    username_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")

    # Enter the username and password
    username_field.send_keys(username)
    time_module.sleep(1)
    password_field.send_keys(password)
    time_module.sleep(1)

    # Submit the login form
    login_form = driver.find_element(By.CLASS_NAME, "common-button")
    login_form.submit()


def wait_for_element(driver: webdriver, selector: str):
    """
    Wait for the specified element to appear on the page.
    """
    # Wait for the page to load
    wait = WebDriverWait(driver, 15)  # wait for up to 15 seconds
    wait.until(lambda d: d.find_element(By.CSS_SELECTOR, selector))


def wait_for_up_ad(driver: webdriver, soup: BeautifulSoup):
    """
    Wait for the next available "up ad" to appear on the page.
    """
    try:
        # Wait for the "time until next up ad" element to appear
        wait_for_element(driver, ".promote-ad_timeButtonContent__P3EhQ")

        # Extract the time from the element
        element = soup.select_one(".promote-ad_timeButtonContent__P3EhQ")
        match = re.search(r"\d{2}:\d{2}:\d{2}", element.get_text())
        time = datetime.strptime(match.group(0), "%H:%M:%S")

        # Calculate the amount of time to wait
        delta = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
        seconds = delta.total_seconds()

        # Log the time we have to wait
        logging.info(f"Waiting {seconds} seconds for the next up ad")

        # Wait for the specified amount of time
        time_module.sleep(seconds)
    except Exception as e:
        # Log any errors that may occur
        logging.error(e)




def click_up_ad(driver: webdriver):
    """
    Click on the "up ad" button when it appears on the page.
    """
    try:
        # Wait for the "up ad" button to appear
        wait_for_element(driver, ".promote-ad_bounceButton__Cwcen")

        # Click on the "up ad" button
        popup_click = driver.find_element(By.CSS_SELECTOR, ".promote-ad_bounceButton__Cwcen")
        popup_click.click()

        # Log that the up ad was clicked successfully
        logging.info("Successfully clicked on the up ad")
    except Exception as e:
        # Log any errors that may occur
        logging.error(e)



def scrape_yad2(username: str, password: str):
    """
    Scrape the yad2.co.il website for available "up ad" buttons.
    """
    # Set up the webdriver
    options = webdriver.ChromeOptions()

    # Specify the user agent
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    # Log into the website
    login(driver, username, password)

    # Wait for the page to load
    wait_for_element(driver, ".ad_wrapper__WjdWz")

    # Parse the page source
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    while True:
        # Refresh the page
        driver.refresh()

        # Check if the "time until next up ad" element exists
        if check_if_element_exists(driver, By.CSS_SELECTOR, ".promote-ad_timeButtonContent__P3EhQ"):
            # Wait for the next available "up ad"
            wait_for_up_ad(driver, soup)
        elif check_if_element_exists(driver, By.CSS_SELECTOR, ".promote-ad_bounceButton__Cwcen"):
            # Click on the "up ad" button
            click_up_ad(driver)


scrape_yad2(USERNAME, PASSWORD)
