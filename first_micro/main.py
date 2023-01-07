from flask import Flask, render_template, request
import requests
import logging
import sys
import os
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/', methods=["GET"])
def hello_world():
    prefix_google = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-250915546-1"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'UA-250915546-1');
    </script>
    """
    return prefix_google + render_template('index.html')

# Define logger on deta
@app.route('/logger', methods = ['GET', 'POST'])
def logger():

    global user_input

    print('Back end log!', file=sys.stderr)
    logging.info("Logging test")
    value = request.form.get("textbox_input")

    return render_template("logger.html",text=value) 

# Cookies from googleanalystics
@app.route('/ganalytics', methods = ['GET', 'POST'])
def get_analytics():

    mail = os.getenv("Google_mail")
    password = os.getenv("Google_password")

    payload = {'inUserName': mail, 'inUserPass': password}
    url = "https://analytics.google.com/analytics/web/#/report-home/a250915546w344989643p281173377"
    r = requests.post(url, data=payload)
    req = requests.get(url, cookies=r.cookies)
    return req.text

# Request with oauth on analystics reporting
"""Hello Analytics Reporting API V4."""

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'test-app-deta-d16db0e9e5b3.json'
VIEW_ID = '281173377'

def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics

def get_report(analytics):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
          'metrics': [{'expression': 'ga:sessions'}],
          'dimensions': [{'name': 'ga:country'}]
        }]
      }
  ).execute()

def print_response(response):
  """Parses and prints the Analytics Reporting API V4 response.

  Args:
    response: An Analytics Reporting API V4 response.
  """
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])

      for header, dimension in zip(dimensionHeaders, dimensions):
        print(header + ': ', dimension)

      for i, values in enumerate(dateRangeValues):
        print('Date range:', str(i))
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          print(metricHeader.get('name') + ':', value)

def main():
  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  print_response(response)

@app.route('/test', methods = ['GET', 'POST'])

def number_visitors():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    nb_visitor = print_response(response)
    print("test visitor", nb_visitor)
    logging.info("Test gdx")
    return render_template('index.html', visitors=str(nb_visitor))


app = Flask(__name__)

@app.route('/', methods=["GET"])
def hello_world():
    prefix_google = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-250915546-1"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'UA-250915546-1');
    </script>
    """
    return prefix_google + render_template('index.html')

# Define logger on deta
@app.route('/logger', methods = ['GET', 'POST'])
def logger():

    global user_input

    print('Back end log!', file=sys.stderr)
    logging.info("Logging test")
    value = request.form.get("textbox_input")

    return render_template("logger.html",text=value) 

# Cookies from googleanalystics
@app.route('/ganalytics', methods = ['GET', 'POST'])
def get_analytics():

    mail = os.getenv("Google_mail")
    password = os.getenv("Google_password")

    payload = {'inUserName': mail, 'inUserPass': password}
    url = "https://analytics.google.com/analytics/web/#/report-home/a250915546w344989643p281173377"
    r = requests.post(url, data=payload)
    req = requests.get(url, cookies=r.cookies)
    return req.text

# Trend
import pandas as pd
from pytrends.request import TrendReq


@app.route('/pytrends', methods = ['GET', 'POST'])
def get_pytrends():
    pytrend = TrendReq(hl='fr', tz=60)
    kw=['Al-Nassr FC']
    pytrend.build_payload(kw, cat=0, timeframe='today 3-m', geo='FR', gprop='')
    df=pytrend.interest_over_time().reset_index()
    df.set_index("date",inplace=True)
    
    return render_template('graph.html', labels=df.index.strftime("%d/%m/%Y").tolist(), values=df["Al-Nassr FC"].tolist())

if __name__ == '__main__':
    app.run(debug = True)
