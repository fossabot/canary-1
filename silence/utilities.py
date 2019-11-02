import boto3
import os


def create_aws_client(client_type: str, public_key: str = None, secret_key: str = None, region:
                      str = None):
    """
    Creates an AWS client of the specified type
    
    :param str client_type: The type of client to create e.g. s3
    :param str public_key: The public key to use with this client
    :param str secret_key: The secret key to use with this client
    :param str region: The AWS region to use with this client
    
    :return: The AWS client
    """
    # Check if the environment variables exist, they are only required for external access
    if public_key is not None and secret_key is not None:

        session = boto3.Session(
            aws_access_key_id=public_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        return session.resource(client_type)

    # If no environment variables rely on a AWS role instead
    else:
        return boto3.resource(client_type)


def delete_files(file_paths: list):

    for file_path in file_paths:
        os.remove(file_path)
