import time
import pandas as pd
import requests
import math
import boto3
import botocore
import os
import json
from twilio.rest import Client


"""
This file handles generating appropriate notifications from the latest air
pollution data
"""

# Initialise a list to hold the global variables
globals = {}

globals['bucket_name'] = "airpollutionnotificationlogs"
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


# Pass in the access credentials via environment variables
AWS_SERVER_PUBLIC_KEY = os.getenv("AWS_SERVER_PUBLIC_KEY", None)
AWS_SERVER_SECRET_KEY = os.getenv("AWS_SERVER_SECRET_KEY", None)

# Check if the environment variables exist, they are only required for external access
if AWS_SERVER_PUBLIC_KEY is not None and AWS_SERVER_SECRET_KEY is not None:

    session = boto3.Session(
        aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=AWS_SERVER_SECRET_KEY,
        region_name='eu-west-2'
    )

    globals['s3'] = session.resource('s3')

# If no environment variables rely on a AWS role instead
else:
    globals['s3'] = boto3.resource('s3')


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

    return (list [dict]) message_logs: The details of each message which was sent
    """

    # Initialise a list to hold the message logs
    message_logs = []

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

        # Create the details of the current message
        current_message = {}
        current_message['topic'] = topic
        current_message['level'] = level
        current_message['topic_level'] = current_topic_level

        # Create the current message in Twilio and send it
        message = client.messages.create(
            from_='+442033225373',
            body=message_body,
            to=subscriber_phone)

        # Update the details of the current message from the call to Twilio
        current_message_extra = vars(message)['_properties']
        current_message_extra['subresource_uris.media'] = current_message_extra['subresource_uris']['media']
        current_message_extra['to'] = hash_phone_number(current_message_extra['to'].replace('+44', '0'))
        current_message_extra['date_created'] = current_message_extra['date_created'].replace(tzinfo=None)
        current_message_extra['date_updated'] = current_message_extra['date_updated'].replace(tzinfo=None)
        del current_message_extra['subresource_uris']
        current_message.update(current_message_extra)

        # Append the message to the message logs
        message_logs.append(current_message)

    return message_logs


def hash_phone_number(phone_number):
    """
    This function creates an md5 hash of a phone number

    param: (str) phone_number: The phone number to create an MD5 hash of

    returns: (str) phone_hash: The MD5 hash of the phone number
    """

    # Create a hash from the phone number
    phone_hash = hashlib.md5(phone_number.encode('utf-8')).hexdigest()

    return phone_hash


def log_notifications_sent(s3, bucket_name, message_logs):
    """
    This function logs messages that have been sent by saving the details
    of each message to a bucket in S3.

    param: (boto3.resource) s3: The boto3 S3 resource to use for interacting
    with Amazon S3
    param: (str) bucket_name: The bucket name in S3 to store the user information
    param: (list[dict]) message_logs: The logs of the messages which have been created
    and sent

    returns: (list[str]) message_ids: The sid of each message logged to S3
    """
    message_ids = []

    for message in message_logs:

        serialised_message = json.dumps(message, default=str)

        s3.Object(bucket_name, 'message-{}.json'.format(
            message['sid'])).put(Body=serialised_message)

        message_ids.append(message['sid'])

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
    # Save the messages to logs
    message_ids = log_notifications_sent(
        s3=globals['s3'],
        bucket_name=globals['bucket_name'],
        message_logs=messages
    )
    # Print the ids of the messages sent
    print ('Messages succesfully sent')
    print (message_ids)
    # Wait an hour before running through the cycle again
    time.sleep(3600)
