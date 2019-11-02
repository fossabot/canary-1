import os
import utilities
import feathers
import silence
import math
from twilio.rest import Client
import time

# Initialise a list to hold the global variables
global_config = {

    'pollution_bucket': os.getenv("POLLUTION_QUERY_RESULTS_S3_BUCKET_NAME", None),
    'subscribers_bucket': os.getenv("SUBSCRIBERS_QUERY_RESULTS_S3_BUCKET_NAME", None),
    'logs_bucket': os.getenv("NOTIFICATION_LOGS_S3_BUCKET_NAME", None),

    'pollution_output_name': "./data/air-pollution-data.csv",
    'subscribers_output_name': "./data/air-pollution-subscribers.csv",

    'database': os.getenv("POLLUTION_DATABASE_NAME", None),

    'AWS_SERVER_PUBLIC_KEY_ATHENA': os.getenv("AWS_SERVER_PUBLIC_KEY_ATHENA", None),
    'AWS_SERVER_SECRET_KEY_ATHENA': os.getenv("AWS_SERVER_SECRET_KEY_ATHENA", None),
    'AWS_SERVER_PUBLIC_KEY_LOGS': os.getenv("AWS_SERVER_PUBLIC_KEY_LOGS", None),
    'AWS_SERVER_SECRET_KEY_LOGS': os.getenv("AWS_SERVER_SECRET_KEY_LOGS", None),
    'AWS_REGION': 'eu-west-2',

    'TWILIO_ACCOUNT_SID': os.getenv("TWILIO_ACCOUNT_ID", None),
    'TWILIO_AUTH_TOKEN': os.getenv("TWILIO_AUTH_TOKEN", None),

    'levels': ['green', 'yellow', 'amber', 'red'],
    'start_hour': 7,
    'end_hour': 21,
    'messages': {
        'green': 'There is no need to take any additional precautions.',
        'yellow': 'Avoid strenuous outdoor activity where possible and take precautions to avoid prolonged outdoor exposure.',
        'amber': 'Avoid all strenuous outdoor activity and limit outdoor exposure.',
        'red': 'Avoid all outdoor activity. Consider staying home.'
    }
}

# Create the AWS and Twilio clients
global_config['s3_athena'] = utilities.create_aws_client(
    client_type="s3",
    public_key=global_config["AWS_SERVER_PUBLIC_KEY_ATHENA"],
    secret_key=global_config["AWS_SERVER_SECRET_KEY_ATHENA"],
    region=global_config["AWS_REGION"])

global_config['athena'] = utilities.create_aws_client(
    client_type="athena",
    public_key=global_config["AWS_SERVER_PUBLIC_KEY_ATHENA"],
    secret_key=global_config["AWS_SERVER_SECRET_KEY_ATHENA"],
    region=global_config["AWS_REGION"])

global_config['s3_logs'] = utilities.create_aws_client(
    client_type="s3",
    public_key=global_config["AWS_SERVER_PUBLIC_KEY_LOGS"],
    secret_key=global_config["AWS_SERVER_SECRET_KEY_LOGS"],
    region=global_config["AWS_REGION"])

global_config['twilio'] = Client(
    global_config['TWILIO_ACCOUNT_SID'],
    global_config['TWILIO_AUTH_TOKEN'])

# Continuously run the code below
while True:
    output_bucket, output_file_path = feathers.generate_data_view(
        client=global_config['athena'],
        results_bucket=global_config['pollution_bucket'],
        database_name=global_config['database'],
        sql_query="SELECT * from airpollution",
        retry_time=60)

    feathers.fetch_data_view(
        s3=global_config['s3_athena'],
        bucket=output_bucket,
        file_path=output_file_path,
        output_path=global_config['pollution_output_name'])

    output_bucket, output_file_path = feathers.generate_data_view(
        client=global_config['athena'],
        results_bucket=global_config['subscribers_bucket'],
        database_name=global_config['database'],
        sql_query="""
        SELECT max(date_created) as last_message, phone, a.topic from 
        (
          SELECT lower(to_hex(md5(to_utf8(phone)))) as phone_hash, phone, subscribers.topic 
          FROM subscribers
        ) AS a 

        LEFT JOIN notificationlogs 

        ON a.phone_hash = notificationlogs.to 

        GROUP BY a.phone_hash, a.phone, a.topic
        """,
        retry_time=60)

    feathers.fetch_data_view(
        s3=global_config['s3_athena'],
        bucket=output_bucket,
        file_path=output_file_path,
        output_path=global_config['subscribers_output_name'])

    # Import the latest pollution data with a 60 second retry time, this is populated by the feathers application
    air_pollution_data = silence.import_data(
        file_path=global_config['pollution_output_name'],
        retry_time=60)

    # Import the latest subscriber data with a 60 second rety time, also populated by the feathers application
    subscriber_data = silence.import_data(
        file_path=global_config['subscribers_output_name'],
        retry_time=60)

    # Check which users are eligible for a notification based on past activity
    subscriber_data_eligible = silence.check_eligibility(
        subscriber_df_with_last_message=subscriber_data,
        start_hour=global_config['start_hour'],
        end_hour=global_config['end_hour'])

    # Get the average pollution levels per hour
    average_per_timestamp = silence.process_air_pollution_data(air_pollution_data)

    # Get the current pollution level & alert category
    current_level = round(average_per_timestamp.iloc[0]['air_quality_index (aqi)']['mean'], 2)
    level_category = math.floor(current_level / 50)
    print ('The current pollution level is {} which is at the {} level'.format(current_level, level_category))

    # Send notifications to the relevant subscribers
    messages = silence.send_notifications(
        topic=global_config['levels'][level_category],
        level=current_level,
        subscriber_df=subscriber_data_eligible,
        client=global_config['twilio'],
        messages=global_config['messages'],
        levels=global_config['levels'])

    # Save the messages to logs
    message_ids = silence.log_notifications_sent(
        s3=global_config['s3_logs'],
        bucket_name=global_config['logs_bucket'],
        message_logs=messages)

    # Print the ids of the messages sent
    print ('Messages succesfully sent')
    print (message_ids)

    # Wait an hour before running through the cycle again
    time.sleep(3600)