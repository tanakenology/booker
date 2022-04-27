from unittest import TestCase
from unittest.mock import patch

import booker


class BookerMainTestCase(TestCase):
    @patch("booker.User")
    @patch("booker.ReservationTask")
    @patch("booker.NotificationTask")
    @patch("booker.parser")
    def test_main(
        self,
        parser_mock,
        notification_task_mock,
        reservation_task_mock,
        user_type_mock,
    ):
        args = parser_mock.parse_args.return_value

        actual = booker.main()

        self.assertIsNone(actual)
        user_type_mock.assert_called_once_with(
            name_kanji=args.name_kanji,
            name_kana=args.name_kana,
            telephone=args.telephone,
            email=args.email,
        )
        reservation_task_mock.assert_called_once_with(
            user_type_mock.return_value
        )
        reservation_task_mock.return_value.assert_called_once_with()
        notification_task_mock.assert_called_once_with(
            reservation_task_mock.return_value.reservations
        )
        notification_task_mock.return_value.assert_called_once_with()
