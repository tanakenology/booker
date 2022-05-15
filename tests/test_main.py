from unittest import TestCase
from unittest.mock import MagicMock, call, patch

import booker


class BookerMainTestCase(TestCase):
    # @patch("booker.do_tasks")
    # @patch("booker.io.read_jsonlines_s3")
    # @patch("booker.config")
    # def test_main(
    #     self,
    #     config_mock,
    #     read_jsonlines_s3_mock,
    #     do_tasks_mock,
    # ):
    #     user_kwargs_1, user_kwargs_2 = MagicMock(), MagicMock()
    #     read_jsonlines_s3_mock.return_value = [user_kwargs_1, user_kwargs_2]

    #     actual = booker.main()

    #     self.assertIsNone(actual)
    #     read_jsonlines_s3_mock.assert_called_once_with(
    #         config_mock.USERS_FILE_PATH
    #     )
    #     do_tasks_mock.assert_has_calls(
    #         [call(user_kwargs_1), call(user_kwargs_2)]
    #     )

    @patch("booker.do_tasks")
    @patch("booker.LoadingUserTask")
    @patch("booker.CheckingConnectionTask")
    def test_main_checking_connection_true(
        self,
        checking_connection_task_mock,
        loading_user_task_mock,
        do_tasks_mock,
    ):
        checking_connection_task_mock.return_value.is_connectable = True
        user_kwargs_1, user_kwargs_2 = MagicMock(), MagicMock()
        loading_user_task_mock.return_value.users = [
            user_kwargs_1,
            user_kwargs_2,
        ]

        actual = booker.main()

        self.assertIsNone(actual)
        checking_connection_task_mock.assert_called_once_with()
        checking_connection_task_mock.return_value.assert_called_once_with()
        loading_user_task_mock.assert_called_once_with()
        loading_user_task_mock.return_value.assert_called_once_with()
        do_tasks_mock.assert_has_calls(
            [call(user_kwargs_1), call(user_kwargs_2)]
        )

    @patch("booker.CheckingConnectionTask")
    def test_main_checking_connection_false(
        self, checking_connection_task_mock
    ):
        checking_connection_task_mock.return_value.is_connectable = False

        actual = booker.main()

        self.assertIsNone(actual)
        checking_connection_task_mock.assert_called_once_with()
        checking_connection_task_mock.return_value.assert_called_once_with()

    @patch("booker.User")
    @patch("booker.ReservationTask")
    @patch("booker.NotificationTask")
    def test_do_tasks(
        self,
        notification_task_mock,
        reservation_task_mock,
        user_type_mock,
    ):
        user_kwargs = MagicMock()

        actual = booker.do_tasks(user_kwargs)

        self.assertIsNone(actual)
        user_type_mock.assert_called_once_with(**user_kwargs)
        reservation_task_mock.assert_called_once_with(
            user_type_mock.return_value
        )
        reservation_task_mock.return_value.assert_called_once_with()
        notification_task_mock.assert_called_once_with(
            reservation_task_mock.return_value.reservations
        )
        notification_task_mock.return_value.assert_called_once_with()
