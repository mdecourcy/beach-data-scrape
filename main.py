
# function that sends get request to https://www.waterboards.ca.gov/water_issues/programs/beaches/search_beach_mon.html using requests.session
from io import StringIO
import requests
import pandas as pd

import requests

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


def get_dataframe(xls: str):
    xls = xls.replace('\t\t', '\t')
    df = pd.read_csv(StringIO(xls), sep='\t', engine='python')
    return df

def return_between_dates(df: pd.DataFrame, start_date: str, end_date: str):
    df['SampleDate'] = pd.to_datetime(df['SampleDate'])
    df = df.loc[(df['SampleDate'] >= start_date) & (df['SampleDate'] <= end_date)]
    return df

def main():
    xls = get_xls()
    df = get_dataframe(xls)
    print(df)
    # print(df["parameter"].unique())
    # between = return_between_dates(df, '2023-01-15', '2023-01-25')
    # print(between)

main()