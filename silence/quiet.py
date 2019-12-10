import time
import pandas as pd
import hashlib
from datetime import datetime
import pytz
import json


def import_data(file_path: str, retry_time: int):
    """
    This function imports data from a CSV file.

    :param str file_path: The path to the data csv file
    :param int retry_time: The time to wait in seconds before re-trying if
    the file import fails

    :return pd.DataFrame data: The dataframe containing the data
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

    :param pd.DataFrame air_pollution_data: The dataframe containing the
    latest air pollution data

    :return pd.DataFrame average_per_timestamp: The dataframe containing

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


def check_eligibility(subscriber_df_with_last_message, start_hour, end_hour, get_current_time_function=datetime.now):
    """
    This function checks when a user was last messaged to ensure that they are eligible to receive a notifictation.
    This prevents sending messages to frequently

    :param pd.DataFrame subscriber_df_with_last_message: The subscriber information including when they last
    received a message
    :param int start_hour: The hour to start sending notifications from e.g. 8 would be 8am in the morning
    :param int end_hour: The hour to stop sending notifications over e.g. 20 would be 10pm at night
    :param func get_current_time_function: The function to use to get the current time

    :return pd.DataFrame subscriber_data_eligible: The subscriber information
    """

    # Convert the last message time to a datetime
    subscriber_df_with_last_message['last_message'] = pd.to_datetime(
        subscriber_df_with_last_message['last_message'], yearfirst=True, utc=True)

    # Extract the day (that is the year, month, day combination) of the last message
    subscriber_df_with_last_message['day'] = subscriber_df_with_last_message['last_message'].apply(
        lambda x: x.strftime('%Y-%m-%d'))

    # Get the current time including the current day as above and the current hour
    current_time = get_current_time_function()
    day = current_time.strftime('%Y-%m-%d')
    hour = int(current_time.strftime('%H'))

    # If outside notification hours don't send a message and return an empty dataframe
    if hour < start_hour or hour > end_hour:
        return pd.DataFrame(columns=['phone', 'topic'])

    # If a message has already been sent today don't send another
    ineligible_subscribers = subscriber_df_with_last_message.index[
        subscriber_df_with_last_message['day'] == day].tolist()

    # Drop the ineligible subscribers
    subscriber_df_with_last_message.drop(inplace=True, index=ineligible_subscribers)
    subscriber_data_eligible = subscriber_df_with_last_message.loc[: ,['phone', 'topic']]

    return subscriber_data_eligible


def send_notifications(topic, level, subscriber_df, client, messages, levels):
    """
    This function sends a topic (alert level) and the current pollution level
    to the relevant subscribers.

    :param str topic: The current alert level (e.g. green, red, ambert etc.)
    :param str level: The current air quality index pollution level (e.g. 156)
    :param pd.DataFrame subscriber_df: The subscriber information
    :param Twilio.Client: The twilio client to use
    :param dict messages: The text of the messages to send
    :param list[str] levels: The available levels

    :return list[dict] message_logs: The details of each message which was sent
    """

    # Initialise a list to hold the message logs
    message_logs = []

    # Check that there are subscribers
    if len(subscriber_df) == 0:
        return message_logs

    # Construct the message body from the current
    message_body = 'The air pollution is currently at {} levels, the current index level is {}. {}'.format(
        topic, level, messages[topic])

    # Get the current topic level as an integer for ordinal comparison
    current_topic_level = levels.index(topic)
    # Get the subscription topics for all subscribers as an integer also
    subscriber_df['topic_level'] = subscriber_df['topic'].apply(lambda x: levels.index(x))
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

    :param: str phone_number: The phone number to create an MD5 hash of

    :return: str phone_hash: The MD5 hash of the phone number
    """

    # Create a hash from the phone number
    phone_hash = hashlib.md5(phone_number.encode('utf-8')).hexdigest()

    return phone_hash


def log_notifications_sent(s3, bucket_name, message_logs):
    """
    This function logs messages that have been sent by saving the details
    of each message to a bucket in S3.

    :param: boto3.resource s3: The boto3 S3 resource to use for interacting
    :param: str bucket_name: The bucket name in S3 to store the user information
    :param: list[dict] message_logs: The logs of the messages which have been created

    :return: list[str] message_ids: The sid of each message logged to S3
    """
    message_ids = []

    for message in message_logs:

        serialised_message = json.dumps(message, default=str)

        try:
            s3.Object(bucket_name, 'message-{}.json'.format(
                message['sid'])).put(Body=serialised_message)

            message_ids.append(message['sid'])
        except:
            pass

    return message_ids



