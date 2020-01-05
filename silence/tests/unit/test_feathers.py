import unittest
from parameterized import parameterized
import uuid
import feathers
import logging


class MockAthenaClient:
    """
    This is a mock of the AWS Athena client
    """

    def __init__(self, failure_flag: bool, results_file: str) -> None:
        """

        :param bool failure_flag: Whether the query should succeed or fail
        :param str results_file: The name of the results file
        """
        self.results_file = results_file
        self.failure = failure_flag

        self.request_counter = 0  # To track the number of requests made
        self.request_limit = 3  # Hardcoded request limit before returning success or failure

        self.ResultConfiguration = None
        self.QueryString = None
        self.ClientRequestToken = None
        self.QueryExecutionContext = None
        self.QueryExecutionId = None

    def start_query_execution(self, QueryString: str, ClientRequestToken: str, QueryExecutionContext,
                              ResultConfiguration) -> dict:
        """
        Mocks starting the execution of a query

        :param str QueryString: The query string to execute
        :param str ClientRequestToken:
        :param QueryExecutionContext:
        :param ResultConfiguration:

        :return: dict response: The response from Athena in AWS
        """

        self.ResultConfiguration = ResultConfiguration
        self.QueryString = QueryString
        self.ClientRequestToken = ClientRequestToken
        self.QueryExecutionContext = QueryExecutionContext

        # The QueryExecutionId is a randomly generated unique id
        self.QueryExecutionId = uuid.uuid4()

        # The response object is a dictionary with the QueryExecutionId
        response = {
            "QueryExecutionId": self.QueryExecutionId
        }

        return response

    def get_query_execution(self, QueryExecutionId: str) -> dict:
        """
        Mocks checking on the status of a query being executed

        :param str QueryExecutionId: The unique QueryExecutionId for this query
        :return: dict response: The response from Athena in AWS
        """

        if QueryExecutionId != self.QueryExecutionId:
            raise ValueError("Execution IDs do not match!")

        self.request_counter += 1

        # Handles polling of the query to see if it has completed
        if self.request_counter >= self.request_limit and not self.failure:
            state = 'SUCCEEDED'
        elif self.failure:
            state = 'FAILED'
        else:
            state = 'RUNNING'

        # The response from Athena in AWS
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

    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logging.getLogger('botocore').setLevel(logging.CRITICAL)
        logging.getLogger('boto3').setLevel(logging.CRITICAL)

    @parameterized.expand([
        [
            "Successful generation of the data view",
            MockAthenaClient(failure_flag=False, results_file="1241241_result.csv"),
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
            MockAthenaClient(failure_flag=True, results_file="1241241_result.csv"),
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