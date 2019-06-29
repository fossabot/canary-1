import boto3
import botocore
import os
import time
import uuid

# Initialise and set the global variables
globals = {}
globals['bucket'] = "airpollutionlondon-queryresults"
globals['database'] = 'airpollutionlondon'
globals['output_name'] = "data/air-pollution-data.csv"

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
    globals['athena'] = session.client('athena')

# If no environment variables rely on a AWS role instead
else:
    globals['s3'] = boto3.resource('s3')
    globals['athena'] = boto3.client('athena')


def generate_data_view(client, results_bucket, database_name, sql_query, retry_time):
    """
    param (boto3.client) client: The Athena client
    param (str) results_bucket: The bucket to contain the Athena results
    param (str) database_name: The name of the database to execute the query against
    param (str) sql_query: The query to execute
    param (int) retry_time: The retry time in seconds to check that the query has succeeded

    returns (str) output_bucket: The bucket containing the output of the Athena query
    returns (str) output_file_path: The path of the output file from the Athena query
    """

    # Start a new execution query
    response = client.start_query_execution(
        # The SQL query statements to be executed.
        QueryString=sql_query,
        # A unique case-sensitive string used to ensure the request to create the query is idempotent
        ClientRequestToken=str(uuid.uuid4()),
        # The database within which the query executes.
        QueryExecutionContext={
            'Database': database_name
        },
        # Specifies information about where and how to save the results of the query execution.
        ResultConfiguration={
            'OutputLocation': 's3://{}'.format(results_bucket),
            'EncryptionConfiguration': {
                'EncryptionOption': 'SSE_S3'
            }
        }
    )

    # Get the id of the query
    query_id = response['QueryExecutionId']

    while True:
        # Check the status of the query's execution
        response = client.get_query_execution(
            QueryExecutionId=query_id
        )
        # Get the state and output details
        query_state = response['QueryExecution']['Status']['State']
        output_file_details = response['QueryExecution']['ResultConfiguration']['OutputLocation'].split('/')
        output_file_path = output_file_details[3]
        output_bucket = output_file_details[2]

        # If the query has succeeded break the loop
        if query_state == "SUCCEEDED":
            break

        # If it has not succeeded try again after the retry time
        time.sleep(retry_time)

    # Return the output bucket and file path
    return output_bucket, output_file_path


def fetch_data_view(s3, bucket, file_path, output_path, retry_time):
    """
    param (boto3.resource) s3: The s3 resource
    param (str) bucket: The bucket to retrieve the file from
    param (str) file_path: The path to the file to retrieve
    param (str) output_path: The path to save the file to
    param (int) retry_time: The time to take before retrying to get the file
    """

    while True:

        try:
            # Try and retrieve the file
            s3.Bucket(bucket).download_file(
                file_path, output_path)
            break
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise


while True:
    output_bucket, output_file_path = generate_data_view(
        client=globals['athena'],
        results_bucket=globals['bucket'],
        database_name=globals['database'],
        sql_query="SELECT * from airpollution",
        retry_time=60)

    fetch_data_view(
        s3=globals['s3'],
        bucket=output_bucket,
        file_path=output_file_path,
        output_path=globals['output_name'],
        retry_time=60)

    time.sleep(3600)
