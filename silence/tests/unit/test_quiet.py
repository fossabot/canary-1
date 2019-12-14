import unittest
from parameterized import parameterized
import pandas as pd
from datetime import datetime
import pytz
import quiet
import logging


class TestQuiet(unittest.TestCase):

    @staticmethod
    def mock_get_current_datetime_function() -> datetime:
        """
        This mocks the get_current_datetime function used to get the current datetime
        :return: datetime: A mocked datetime response
        """
        return datetime(year=2019, month=10, day=20, hour=10, tzinfo=pytz.UTC)


    class MockTwilioClient():

        def __init__(self):
            self.messages = self.Messages()

        class Messages:

            def create(self, from_, to, body):

                class Message:

                    def __init__(self, from_, to, body):

                        self._properties = {
                            "account_sid": "AC32281bfdbbce8a6d9088d64bde4a5fe6",
                            "api_version": "2010-04-01",
                            "body": body,
                            "date_created": datetime(year=2019, month=10, day=19, hour=21, minute=59, second=24, tzinfo=pytz.UTC),
                            "date_updated": datetime(year=2019, month=10, day=19, hour=21, minute=59, second=24, tzinfo=pytz.UTC),
                            "date_sent": None,
                            "direction": "outbound-api",
                            "error_code": None,
                            "error_message": None,
                            "from_": from_,
                            "messaging_service_sid": None,
                            "num_media": "0",
                            "num_segments": "2",
                            "price": None,
                            "price_unit": "USD",
                            "sid": "SM4b03fc56258a4784b695857b09aa0251",
                            "status": "queued",
                            "to" :'+44' + to[1:],
                            "uri": "/2010-04-01/Accounts/AC32281bfdbbce8a6d9088d64bde4a5fe6/Messages/SM4b03fc56258a4784b695857b09aa0251.json",
                            "subresource_uris": {
                                "media": "/2010-04-01/Accounts/AC32281bfdbbce8a6d9088d64bde4a5fe6/Messages/SM4b03fc56258a4784b695857b09aa0251/Media.json"
                            }
                        }

                return Message(from_, to, body)


    @parameterized.expand([
        [
            pd.DataFrame(
                data={
                    "average": [156.0],
                    "time": ["2019-04-17 20:00:00.000"],
                    "dt": ["2019-12-14-10-00-00"],
                    "count": [4]
                }
            ),
            (156.0, 3)
        ]
    ])
    def test_process_air_pollution_data(self, air_pollution_data, expected_outcome) -> None:
        """
        This tests that processing of the air pollution data works as expected
        :param pd.DataFrame air_pollution_data: The input raw air pollution data
        :param pd.DataFrame expected_outcome: The expected outcome
        :return: None
        """

        current_level, level_category = quiet.process_air_pollution_data(
            air_pollution_data=air_pollution_data)

        self.assertEqual(
            first=expected_outcome[0],
            second=current_level,
            msg="The current air pollution level is not as expected"
        )

        self.assertEqual(
            first=expected_outcome[1],
            second=level_category,
            msg="The current air pollution category is not as expected"
        )


    @parameterized.expand([
        # Tests that if a user hasn't received a message today and are inside the valid hours they are eligible
        [
            pd.DataFrame(
                data={
                    "last_message": ["2019-10-19 09:12:56.000"],
                    "phone": ["07719143007"],
                    "topic": ["yellow"]
                },
                index=[0]),
            8,
            20,
            pd.DataFrame(
                data={
                    "phone": ["07719143007"],
                    "topic": ["yellow"]
                },
                index=[0])
        ],
        # Tests that a user who has never been sent a message can be eligible
        [
            pd.DataFrame(
                data={
                    "last_message": ["2019-10-19 09:12:56.000", ""],
                    "phone": ["07719143007", "07719143008"],
                    "topic": ["yellow", "amber"]
                },
                index=[0, 1]),
            8,
            20,
            pd.DataFrame(
                data={
                    "phone": ["07719143007", "07719143008"],
                    "topic": ["yellow", "amber"]
                },
                index=[0, 1])
        ],
        # Tests that a user who has already seen a message is ineligible
        [
            pd.DataFrame(
                data={
                    "last_message": ["2019-10-20 09:12:56.000", ""],
                    "phone": ["07719143007", "07719143008"],
                    "topic": ["yellow", "amber"]
                },
                index=[0, 1]),
            8,
            20,
            pd.DataFrame(
                data={
                    "phone": ["07719143008"],
                    "topic": ["amber"]
                },
                index=[1])
        ],
        # Tests that no users are eligible during off limit hours
        [
            pd.DataFrame(
                data={
                    "last_message": ["2019-10-19 09:12:56.000", ""],
                    "phone": ["07719143007", "07719143008"],
                    "topic": ["yellow", "amber"]
                },
                index=[0, 1]),
            11,
            20,
            pd.DataFrame(columns=['phone', 'topic'])
        ]
    ])
    def test_check_eligibility(self, subscriber_df_with_last_message, start_hour, end_hour, expected_outcome) -> None:
        """
        This tests that the eligibility check for message works as expected
        :param subscriber_df_with_last_message:
        :param start_hour:
        :param end_hour:
        :param expected_outcome:
        :return: None
        """

        eligible_subscribers = quiet.check_eligibility(
            subscriber_df_with_last_message=subscriber_df_with_last_message,
            start_hour=start_hour,
            end_hour=end_hour,
            get_current_time_function=self.mock_get_current_datetime_function)

        self.assertTrue(
            expr=eligible_subscribers.equals(expected_outcome),
            msg="The output does not match the expected outcome"
        )

    @parameterized.expand([
        # Test single notification where level is appropriate for eligible subscriber
        [
            "yellow",
            52.33,
            pd.DataFrame(
                data={
                    "phone": ["07719143007"],
                    "topic": ["yellow"]
                },
                index=[0]
            ),
            {
                'green': 'There is no need to take any additional precautions.',
                'yellow': 'Avoid strenuous outdoor activity where possible and take precautions to avoid prolonged outdoor exposure.',
                'amber': 'Avoid all strenuous outdoor activity and limit outdoor exposure.',
                'red': 'Avoid all outdoor activity. Consider staying home.'
            },
            ['green', 'yellow', 'amber', 'red'],
            [
                {
                    "topic": "yellow",
                    "level": 52.33,
                    "topic_level": 1,
                    "account_sid": "AC32281bfdbbce8a6d9088d64bde4a5fe6",
                    "api_version": "2010-04-01",
                    "body": "The air pollution is currently at yellow levels, the current index level is 52.33. Avoid strenuous outdoor activity where possible and take precautions to avoid prolonged outdoor exposure.",
                    "date_created": datetime(year=2019, month=10, day=19, hour=21, minute=59, second=24, tzinfo=None),
                    "date_updated": datetime(year=2019, month=10, day=19, hour=21, minute=59, second=24, tzinfo=None),
                    "date_sent": None,
                    "direction": "outbound-api",
                    "error_code": None,
                    "error_message": None,
                    "from_": "+442033225373",
                    "messaging_service_sid": None,
                    "num_media": "0",
                    "num_segments": "2",
                    "price": None,
                    "price_unit": "USD",
                    "sid": "SM4b03fc56258a4784b695857b09aa0251",
                    "status": "queued",
                    "to": "66a9c4fd3349c4ebacd05e02b7222e78",
                    "uri": "/2010-04-01/Accounts/AC32281bfdbbce8a6d9088d64bde4a5fe6/Messages/SM4b03fc56258a4784b695857b09aa0251.json",
                    "subresource_uris.media": "/2010-04-01/Accounts/AC32281bfdbbce8a6d9088d64bde4a5fe6/Messages/SM4b03fc56258a4784b695857b09aa0251/Media.json"
                }
            ]
        ],
        # Test no notifications as level too low for eligible subscriber
        [
            "green",
            32.56,
            pd.DataFrame(
                data={
                    "phone": ["07719143007"],
                    "topic": ["yellow"]
                },
                index=[0]
            ),
            {
                'green': 'There is no need to take any additional precautions.',
                'yellow': 'Avoid strenuous outdoor activity where possible and take precautions to avoid prolonged outdoor exposure.',
                'amber': 'Avoid all strenuous outdoor activity and limit outdoor exposure.',
                'red': 'Avoid all outdoor activity. Consider staying home.'
            },
            ['green', 'yellow', 'amber', 'red'],
            [],
        ]
    ])
    def test_send_notifications(self, topic, level, subscriber_df, messages, levels, expected_outcome):


        client = self.MockTwilioClient()

        message_logs = quiet.send_notifications(
            topic=topic,
            level=level,
            subscriber_df=subscriber_df,
            client=client,
            messages=messages,
            levels=levels)

        self.assertEqual(
            first=message_logs.sort(),
            second=expected_outcome.sort()
        )


    def test_hash_phone_number(self):
        pass

    def test_log_notifications_sent(self):
        pass