import logging
from io import StringIO
from typing import List, Dict
import pandas as pd
import requests

# function that sends requests to get xls output of given payload request
# input: none
# output: xls string
# todo: add input parameters for payload to allow for different queries, scraping data for more than just SD county
def get_xls(payload: Dict) -> str:
    headers = {
        "Host": "beachwatch.waterboards.ca.gov",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://beachwatch.waterboards.ca.gov",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://beachwatch.waterboards.ca.gov/public/result.php"
    }
    with requests.Session() as session:
        response = session.post('https://beachwatch.waterboards.ca.gov/public/result.php', data=payload, headers=headers)
        response.raise_for_status()
        xls = session.get('https://beachwatch.waterboards.ca.gov/public/export.php')
        xls.raise_for_status()
        return xls.text

# function that converts tabbed xls string to dataframe
# input: xls string
# output: dataframe
def get_dataframe(xls: str) -> pd.DataFrame: 
    xls = xls.replace('\t\t', '\t') # replace double tabs with single tab to avoid pandas error as original dataset has *some* double tabs
    return pd.read_csv(StringIO(xls), sep='\t', engine='python')


# function that returns dataframe between two dates
# input: dataframe, start date, end date
# output: dataframe
def filter_between_dates(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    df['SampleDate'] = pd.to_datetime(df['SampleDate'])
    return df.loc[(df['SampleDate'] >= start_date) & (df['SampleDate'] <= end_date)]

# function that takes in dataframe and posts to a mongodb api
# input: dataframe
# output: none
# todo: post to api
# todo: bulk post to api to load historical data
def post_to_mongo_api(df: pd.DataFrame, url: str) -> None:
    try:
        payload = df.to_dict('records')
        headers = {}
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
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
    xls = get_xls(payload)
    df = get_dataframe(xls)
    # post_to_mongo(df)
    # print(df["Beach Name"].unique()) # get unique values for Beach Name column
    between = filter_between_dates(df, '2023-01-29', '2023-01-30') # filter between two dates, to be used to only post data collected that day
    logging.info(between.to_dict('records'))