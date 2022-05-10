from unittest import TestCase
from unittest.mock import MagicMock, patch

from booker import config


class ConfigTestCase(TestCase):
    @patch("booker.config.boto3")
    def test_get_secret_when_secret_string(self, boto3_mock):
        secret_name = "booker"
        region_name = "ap-northeast-1"
        session = boto3_mock.session.Session.return_value
        client = session.client.return_value
        expected = MagicMock()
        client.get_secret_value.return_value = {"SecretString": expected}

        actual = config.get_secret()

        self.assertEqual(actual, expected)
        boto3_mock.session.Session.assert_called_once_with()
        session.client.assert_called_once_with(
            service_name="secretsmanager", region_name=region_name
        )
        client.get_secret_value.assert_called_once_with(SecretId=secret_name)

    @patch("booker.config.base64")
    @patch("booker.config.boto3")
    def test_get_secret_when_secret_binary(self, boto3_mock, base64_mock):
        secret_name = "booker"
        region_name = "ap-northeast-1"
        session = boto3_mock.session.Session.return_value
        client = session.client.return_value
        expected = MagicMock()
        client.get_secret_value.return_value = {"SecretBinary": expected}

        actual = config.get_secret()

        self.assertEqual(actual, base64_mock.b64decode.return_value)
        boto3_mock.session.Session.assert_called_once_with()
        session.client.assert_called_once_with(
            service_name="secretsmanager", region_name=region_name
        )
        client.get_secret_value.assert_called_once_with(SecretId=secret_name)
        base64_mock.b64decode.assert_called_once_with(expected)

    # TODO: add test for assertions about expected exceptions
