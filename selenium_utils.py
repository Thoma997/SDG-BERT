# -------------
# This module delivers helper functions
# to get a driver instance for the chrome webdriver
# make sure the path to the webdriver is right
# -------------

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import settings
import helpers

def get_driver_options():
    """
    Returns default driver options
    this function is used by the
    get_driver_with_options function only.
    """
    # Define Browser Options
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Hides the browser window
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    return chrome_options


def get_driver_with_options():
    """
    Returns a driver object of the chrome
    web driver. This can be used for crawling.
    """
    #options = get_driver_options()
    #return webdriver.Chrome(options=options)
    return webdriver.Chrome()

def close_driver(driver):
    """
    Closes the webcrawler object which is
    passed to the function as argument.

    Argument:
    driver -- chrome webdriver object
    """
    driver.close()


def click_button_xpath(driver, platform):
    """
    Clicks the "show more" button when scrolling down the review page of a play store app
    Tested yet with review pages only.

    Argument:
    driver -- the selenium driver holding the current session
    """
    xpath = settings.platforms[platform]['search_listings']['show_more_xpath']
    time.sleep(1)
    show_more_button = driver.find_elements_by_xpath(xpath)[0]
    driver.execute_script("arguments[0].click();", show_more_button)


def scroll_down_page(driver):
    # Scroll down to the bottom.
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    # Wait to load the page
    time.sleep(1)
    # Scroll down again if bottom changed.
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    # Calculate new scroll height and compare with last height.
    return driver.execute_script("return document.body.scrollHeight")


def is_date_reached(driver, platform):
    search_by = settings.platforms[platform]['search_listings']['search_by']
    search_query = settings.platforms[platform]['search_listings']['search_query']
    element_positions = settings.platforms[platform]['search_listings']['element_positions']
    date_format = settings.platforms[platform]['search_listings']['date_format']
    reference_date = settings.platforms[platform]['search_listings']['reference_date']
    reference_date = datetime.strptime(reference_date, '%Y-%m-%d')
    date = None

    if search_by == 'class':
        elements = driver.find_elements_by_class_name(search_query)
    else:
        return None

    if len(elements) >= 2:
        for pos in element_positions:
            try:
                text = str(elements[pos].text).strip()
                date = datetime.strptime(text, date_format)
                break
            except ValueError as e:
                helpers.log('Can not generate date from {} and format {} at pos {}'.format(text, date_format, pos))

        if not date:
            raise ValueError('Can not generate any date')

        if date <= reference_date:
            return True
        else:
            return False
    else:
        raise LookupError('No elements found using {}'.format())


def scroll_down_till_limit(driver, platform):
    """
    Scrolls down a webpage x_times times. Clicking button button when scrolled down if
    specified.

    Arguments:
    driver -- chrome selenium driver of current session
    x_times -- how many times the driver should scroll until the end of the page
    button -- which button to click when scrolled down

    Returns:
    driver -- the webdriver at the final state
    """
    # Scroll page to load whole content
    last_height = 0
    while True:
        new_height = scroll_down_page(driver)
        # if no more scrolling possible
        if new_height == last_height:
            break
        # if specified point in past reached
        if is_date_reached(driver, platform):
            break

        last_height = new_height
        click_button_xpath(driver, platform)

    return driver
