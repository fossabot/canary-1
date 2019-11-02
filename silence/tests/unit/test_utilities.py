import unittest
from parameterized import parameterized
import utilities
import os


class TestFeathers(unittest.TestCase):

    @parameterized.expand([
        # Standard s3 client
        ["s3", "<class 'boto3.resources.factory.s3.ServiceResource'>"],
        # S# client type capitalised
        ["S3", "<class 'boto3.resources.factory.s3.ServiceResource'>"],
        # Standard athena client
        ["athena", "<class 'botocore.client.Athena'>"],
        # Athena client type capitalised awkwardly
        ["aTHEna", "<class 'botocore.client.Athena'>"]
    ])
    def test_create_aws_client_success(self, client_type, expected_outcome):

        aws_client = utilities.create_aws_client(
            client_type=client_type,
            public_key=None,
            secret_key=None,
            region=None
        )

        self.assertEqual(
            first=str(type(aws_client)),
            second=expected_outcome)


    @parameterized.expand([
        ["s9", KeyError]
    ])
    def test_create_aws_client_fail(self, client_type, expected_exception):

        with self.assertRaises(expected_exception):

            utilities.create_aws_client(
                client_type=client_type,
                public_key=None,
                secret_key=None,
                region=None
            )


    @parameterized.expand([
        # Delete a single file which exists
        [
            ["./data/test.txt"],
            ["./data/test.txt"],
            ["./data/test.txt"]
        ],
        # Delete a file which exists and ignore a file which does not exist
        [
            ["./data/test.txt", "./data/test_does_not_exist.json"],
            ["./data/test.txt"],
            ["./data/test.txt"]
        ],
        # Delete multiple files
        [
            ["./data/test.txt", "./data/test_does_exist.json"],
            ["./data/test.txt", "./data/test_does_exist.json"],
            ["./data/test.txt", "./data/test_does_exist.json"]
        ],
        # Delete no files as none exist
        [
            ["./data/test.txt", "./data/test_does_exist.json"],
            [],
            []
        ]
    ])
    def test_delete_files_success(self, file_paths, file_paths_to_seed, expected_outcome):

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
