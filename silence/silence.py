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
globals['levels'] = ['green', 'yellow', 'amber', 'red']

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
    This function imports the data.

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
    pollution level

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

    param (str) topic: The current alert level
    param (str) level: The current pollution level
    param (Pandas DataFrame) subscriber_df: The subscriber information
    param (str) account_sid: The twilio account id
    param (str) auth_token: The twilio authorisation token

    return (list [str]) message_ids: The ids of the messages that were sent
    """

    """
    # Send a WhatsApp message
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body='Your appointment is coming up on {} at {}'.format(topic, topic),
        to='whatsapp:+447719143007'
    )

    # Print tbe message id
    print(message.sid)
    """

    message_ids = []

    message_body = 'The air pollution has just reached {} levels the current level is {}'.format(
        topic, level)

    current_topic_level = globals['levels'].index(topic)

    subscriber_df['topic_level'] = subscriber_df['topic'].apply(lambda x: globals['levels'].index(x))

    relevant_subscribers = subscriber_df[subscriber_df['topic_level'] > current_topic_level]

    for subscriber_phone in relevant_subscribers['phone'].values:
        # Send an SMS message
        message = client.messages.create(
            from_='+442033225373',
            body=message_body,
            to=subscriber_phone
        )

        # Print the message id
        message_ids.append(message.sid)

    return message_ids

# Continuously run the code below
while True:
    # Import the latest pollution data with a 60 second retry time
    air_pollution_data = import_data(globals['air_pollution_file'], 60)
    subscriber_data = import_data(globals['subscriber_file'], 60)
    # Get the average pollution levels per hour
    average_per_timestamp = process_air_pollution_data(air_pollution_data)
    # Get the current pollution level
    current_level = round(average_per_timestamp.iloc[0]['air_quality_index (aqi)']['mean'], 2)
    # Get the alert category
    level_category = math.floor(current_level / 50)
    # Send notifications to the relevant subscribers
    send_notifications(
        topic=globals['levels'][level_category],
        level=current_level,
        subscriber_df=subscriber_data,
        client=twilio_client)
    # Wait an hour before running through the cycle again
    time.sleep(3600)
