import unittest
import main
import logging
from parameterized import parameterized


class TestMain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.global_config = main.generate_config()
        cls.global_config = main.create_clients(cls.global_config)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logging.getLogger('boto3').setLevel(logging.CRITICAL)

    def test_main(self):
        main.send_notifications(self.global_config, notification_interval=0, retry_time=20)
