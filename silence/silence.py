import time
import pandas as pd
import requests
import math
import os
from twilio.rest import Client

"""
This file handles generating appropriate notifications from the latest air
pollution data
"""

# Initialise a list to hold the global variables
globals = {}

# Set the directory the the air pollution file
globals['air_pollution_file'] = "./data/air-pollution-data.csv"
globals['subscriber_file'] = "./data/air-pollution-subscribers.csv"

# Set the available air pollution levels and appropriate messages
globals['levels'] = ['green', 'yellow', 'amber', 'red']
globals['messages'] = {
    'green': 'There is no need to take any additional precautions.',
    'yellow': 'Avoid strenuous outdoor activity where possible and take precautions to avoid prolonged outdoor exposure.',
    'amber': 'Avoid all strenuous outdoor activity and limit outdoor exposure.',
    'red': 'Avoid all outdoor activity. Consider staying home.'
}

# Get the Twilio account id and authorisation token
globals['twilio_account_sid'] = os.getenv("TWILIO_ACCOUNT_ID", None)
globals['twilio_auth_token'] = os.getenv("TWILIO_AUTH_TOKEN", None)

# Create the client
twilio_client = Client(
    globals['twilio_account_sid'],
    globals['twilio_auth_token'])

# Import the data
def import_data(file_path, retry_time):
    """
    This function imports data from a CSV file.

    param (str) file_path: The path to the data csv file
    param (int) retry_time: The time to wait in seconds before re-trying if
    the file import fails

    return (Pandas DataFrame) data: The dataframe containing the data
    """

    # Keep running until the data is loaded
    while True:
        # Try and read the data from a CSV
        try:
            data = pd.read_csv(file_path)
            # If succesful break the loop
            break
        # If not succesful, assume file does not exist and wait out the retry_period
        except:
            print(
                'File does not exist yet, waiting {} secs before retrying'.format(
                    retry_time
                ))
            time.sleep(retry_time)

    # Return the air pollution data
    return data


def process_air_pollution_data(air_pollution_data):
    """
    This function processes the air pollution data to produce an hourly average
    pollution level.

    param (Pandas DataFrame) air_pollution_data: The dataframe containing the
    latest air pollution data

    returns (Pandas DataFrame) average_per_timestamp: The dataframe containing
    the average pollution levels per hour

    Assumptions:
    - Times are taken on the hour.
    - The average level changes hourly.
    - There is no more than one record for each city code per hour
    """

    # Remove missing air quality index values
    filled_index = air_pollution_data['air_quality_index (aqi)'].dropna('rows').index
    air_pollution_data = air_pollution_data.loc[filled_index]

    # Get the average air quality for each hour
    average_per_timestamp = air_pollution_data.groupby('time').agg({
        'air_quality_index (aqi)': ['mean', 'count', 'max', 'min']
    }).sort_index(ascending=False)

    return average_per_timestamp


def send_notifications(topic, level, subscriber_df, client):
    """
    This function sends a topic (alert level) and the current pollution level
    to the relevant subscribers.

    param (str) topic: The current alert level (e.g. green, red, ambert etc.)
    param (str) level: The current air quality index pollution level (e.g. 156)
    param (Pandas DataFrame) subscriber_df: The subscriber information
    param (Twilio Client) client: The twilio client to use

    return (list [str]) message_ids: The ids of the messages that were sent
    """

    # Initialise a list to hold the message ids
    message_ids = []

    # Construct the message body from the current
    message_body = 'The air pollution is currently at {} levels, the current index level is {}. {}'.format(
        topic, level, globals['messages'][topic])

    # Get the current topic level as an integer for ordinal comparison
    current_topic_level = globals['levels'].index(topic)
    # Get the subscription topics for all subscribers as an integer also
    subscriber_df['topic_level'] = subscriber_df['topic'].apply(lambda x: globals['levels'].index(x))
    # Identify the relevant subscribers who have a notification level less than or equal to the current level
    relevant_subscribers = subscriber_df[current_topic_level >= subscriber_df['topic_level']]

    # For each subscriber send a notification
    for subscriber_phone in relevant_subscribers['phone'].values:
        # Send an SMS message
        try:
            message = client.messages.create(
                from_='+442033225373',
                body=message_body,
                to=subscriber_phone
            )

            # Append the message id
            message_ids.append(message.sid)
        except:
            # Pass in the case of an error for now
            pass

    return message_ids

# Continuously run the code below
while True:
    # Import the latest pollution data with a 60 second retry time, this is populated by the feathers application
    air_pollution_data = import_data(globals['air_pollution_file'], 60)
    # Import the latest subscriber data with a 60 second rety time, also populated by the feathers application
    subscriber_data = import_data(globals['subscriber_file'], 60)
    # Get the average pollution levels per hour
    average_per_timestamp = process_air_pollution_data(air_pollution_data)
    # Get the current pollution level
    current_level = round(average_per_timestamp.iloc[0]['air_quality_index (aqi)']['mean'], 2)
    # Get the alert category
    level_category = math.floor(current_level / 50)
    print ('The current pollution level is {} which is at the {} level'.format(current_level, level_category))
    # Send notifications to the relevant subscribers
    messages = send_notifications(
        topic=globals['levels'][level_category],
        level=current_level,
        subscriber_df=subscriber_data,
        client=twilio_client)
    # Print the ids of the messages sent
    print (messages)
    # Wait an hour before running through the cycle again
    time.sleep(3600)
