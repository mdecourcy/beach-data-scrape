
# function that sends get request to https://www.waterboards.ca.gov/water_issues/programs/beaches/search_beach_mon.html using requests.session
from io import StringIO
import json
import requests
import pandas as pd
import uuid

# function that sends requests to get xls output of given payload request
# input: none
# output: xls string
# todo: add input parameters for payload


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
            resp = sesh.post(
                'https://beachwatch.waterboards.ca.gov/public/result.php', data=payload, headers=headers)
            resp.raise_for_status()
            xls = sesh.get(
                'https://beachwatch.waterboards.ca.gov/public/export.php')
            xls.raise_for_status()
            return xls.text
    except requests.exceptions.HTTPError as e:
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
# todo: add input parameters for api url
# todo: add error handling
# todo: post to api


def post_to_mongo_api(df: pd.DataFrame, url: str):
    try:
        payload = df.to_json(orient="records")
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text.encode('utf8'))
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"An error occurred: {e}")


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


def convert_dataframe_to_mongodb(df, column_map):
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
    df['Sample DateTime'] = pd.to_datetime(
        df['SampleDate'] + ' ' + df['SampleTime'])
    converted_dates = []

    for _, row in df.iterrows():
        sample_datetime = row['Sample DateTime'].tz_localize(
            'UTC').tz_convert('Etc/GMT+9')
        converted_dates.append(sample_datetime.isoformat())

    df['Sample DateTime'] = converted_dates
    return df


if __name__ == "__main__":
    xls = get_xls()
    df = get_dataframe(xls)
    # Convert the DataFrame to MongoDB conventions
    converted_df = convert_dataframe_to_mongodb(df, column_map)
    # Convert the DataFrame to JSON
    json_data = converted_df.to_json(orient='records')
    # Write the JSON data to the output file
    with open('output.json', 'w') as file:
        file.write(json_data)
    # post_to_mongo(df)
    # print(df["Beach Name"].unique()) # get unique values for parameter column
    # between = filter_between_dates(df, '2023-05-15', '2023-05-19')
    # print(between.to_json(orient="records"))
