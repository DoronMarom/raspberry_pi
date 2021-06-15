import json
import datetime
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import requests


def signin_to_desirable_web_site(driver, user_name, password, web_site_name):
    try:
        signIn_locations = Path(__file__).cwd()
        selenium_config = Path.joinpath(signIn_locations,"selenium_config.json")
        with open(selenium_config, 'r') as element_config:
            elements_ditails = json.loads(element_config.read())
            # Wait until log in and password appears on page

            wait = WebDriverWait(driver, 10)
            wait.until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, elements_ditails[web_site_name]['VISIBILITY_OF_ELEMENT'])))
            # Insert user name
            content_user_name = driver.find_element_by_class_name(
                elements_ditails[web_site_name]['USER_NAME_ELEMENT'])
            content_user_name.send_keys(user_name)
            # Insert password
            content_password = driver.find_element_by_class_name(
                elements_ditails[web_site_name]['PASSWORD_ELEMENT'])
            content_password.send_keys(password)
            driver.find_element_by_class_name(elements_ditails[web_site_name]['SIGNIN_BUTTON_ELEMENT']).click()
        return 1
    except Exception as e:
        return e.args


def open_tableau_reports_in_full_screen(driver):
    try:
        driver.switch_to.frame(0)
        driver.find_element_by_xpath('//*[@id="toggle-fullscreen-ToolbarButton"]').click()
        return 1
    except Exception as e:
        return f"Can't open expected report {e.args}"


def open_expected_report(driver, url):
    try:
        time.sleep(5)
        driver.get(url)
        time.sleep(5)
        return 1
    except Exception as e:
        return f"Can't open expected report {e.args}"


def minimum_maximum_page(driver):
    try:
        driver.find_element_by_xpath('//*[@id="toggle-fullscreen-ToolbarButton"]').click()
        driver.refresh()
        time.sleep(2)
        return 1

    except Exception as e:
        return f"Can't open expected report {e.args}"


def open_browser_in_full_screen(driver, url):
    driver.get(url)
    driver.maximize_window()


def get_chrome_driver():
    driver = webdriver.Chrome()
    return driver


def get_permissions_for_ditails_for_relevant_site():
    try:
        response = requests.get('https://hfweh1msjb.execute-api.us-east-1.amazonaws.com/v1/tableau')
        return json.loads(response.text)
    except Exception as e:
        return f"Didn't get permissions details from aws {e.args}"


def get_reports_list():
    try:
        response = requests.get('https://ryqx5f2qd1.execute-api.us-east-1.amazonaws.com/v1/tableau-reports-list')
        return json.loads(response.text)
    except Exception as e:
        return f"Didn't get reports_list details from aws {e.args}"


def get_report_name_according_to_my_tv_name(tv_name):
    try:
        body = json.dumps({"tv_name": tv_name})
        url = 'https://w64q4i353h.execute-api.us-east-1.amazonaws.com/v1/report-name'
        response = requests.post(url=url, data=body)
        return json.loads(response.text)
    except Exception as e:
        return f"Didn't get report name"


def main():
    data_start_run = datetime.datetime.now()
    number_of_refresh = 0
    tv_name = 'Data_Engineer_1'
    old_report = ''
    chrome_driver = None
    minimaise_page_if_not_first_run = 0
    os.system(f'''osascript -e 'display notification "TV NAME {tv_name}"' ''')
    while True:
        try:
            # Create chrome driver if not exist
            if not chrome_driver:
                chrome_driver = get_chrome_driver()
            reports_name = get_report_name_according_to_my_tv_name(tv_name)
            # Check if report name change if yes insert to code
            if reports_name['report_name'] != old_report:
                results_reports_list = get_reports_list()
                web_type = results_reports_list[reports_name['report_name']][1]
                # Code for url that doesn't need sign in
                if web_type == 'general':
                    results_reports_list = get_reports_list()
                    open_browser_in_full_screen(chrome_driver, results_reports_list[reports_name['report_name']][0])
                else:
                    results = get_permissions_for_ditails_for_relevant_site()
                    base_url = results[results_reports_list[reports_name['report_name']][1]]['base_url']
                    user_name = results[results_reports_list[reports_name['report_name']][1]]['user']
                    password = results[results_reports_list[reports_name['report_name']][1]]['password']
                    open_browser_in_full_screen(chrome_driver, base_url)
                    signin_to_desirable_web_site(chrome_driver, user_name, password,
                                                 results_reports_list[reports_name['report_name']][1])
                    open_expected_report(chrome_driver, results_reports_list[reports_name['report_name']][0])
                    # Only for Tablaeu press on full screen button after open relevant report
                    if results_reports_list[reports_name['report_name']][1] == 'tablaeu':
                        if minimaise_page_if_not_first_run:
                            minimum_maximum_page(chrome_driver)
                        open_tableau_reports_in_full_screen(chrome_driver)
                        minimaise_page_if_not_first_run = 1
                old_report = reports_name['report_name']
            else:
                time.sleep(2)
                data_current_time = datetime.datetime.now()
                diff = data_current_time - data_start_run
                diff_in_second = diff.seconds
                diff_in_hour = diff_in_second / 3600
                local_refresh_counter = number_of_refresh + 1
                if local_refresh_counter <= diff_in_hour:
                    chrome_driver.refresh()
                    number_of_refresh += 1
        except Exception as e:
            return f"Report didn't open {e.args}"
        finally:
            continue


if __name__ == "__main__":
    main()
