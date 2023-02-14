# Beach Monitoring Data Retriever

This code retrieves beach monitoring data from the California Water Boards website using the requests library. The data is returned in the form of an Excel file, and can be further processed using the provided helper functions.

### Usage

```python
if __name__ == "__main__":
  xls = get_xls() 
  df = get_dataframe(xls)
  print(df)
```

The `get_xls` function sends a GET request to the California Water Boards website and returns the data in the form of an Excel file. The `get_dataframe` function then converts the Excel file to a Pandas dataframe, which can be further processed.
### Helper Functions
```python
return_between_dates(df: pd.DataFrame, start_date: str, end_date: str)
```

This function filters the dataframe to only include rows between the given start and end dates. The dates must be in the format 'YYYY-MM-DD'.

***Example:***
```python
between = return_between_dates(df, '2023-01-15', '2023-01-25')
print(between)
```

### Known Issues

* The original dataset has some double tabs, which can cause issues when using the Pandas library. The get_dataframe function addresses this issue by replacing double tabs with single tabs before processing the data.

* The payload is hardcoded, to change the payload you need to change the payload variable.

* This script is scraping data from website, if website format or structure changed it may not work.

* It's not checking for the header of the website.
