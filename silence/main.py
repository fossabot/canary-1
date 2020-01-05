import os
import utilities
import feathers
import quiet
from twilio.rest import Client
import time
import logging
from datetime import datetime, timedelta
import json


def generate_config() -> dict:
    # Get the config settings from environment variables
    global_config = {

        # Bucket names
        'pollution_bucket': os.getenv("POLLUTION_QUERY_RESULTS_S3_BUCKET_NAME", None),
        'subscribers_bucket': os.getenv("SUBSCRIBERS_QUERY_RESULTS_S3_BUCKET_NAME", None),
        'logs_bucket': os.getenv("NOTIFICATION_LOGS_S3_BUCKET_NAME", None),

        # File names for database query results
        'pollution_output_name': os.getenv("POLLUTION_OUTPUT_NAME", None),
        'subscribers_output_name': os.getenv("SUBSCRIBERS_OUTPUT_NAME", None),

        # Database name
        'database': os.getenv("POLLUTION_DATABASE_NAME", None),

        # Credentials for access to AWS
        'AWS_SERVER_PUBLIC_KEY_ATHENA': os.getenv("AWS_SERVER_PUBLIC_KEY_ATHENA", None),
        'AWS_SERVER_SECRET_KEY_ATHENA': os.getenv("AWS_SERVER_SECRET_KEY_ATHENA", None),
        'AWS_SERVER_PUBLIC_KEY_LOGS': os.getenv("AWS_SERVER_PUBLIC_KEY_LOGS", None),
        'AWS_SERVER_SECRET_KEY_LOGS': os.getenv("AWS_SERVER_SECRET_KEY_LOGS", None),
        'AWS_REGION': os.getenv("AWS_REGION", None),

        # Credentials for Twilio
        'TWILIO_ACCOUNT_SID': os.getenv("TWILIO_ACCOUNT_ID", None),
        'TWILIO_AUTH_TOKEN': os.getenv("TWILIO_AUTH_TOKEN", None),
    }

    # Get the other config settings from a file
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notification_config.json')) as json_file:
        notification_config = json.load(json_file)
        global_config.update(notification_config)

    return global_config


def create_clients(global_config: dict) -> dict:
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

    return global_config


def send_notifications(global_config: dict, retry_time: int = 60, notification_interval: int = 3600) -> None:

    current_time = (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")

    output_bucket, output_file_path = feathers.generate_data_view(
        client=global_config['athena'],
        results_bucket=global_config['pollution_bucket'],
        database_name=global_config['database'],
        sql_query=f"""
        SELECT * FROM (
          SELECT 
          time, 
          dt, 
          avg("air_quality_index (aqi)") as "average", 
          count("air_quality_index (aqi)") as "count" 
          FROM airpollution 
          WHERE dt>='{current_time}' 
          GROUP BY time, dt 
          ORDER BY time DESC) 
        LIMIT 1;
        """,
        retry_time=retry_time)

    feathers.fetch_data_view(
        s3=global_config['s3_athena'],
        bucket=output_bucket,
        file_path=output_file_path,
        output_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), global_config['pollution_output_name']))

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
        retry_time=retry_time)

    feathers.fetch_data_view(
        s3=global_config['s3_athena'],
        bucket=output_bucket,
        file_path=output_file_path,
        output_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), global_config['subscribers_output_name']))

    # Import the latest pollution data with a 60 second retry time, this is populated by the feathers application
    air_pollution_data = quiet.import_data(
        file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), global_config['pollution_output_name']),
        retry_time=retry_time)

    # Import the latest subscriber data with a 60 second rety time, also populated by the feathers application
    subscriber_data = quiet.import_data(
        file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), global_config['subscribers_output_name']),
        retry_time=retry_time)

    utilities.delete_files(
        [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), global_config['pollution_output_name']),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), global_config['subscribers_output_name'])
        ]
    )

    # Check which users are eligible for a notification based on past activity
    subscriber_data_eligible = quiet.check_eligibility(
        subscriber_df_with_last_message=subscriber_data,
        start_hour=global_config['start_hour'],
        end_hour=global_config['end_hour'])

    # Get the current pollution level & alert category
    current_level, level_category = quiet.process_air_pollution_data(air_pollution_data)

    # Send notifications to the relevant subscribers
    messages = quiet.send_notifications(
        topic=global_config['levels'][level_category],
        level=current_level,
        subscriber_df=subscriber_data_eligible,
        client=global_config['twilio'],
        messages=global_config['messages'],
        levels=global_config['levels'])

    # Save the messages to logs
    message_ids = quiet.log_notifications_sent(
        s3=global_config['s3_logs'],
        bucket_name=global_config['logs_bucket'],
        message_logs=messages)

    # Print the ids of the messages sent
    logging.debug('Messages succesfully sent')
    logging.debug(str(message_ids))

    # Wait the notification interval
    time.sleep(notification_interval)
