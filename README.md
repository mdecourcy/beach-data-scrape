# Beach Monitoring Data Retriever

This code provides functions for sending requests to the California State Water Resources Control Board website to obtain water quality data for San Diego County, and then process the data and post it to a MongoDB API.

### Dependencies

    - logging
    - io
    - typing
    - pandas
    - requests

### How to use

To use this code, run the Python script in a Python environment with the required dependencies installed. The script will retrieve water quality data for San Diego County from the California State Water Resources Control Board website and filter it by date. The data will then be logged and can be optionally posted to a MongoDB API.

### Functions

`get_xls(payload: Dict) -> str`

This function sends requests to the California State Water Resources Control Board website to retrieve water quality data for San Diego County. It takes a dictionary of payload data as an input and returns an Excel file as a string.

`get_dataframe(xls: str) -> pd.DataFrame`

This function takes an Excel file as a string and converts it to a Pandas DataFrame.

`filter_between_dates(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame`

This function filters the DataFrame by date, returning a new DataFrame with only the data collected between the specified start and end dates.

`post_to_mongo_api(df: pd.DataFrame, url: str) -> None`

This function takes a DataFrame and posts it to a MongoDB API. It takes a URL for the API as an input.

### Todo

There are several todo items in the code for adding more functionality. These include adding input parameters for the payload to allow for different queries, scraping data for more than just San Diego County, bulk posting to the MongoDB API to load historical data, and posting to the API.

### Known Issues

- The original dataset has some double tabs, which can cause issues when using the Pandas library. The get_dataframe function addresses this issue by replacing double tabs with single tabs before processing the data.

- The payload is currently hardcoded, to change the payload you need to modify the payload variable in the code.

- This script is scraping data from a website, if the website format or structure changes, it may not work.
