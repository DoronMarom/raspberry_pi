import flask
from flask_restful import Api, Resource, reqparse, request, abort, fields, marshal_with
import json
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import requests

app = flask.Flask(__name__)
api = Api(app)


def signin_to_tableau(driver, user_name, password):
    try:
        # Wait until log in and password appears on page
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'tb-text-box-input.tb-enable-selection.ng-pristine.ng'
                                                             '-untouched.ng-empty.ng-invalid.ng-invalid-required')))
        # Insert user name
        content_user_name = driver.find_element_by_class_name('tb-text-box-input.tb-enable-selection.ng-pristine.ng'
                                                              '-untouched.ng-empty.ng-invalid.ng-invalid-required')
        content_user_name.send_keys(user_name)
        # Insert password
        content_password = driver.find_element_by_class_name(
            'tb-text-box-input.tb-enable-selection.ng-pristine.ng-untouched.ng-empty.ng-invalid.ng-invalid-required')
        content_password.send_keys(password)
        driver.find_element_by_class_name('tb-orange-button.tb-button-login').click()
        return 1
    except Exception as e:
        return e.args


def open_expected_report(driver, url):
    try:
        time.sleep(5)
        driver.get(url)
        time.sleep(5)
        driver.switch_to.frame(0)
        driver.find_element_by_xpath('//*[@id="toggle-fullscreen-ToolbarButton"]').click()
        return 1
    except Exception as e:
        return f"Can't open expected report {e.args}"


def open_browser_in_full_screen(driver, url):
    driver.get(url)
    driver.maximize_window()


def get_chrome_driver():
    driver = webdriver.Chrome()
    return driver


def get_permissions_for_tableau():
    try:
        response = requests.get('https://hfweh1msjb.execute-api.us-east-1.amazonaws.com/v1/tableau')
        return json.loads(response.text)
    except Exception as e:
        return f"Didn't get permissions details from aws {e.args}"


def get_reports_list_for_tableau():
    try:
        response = requests.get('https://ryqx5f2qd1.execute-api.us-east-1.amazonaws.com/v1/tableau-reports-list')
        return json.loads(response.text)
    except Exception as e:
        return f"Didn't get reports_list details from aws {e.args}"


tableau_put_args = reqparse.RequestParser()
tableau_put_args.add_argument("report_name", type=str, help="report_name is required", required=True)
tableau_put_args.add_argument("challenge", type=str, help="url is required", required=True)


@app.route('/tablaeu', methods=['POST'])
def query_records():
    mondy_request = request.get_json()
    if 'challenge' in mondy_request:
        return mondy_request
    else:
        try:
            reports_name = mondy_request['event']['value']['label']['text']
            results = get_permissions_for_tableau()
            results_reports_list = get_reports_list_for_tableau()
            base_url = results['base_url']
            user_name = results['user']
            password = results['password']
            if 'Close' in reports_name:
                subprocess.run(['pkill', '-a', '-i', 'Google Chrome'], capture_output=True)
                return {
                    'statusCode': 200,
                    'body': json.dumps('Closed chrome browser')
                }
            else:
                chrome_driver = get_chrome_driver()
                open_browser_in_full_screen(chrome_driver, base_url)
                signin_to_tableau(chrome_driver, user_name, password)
                open_report = open_expected_report(chrome_driver, results_reports_list[reports_name])
                if open_report == 1:
                    return {
                        'statusCode': 200,
                        'body': json.dumps(f'Open report {reports_name}')
                    }
                else:
                    return {
                        'statusCode': 404,
                        'body': json.dumps(f'Faild Open report {reports_name}')
                    }
        except Exception as e:
            return {
                        'statusCode': 404,
                        'body': json.dumps(f'Faild Open report {e.args}')
                    }


if __name__ == "__main__":
    app.run(debug=True)
