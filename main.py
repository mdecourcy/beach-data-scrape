
# function that sends get request to https://www.waterboards.ca.gov/water_issues/programs/beaches/search_beach_mon.html using requests.session
from io import StringIO
import requests
import pandas as pd

import requests

# function that sends requests to get xls output of given payload request
# input: none
# output: xls string
# todo: add input parameters for payload to allow for different queries, scraping data for more than just SD county
def get_xls():
    headers = {
        "Host": "beachwatch.waterboards.ca.gov",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "122",
        "Origin": "https://beachwatch.waterboards.ca.gov",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://beachwatch.waterboards.ca.gov/public/result.php"
    }
    payload = {
        "County": "10",
        "stationID": "",
        "parameter": "",
        "qualifier": "",
        "method": "",
        "created": "30",
        "year": "2023",
        "sort": "`SampleDate`",
        "sortOrder": "DESC",
        "submit": "Search"
    }

    try:
        with requests.session() as sesh:
            resp = sesh.post('https://beachwatch.waterboards.ca.gov/public/result.php', data=payload, headers=headers)
            resp.raise_for_status()
            xls = sesh.get('https://beachwatch.waterboards.ca.gov/public/export.php')
            xls.raise_for_status()
            return xls.text
    except requests.exceptions.HTTPError as e:
        print(f"An error occurred: {e}")

# function that converts tabbed xls string to dataframe
# input: xls string
# output: dataframe
def get_dataframe(xls: str):
    xls = xls.replace('\t\t', '\t') # replace double tabs with single tab to avoid pandas error as original dataset has *some* double tabs
    df = pd.read_csv(StringIO(xls), sep='\t', engine='python')
    return df

# function that returns dataframe between two dates
# input: dataframe, start date, end date
# output: dataframe
def filter_between_dates(df: pd.DataFrame, start_date: str, end_date: str):
    df['SampleDate'] = pd.to_datetime(df['SampleDate'])
    df = df.loc[(df['SampleDate'] >= start_date) & (df['SampleDate'] <= end_date)]
    return df

# function that takes in dataframe and posts to a mongodb api
# input: dataframe
# output: none
# todo: post to api
# todo: bulk post to api to load historical data
def post_to_mongo_api(df: pd.DataFrame, url: str):
    try:
        payload = df.to_json(orient="records")
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text.encode('utf8'))
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"An error occurred: {e}")

    
if __name__ == "__main__":
    xls = get_xls() 
    df = get_dataframe(xls)
    # post_to_mongo(df)
    # print(df["Beach Name"].unique()) # get unique values for Beach Name column
    between = filter_between_dates(df, '2023-01-29', '2023-01-30')
    print(between.to_json(orient="records"))
