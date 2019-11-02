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

    client_mapping = {
        "s3": "resource",
        "athena": "client"
    }

    if client_type.lower() not in list(client_mapping.keys()):
        raise KeyError(f"No client setting specified for client_type of {client_type}. Please use one of {list(client_mapping.keys())}")
    else:
        client_type = client_type.lower()

    # Check if the environment variables exist, they are only required for external access
    if public_key is not None and secret_key is not None:

        session = boto3.Session(
            aws_access_key_id=public_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        return getattr(session, client_mapping[client_type])(client_type)

    # If no environment variables rely on a AWS role instead
    else:
        return getattr(boto3, client_mapping[client_type])(client_type)


def delete_files(file_paths: list) -> list:
    """
    Deletes all the provided files if they exist

    :param list[str] file_paths: The file paths to delete
    :return: list[str] deleted_files: The files that were deleted
    """
    deleted_files = []

    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted_files.append(file_path)

    return deleted_files

