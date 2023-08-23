from io import StringIO
import json
import requests
import pandas as pd
import uuid
import logging
import os
import argparse
from datetime import datetime
import dotenv  

dotenv.load_dotenv()

INFLUXDB_URL = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG', 'health')
INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET', 'waterquality')
INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN', '')

# Configuring the logger
logging.basicConfig(filename='app.log',  # Log goes to this file
                    level=logging.INFO,   # Capture everything from info level upwards
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Format of the log

logger = logging.getLogger(__name__)  # Create logger instance for this module


# function that sends requests to get xls output of given payload request
# input: none
# output: xls string
# todo: add input parameters for payload


def get_xls(year=2023, county=10):
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
        "County": f"{county}",
        "stationID": "",
        "parameter": "",
        "qualifier": "",
        "method": "",
        "created": "",
        "year": f"{year}",
        "sort": "`SampleDate`",
        "sortOrder": "DESC",
        "submit": "Search"
    }

    try:
        with requests.session() as sesh:
            resp = sesh.post(
                'https://beachwatch.waterboards.ca.gov/public/result.php', data=payload, headers=headers)
            resp.raise_for_status()
            xls = sesh.get(
                'https://beachwatch.waterboards.ca.gov/public/export.php')
            xls.raise_for_status()
            return xls.text
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTPError in get_xls function: {e}")
        print(f"An error occurred: {e}")

# function that converts tabbed xls string to dataframe
# input: xls string
# output: dataframe


def get_dataframe(xls: str):
    # replace double tabs with single tab to avoid pandas error as original dataset has *some* double tabs
    xls = xls.replace('\t\t', '\t')
    df = pd.read_csv(StringIO(xls), sep='\t', engine='python')
    return df

# function that returns dataframe between two dates
# input: dataframe, start date, end date
# output: dataframe


def filter_between_dates(df: pd.DataFrame, start_date: str, end_date: str):
    df['SampleDate'] = pd.to_datetime(df['SampleDate'])
    df = df.loc[(df['SampleDate'] >= start_date)
                & (df['SampleDate'] <= end_date)]
    return df

# function that takes in dataframe and posts to a mongodb api
# input: dataframe
# output: none

# Define the column map for converting column names
column_map = {
    'id': '_id',
    'Station_ID': 'station_id',
    'Station Name': 'station_name',
    'SampleDate': 'sample_date',
    'SampleTime': 'sample_time',
    'parameter': 'parameter',
    'qualifier': 'qualifier',
    'Result': 'result',
    'unit': 'unit',
    'method': 'method',
    'type': 'type',
    'County': 'county',
    'Description': 'description',
    'Beach Name': 'beach_name',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'CreateDate': 'create_date'
}


def convert_df_column_names(df, column_map):
    # Create a dictionary to store the converted column names and their corresponding values
    converted_data = {}

    df = date_time_to_datetime(df)

    # Iterate over the columns in the DataFrame
    for column in df.columns:
        if column in column_map:
            converted_column = column_map[column]
        else:
            converted_column = column.lower().replace(' ', '_')
        converted_data[converted_column] = df[column].values.tolist()

    # Add a new column '_id' with generated GUIDs
    converted_data['_id'] = [str(uuid.uuid4()) for _ in range(len(df))]

    # Convert the dictionary to a new DataFrame
    converted_df = pd.DataFrame(converted_data)

    return converted_df


def date_time_to_datetime(df):
    df['sample_datetime'] = pd.to_datetime(df['SampleDate'] + ' ' + df['SampleTime'])
    df['sample_datetime'] = df['sample_datetime'].dt.tz_localize('America/Los_Angeles').dt.tz_convert('UTC')
    return df


def write_to_influxdb(df, url, org, bucket, token):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "text/plain"
    }
    
    line_protocol_data = df_to_line_protocol(df)
    
    try:
        write_url = f"{url}/api/v2/write?org={org}&bucket={bucket}&precision=ns"
        response = requests.post(write_url, headers=headers, data=line_protocol_data)
        
        if not response.ok:
            logger.error(response.content.decode('utf-8'))  
        
        response.raise_for_status()
    except Exception as e:
        logger.exception("Exception occurred in write to influx db {e}")

def df_to_line_protocol(df):
    lines = []
    for _, row in df.iterrows():
        # The beach name and station_id are tags. We need to escape special characters.
        beach_name_escaped = row["beach_name"].replace(",", r"\,").replace(" ", r"\ ")
        station_id = row["station_id"]
        tag_set = f'beach_name={beach_name_escaped},station_id={station_id}'

        
        # Check if the result is numeric (integer or float)
        if isinstance(row['result'], (int, float)):
            field_set = f'parameter="{row["parameter"]}",result={row["result"]}'
        else:
            field_set = f'parameter="{row["parameter"]}",result="{row["result"]}"'
        
        # Timestamp remains as is
        timestamp = int(pd.Timestamp(row['sample_datetime']).value)
        measurement = row["parameter"].replace(",", r"\,").replace(" ", r"\ ")
        # Combine to form the line protocol
        line = f"{measurement},{tag_set} {field_set} {timestamp}"
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and process water quality data.")
    parser.add_argument('--first-pass', action='store_true', help="Run the script for all years from 2000 to the present year.")
    args = parser.parse_args()

    if args.first_pass:
        current_year = pd.Timestamp.now().year
        for year in range(2000, current_year + 1):
            xls = get_xls(str(year))
            if xls:
                df = get_dataframe(xls)
                if df is not None:
                    logger.info(f'found data for {year}, inserting to db...')
                    converted_df = convert_df_column_names(df, column_map)
                    write_to_influxdb(converted_df, INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN)
    else:
        xls = get_xls()
        if xls:
            df = get_dataframe(xls)
            if df is not None:
                converted_df = convert_df_column_names(df, column_map)
                write_to_influxdb(converted_df, INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET, INFLUXDB_TOKEN)
