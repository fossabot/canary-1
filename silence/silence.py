import time
import pandas as pd
import requests
import math

"""
This file handles generating appropriate notifications from the latest air
pollution data
"""

# Initialise a list to hold the global variables
globals = {}
# Set the directory the the air pollution file
globals['air_pollution_file'] = "./data/air-pollution-data.csv"
globals['levels'] = ['green', 'yellow', 'amber', 'red']

# Import the air pollution data
def import_air_pollution_data(file_path, retry_time):
    """

    str file_path: The path to the air pollution data csv file
    int retry_time: The time to wait before re-trying if the file import fails
    """

    while True:
        try:
            air_pollution_data = pd.read_csv(file_path)
            break
        except:
            print(
                'File does not exist yet, waiting {} secs before retrying'.format(
                    retry_time
                ))
            time.sleep(retry_time)

    return air_pollution_data


"""
Assumptions:
- Times are taken on the hour.
- The average level changes hourly.
- There is no more than one record for each city code per hour
"""

def process_air_pollution_data(air_pollution_data):

    # Remove missing air quality index values
    filled_index = air_pollution_data['air_quality_index (aqi)'].dropna('rows').index
    air_pollution_data = air_pollution_data.loc[filled_index]

    # Get the average air quality for each hour
    average_per_timestamp = air_pollution_data.groupby('time').agg({
        'air_quality_index (aqi)': ['mean', 'count', 'max', 'min']
    }).sort_index(ascending=False)

    return average_per_timestamp


def send_notifications(topics):
    """
    This function sends a topic based on the air pollution level
    """


while True:
    air_pollution_data = import_air_pollution_data(globals['air_pollution_file'], 60)
    average_per_timestamp = process_air_pollution_data(air_pollution_data)
    current_level = average_per_timestamp.iloc[0]['air_quality_index (aqi)']['mean']
    level_category = math.lower(current_level / 50)
    send_notifications(topics=globals['levels'][:level_category])
    time.sleep(3600)
