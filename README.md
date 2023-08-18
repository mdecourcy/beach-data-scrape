# Water Quality Data Processor

This script fetches water quality data from the Beach Watch website, processes it, and then writes it into an InfluxDB database. The data spans from the year 2000 to the current year, though it can also fetch data for specific years. The script can be run with a "first-pass" argument which causes it to fetch and process data for all years since 2000.

## Getting Started

### Prerequisites

1. Python (version used in development was 3.11.4, but it should work with any 3.x version).
2. Python libraries: `io`, `json`, `requests`, `pandas`, `uuid`, `logging`, `os`, `argparse`, `datetime`, `dotenv`.

3. Environment variables (or `.env` file):

- `INFLUXDB_URL`: The InfluxDB server URL.
- `INFLUXDB_ORG`: The organization for the InfluxDB.
- `INFLUXDB_BUCKET`: The bucket where data will be stored in the InfluxDB.
- `INFLUXDB_TOKEN`: The authentication token for InfluxDB.

4. Access to the Beach Watch website.

### Installation

1. Clone the repository to your local machine: ```git clone https://github.com/mdecourcy/beach-data-scrape.git```

2. Navigate to the project directory: ```cd [project_directory]```

3. Install the required Python packages: ```pip install -r requirements.txt```

### Usage

To run the script for all years from 2000 to the current year: ```python script_name.py --first-pass```

To run the script for the current year: ```python script_name.py```

    
### Features

- Fetches water quality data in the form of an XLS file.
- Converts the XLS data to a pandas dataframe.
- Maps the column names to the desired format.
- Converts the dataframe data to line protocol, which is the format required for writing data to InfluxDB.
- Writes the data to an InfluxDB database.

### Logging

The script logs various information and error messages. Logs are written to a file named app.log.
Contributing

If you wish to contribute to this project, please create an issue first to discuss your intended changes. After that, you can create a pull request.
License

This project is open-source. Please refer to the LICENSE file for more details.

### Acknowledgements

- Thanks to the Beach Watch website for providing the data.
- Thanks to the InfluxDB community for their extensive documentation.

### Disclaimer

The script relies on the availability of the Beach Watch website and the format in which it provides data. If there are changes in the website's structure or the data format, the script may not function as expected.