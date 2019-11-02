import unittest
from parameterized import parameterized
import utilities
import os
import botocore


class TestFeathers(unittest.TestCase):

    @parameterized.expand([
        [
            "Standard s3 client using credentials",
            "s3",
            "abc",
            "def",
            "eu-west-2",
            "<class 'boto3.resources.factory.s3.ServiceResource'>"
        ],
        [
            "Standard s3 client using credentials but with no region",
            "s3",
            "abc",
            "def",
            None,
            "<class 'boto3.resources.factory.s3.ServiceResource'>"
        ],
        [
            "Standard s3 client no credentials with a region",
            "s3",
            None,
            None,
            "eu-west-2",
            "<class 'boto3.resources.factory.s3.ServiceResource'>"
        ],
        [
            "Standard s3 client no credentials and no region",
            "s3",
            None,
            None,
            None,
            "<class 'boto3.resources.factory.s3.ServiceResource'>"
        ],
        [
            "Standard s3 client with capitalisation",
            "S3",
            "abc",
            "def",
            "eu-west-2",
            "<class 'boto3.resources.factory.s3.ServiceResource'>"
        ],
        [
            'Standard athena client with credentials',
            "athena",
            "abc",
            "def",
            "eu-west-2",
            "<class 'botocore.client.Athena'>"
        ],
        [
            "Standard athena client with no credentials",
            "athena",
            None,
            None,
            "eu-west-2",
            "<class 'botocore.client.Athena'>"
        ],
        [
            "Standard athena client with awkward capitalisation",
            "atHEnA",
            "abc",
            "def",
            "eu-west-2",
            "<class 'botocore.client.Athena'>"
        ]
    ])
    def test_create_aws_client_success(self, test_name, client_type, public_key, private_key, region, expected_outcome):

        aws_client = utilities.create_aws_client(
            client_type=client_type,
            public_key=public_key,
            secret_key=private_key,
            region=region
        )

        self.assertEqual(
            first=str(type(aws_client)),
            second=expected_outcome)


    @parameterized.expand([
        [
            "A client type which does not exist",
            "s9",
            None,
            None,
            None,
            KeyError
        ],
        [
            'Standard athena client with no credentials and no region',
            "athena",
            None,
            None,
            None,
            botocore.exceptions.NoRegionError
        ],
    ])
    def test_create_aws_client_fail(self, test_name, client_type, public_key, private_key, region, expected_exception):

        with self.assertRaises(expected_exception):

            utilities.create_aws_client(
                client_type=client_type,
                public_key=public_key,
                secret_key=private_key,
                region=region
            )


    @parameterized.expand([
        [
            "Delete a single file which exists",
            ["./data/test.txt"],
            ["./data/test.txt"],
            ["./data/test.txt"]
        ],
        [
            "Delete a file which exists and ignore a file which does not exist",
            ["./data/test.txt", "./data/test_does_not_exist.json"],
            ["./data/test.txt"],
            ["./data/test.txt"]
        ],
        [
            "Delete a file which exists and ignore a file which does not exist",
            ["./data/test.txt", "./data/test_does_exist.json"],
            ["./data/test.txt", "./data/test_does_exist.json"],
            ["./data/test.txt", "./data/test_does_exist.json"]
        ],
        [
            "Delete a file which exists and ignore a file which does not exist",
            ["./data/test.txt", "./data/test_does_exist.json"],
            [],
            []
        ]
    ])
    def test_delete_files_success(self, test_name, file_paths, file_paths_to_seed, expected_outcome):

        for file_path in file_paths_to_seed:

            with open(file_path, "w+") as f:
                f.write("This is a test file")

            if not os.path.exists(file_path):
                raise FileNotFoundError("Test file not created successfully")

        files_deleted = utilities.delete_files(file_paths)

        self.assertEqual(
            first=files_deleted,
            second=expected_outcome
        )
