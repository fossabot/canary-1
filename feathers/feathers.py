import boto3
import botocore
import os
import time

# Initialise and set the global variables
globals = {}
globals['bucket'] = "air-pollution-data"
globals['key'] = "air-pollution-data.csv"
globals['output_name'] = "data/air-pollution-data.csv"

# Pass in the access credentials via environment variables
AWS_SERVER_PUBLIC_KEY = os.getenv("AWS_SERVER_PUBLIC_KEY", None)
AWS_SERVER_SECRET_KEY = os.getenv("AWS_SERVER_SECRET_KEY", None)

# Check if the environment variables exist, they are only required for external access
if AWS_SERVER_PUBLIC_KEY is not None and AWS_SERVER_SECRET_KEY is not None:
    session = boto3.Session(
        aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=AWS_SERVER_SECRET_KEY,
    )
    s3 = session.resource('s3')

# If no environment variables rely on a AWS role instead
else:
    s3 = boto3.resource('s3')

while True:

    try:
        # Try and retrieve the file
        s3.Bucket(globals['bucket']).download_file(
            globals['key'], globals['output_name'])
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    # Update every hour
    time.sleep(3600)
