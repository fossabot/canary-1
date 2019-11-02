import unittest
from parameterized import parameterized
import uuid
import feathers


class MockS3Client:

    def __init__(self, failure_flag: bool, results_file: str):
        self.results_file = results_file
        self.request_counter = 0
        self.request_limit = 3
        self.failure = failure_flag
        self.ResultConfiguration = None
        self.QueryString = None
        self.ClientRequestToken = None
        self.QueryExecutionContext = None
        self.QueryExecutionId = None

    def start_query_execution(self, QueryString, ClientRequestToken, QueryExecutionContext, ResultConfiguration):

        self.ResultConfiguration = ResultConfiguration
        self.QueryString = QueryString
        self.ClientRequestToken = ClientRequestToken
        self.QueryExecutionContext = QueryExecutionContext
        self.QueryExecutionId = uuid.uuid4()

        response = {
            "QueryExecutionId": self.QueryExecutionId
        }

        return response

    def get_query_execution(self, QueryExecutionId):

        if QueryExecutionId != self.QueryExecutionId:
            raise ValueError("Execution IDs do not match!")

        self.request_counter += 1

        if self.request_counter >= self.request_limit and not self.failure:
            state = 'SUCCEEDED'
        elif self.failure:
            state = 'FAILED'
        else:
            state = 'RUNNING'

        response = {
            'QueryExecution': {
                'QueryExecutionId': self.QueryExecutionId,
                'Query': self.QueryString,
                'StatementType': None,
                'ResultConfiguration': {
                    'OutputLocation': self.ResultConfiguration["OutputLocation"] + "/" + self.results_file,
                    'EncryptionConfiguration': {
                        'EncryptionOption': self.ResultConfiguration["EncryptionConfiguration"]["EncryptionOption"],
                        'KmsKey': None
                    }
                },
                'QueryExecutionContext': {
                    'Database': self.QueryExecutionContext["Database"]
                },
                'Status': {
                    'State': state,
                    'StateChangeReason': None,
                    'SubmissionDateTime': None,
                    'CompletionDateTime': None
                },
                'Statistics': {
                    'EngineExecutionTimeInMillis': None,
                    'DataScannedInBytes': None,
                    'DataManifestLocation': None
                },
                'WorkGroup': None
            }
        }

        return response


class TestFeathers(unittest.TestCase):

    @parameterized.expand([
        [
            "Successful generation of the data view",
            MockS3Client(failure_flag=False, results_file="1241241_result.csv"),
            "airpollutionqueryresults",
            "AIRPOLLUTION",
            "select * from airpollution",
            2,
            [
                "airpollutionqueryresults",
                "1241241_result.csv"
            ]
        ]
    ])
    def test_generate_data_view_success(self, test_name, client, results_bucket, database_name, sql_query,
                                        retry_time, expected_outcome):

        output_bucket, output_file_path = feathers.generate_data_view(
            client=client,
            results_bucket=results_bucket,
            database_name=database_name,
            sql_query=sql_query,
            retry_time=retry_time
        )

        self.assertEqual(
            first=output_bucket,
            second=expected_outcome[0]
        )

        self.assertEqual(
            first=output_file_path,
            second=expected_outcome[1]
        )

    @parameterized.expand([
        [
            "Failed generation of the data view",
            MockS3Client(failure_flag=True, results_file="1241241_result.csv"),
            "airpollutionqueryresults",
            "AIRPOLLUTION",
            "select * from airpollution",
            2,
            Exception
        ]
    ])
    def test_generate_data_view_failure(self, test_name, client, results_bucket, database_name, sql_query,
                                        retry_time, expected_exception):

        with self.assertRaises(expected_exception):

            feathers.generate_data_view(
                client=client,
                results_bucket=results_bucket,
                database_name=database_name,
                sql_query=sql_query,
                retry_time=retry_time
            )


    def test_fetch_data_view(self):
        pass