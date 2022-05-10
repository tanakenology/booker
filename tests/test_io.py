from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from booker import io


class IoTestCase(TestCase):
    @patch("booker.io.json")
    @patch("booker.io.boto3")
    @patch("booker.io.urlparse")
    def test_read_jsonlines_s3(self, urlparse_mock, boto3_mock, json_mock):
        from types import GeneratorType

        path = MagicMock(spec=str)
        o = urlparse_mock.return_value
        s3 = boto3_mock.resource.return_value
        bucket = s3.Bucket.return_value
        obj = bucket.Object.return_value
        res = obj.get.return_value
        body = res["Body"].read.return_value.decode.return_value
        line_1, line_2 = MagicMock(), MagicMock()
        body.splitlines.return_value = [line_1, line_2]
        json_mock.loads.side_effect = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        expected = [{"a": 1, "b": 2}, {"c": 3, "d": 4}]

        actual = io.read_jsonlines_s3(path)

        self.assertIsInstance(actual, GeneratorType)
        self.assertEqual(list(actual), expected)
        urlparse_mock.assert_called_once_with(path)
        boto3_mock.resource.assert_called_once_with(o.scheme)
        s3.Bucket.assert_called_once_with(o.netloc)
        bucket.Object.assert_called_once_with(o.path[1:])
        obj.get.assert_called_once_with()
        res["Body"].read.assert_called_once_with()
        res["Body"].read.return_value.decode.assert_called_once_with("utf-8")
        body.splitlines.assert_called_once_with()
        json_mock.loads.assert_has_calls([call(line_1), call(line_2)])
