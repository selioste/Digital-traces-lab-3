from flask import Flask, render_template, request,  send_file
import logging 
import sys
import requests
import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from pytrends.request import TrendReq

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
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    nb_visitor = print_response(response)
    return prefix_google + render_template('testjs.html', visitors = nb_visitor)

# Define logger on deta
@app.route('/logger', methods = ['GET', 'POST'])
def logger():

    global user_input

    print('Back end log!', file=sys.stderr)
    logging.info("Logging test")
    value = request.form.get("textbox_input")

    return render_template("logger.html",text=value) 

@app.route('/cookies')
def cookies():
    # Request google
    req = requests.get("https://www.google.com/")
    # return req.text
    return render_template("cookies.html", cookie=req.cookies.get_dict())

# googleanalystics
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
KEY_FILE_LOCATION = "keys.json"
VIEW_ID = "281173377"

def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.
    Returns:
      An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    return build('analyticsreporting', 'v4', credentials=credentials)


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
                    'metrics': [{'expression': 'ga:pageviews'}],
                    'dimensions': []
                    # 'dimensions': [{'name': 'ga:country'}]
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
        metricHeaders = columnHeader.get(
            'metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                print(header + ': ', dimension)

            for i, values in enumerate(dateRangeValues):
                print('Date range:', str(i))
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    visitors = value
    return str(visitors)


@app.route('/trend')
def index():
    # Connect to Google Trends API
    pytrends = TrendReq(hl='fr-FR', tz=360, timeout=(10,25),retries=2, backoff_factor=0.1)

    # Set keywords and get trend data
    kw_list = ['banane','orange']
    pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')
    trends = pytrends.interest_over_time()

    # Format data for Chart.js
    labels = trends.index.strftime('%Y-%m-%d').tolist()
    data = {
        'banane': trends['banane'].tolist(),
        'orange': trends['orange'].tolist()
    }

    # Render template and pass data to be plotted
    return render_template('chartjs.html', labels=labels, data=data)

@app.route('/timerlog_image')
def afficher_image():
    return render_template('timer_log.html')

if __name__ == '__main__':
    app.run(debug = True)
