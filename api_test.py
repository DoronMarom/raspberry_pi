import flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
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


# tableau_put_args = reqparse.RequestParser()
# tableau_put_args.add_argument("report_name", type=str, help="report_name is required", required=True)
# tableau_put_args.add_argument("url", type=str, help="url is required", required=True)
#
#
class Tablaeu(Resource):
    base_url = ''
    user_name = ''
    password = ''
    tableau_url = ''

    def get(self, reports_name):
        try:
            results = get_permissions_for_tableau()
            results_reports_list = get_reports_list_for_tableau()
            self.base_url = results['base_url']
            self.user_name = results['user']
            self.password = results['password']
            self.tableau_url = results_reports_list[reports_name]
            chrome_driver = get_chrome_driver()
            open_browser_in_full_screen(chrome_driver, self.base_url)
            signin_to_tableau(chrome_driver, self.user_name, self.password)
            open_report = open_expected_report(chrome_driver, results_reports_list[reports_name])
            if open_report == 1:
                return "Report_open", 200
            else:
                return open_report
        except Exception as e:
            return f"Can't open the relevant page {e.args}"

    # @marshal_with(resource_fields)
    # def put(self):
    #     try:
    #         args = tableau_put_args.parse_args()
    #         report = ReportModel(report_name=args['report_name'], url=args['url'])
    #         db.session.add(report)
    #         db.session.commit()
    #         return report, 201
    #     except Exception as e:
    #         return f"Can't open the relevant page {e.args}"


api.add_resource(Tablaeu, "/tableau/<string:reports_name>")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
