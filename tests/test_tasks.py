from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, call, mock_open, patch

import pytest
from booker.tasks import (
    By,
    CheckingConnectionTask,
    LoadingUserTask,
    NotificationTask,
    Reservation,
    ReservationTask,
    User,
    config,
    metadata,
)


class CheckingConnectionTaskTestCase(TestCase):
    @patch("booker.tasks.config")
    @patch("booker.tasks.urlparse")
    def test__init(self, urlparse_mock, config_mock):
        host, port = MagicMock(), MagicMock()
        urlparse_mock.return_value.netloc.split.return_value = [host, port]

        sut = CheckingConnectionTask()

        urlparse_mock.assert_called_once_with(config_mock.SELENIUM_REMOTE_URL)
        urlparse_mock.return_value.netloc.split.assert_called_once_with(":")
        self.assertEqual(sut.host, host)
        self.assertEqual(sut.port, port)
        self.assertEqual(sut.is_connectable, False)

    @patch("booker.tasks.sleep")
    @patch("booker.tasks.logging")
    @patch("booker.tasks.CheckingConnectionTask._check_connection")
    @patch("booker.tasks.config")
    def test__call_connectable(
        self, config_mock, check_connection_mock, logging_mock, sleep_mock
    ):
        config_mock.SELENIUM_REMOTE_URL = "http://local.selenium:4444/wd/hub"
        check_connection_mock.side_effect = [False, False, False, True]

        sut = CheckingConnectionTask()
        actual = sut()

        self.assertIsNone(actual)
        self.assertTrue(sut.is_connectable)
        logging_mock.info.assert_has_calls(
            [call("Sleeping."), call("Sleeping."), call("Sleeping.")]
        )
        sleep_mock.assert_has_calls([call(1), call(1), call(1)])

    @patch("booker.tasks.sys")
    @patch("booker.tasks.sleep")
    @patch("booker.tasks.logging")
    @patch("booker.tasks.CheckingConnectionTask._check_connection")
    @patch("booker.tasks.config")
    def test__call_not_connectable(
        self,
        config_mock,
        check_connection_mock,
        logging_mock,
        sleep_mock,
        sys_mock,
    ):
        config_mock.SELENIUM_REMOTE_URL = "http://local.selenium:4444/wd/hub"
        retry = 100
        check_connection_mock.side_effect = [False] * retry

        sut = CheckingConnectionTask()
        actual = sut()

        self.assertIsNone(actual)
        self.assertFalse(sut.is_connectable)
        logging_mock.info.assert_has_calls([call("Sleeping.")] * retry)
        sleep_mock.assert_has_calls([call(1)] * retry)
        logging_mock.error.assert_called_once_with(
            "🚨 Failed to connect to local.selenium:4444!"
        )
        sys_mock.exit.assert_called_once_with(1)

    @patch("booker.tasks.logging")
    @patch("booker.tasks.STDOUT")
    @patch("booker.tasks.DEVNULL")
    @patch("booker.tasks.Popen")
    @patch("booker.tasks.config")
    def test__check_connection_connectable(
        self, config_mock, Popen_mock, DEVNULL_mock, STDOUT_mock, logging_mock
    ):
        config_mock.SELENIUM_REMOTE_URL = "http://local.selenium:4444/wd/hub"
        Popen_mock.return_value.wait.return_value = 0

        sut = CheckingConnectionTask()
        actual = sut._check_connection()

        self.assertTrue(actual)
        Popen_mock.assert_called_once_with(
            ["nc", "-zv", sut.host, sut.port],
            stdout=DEVNULL_mock,
            stderr=STDOUT_mock,
        )
        Popen_mock.return_value.wait.assert_called_once_with()
        logging_mock.info.assert_called_once_with(
            f"✅ Can communicate with {sut.host}:{sut.port}!"
        )

    @patch("booker.tasks.logging")
    @patch("booker.tasks.STDOUT")
    @patch("booker.tasks.DEVNULL")
    @patch("booker.tasks.Popen")
    @patch("booker.tasks.config")
    def test__check_connection_not_connectable(
        self, config_mock, Popen_mock, DEVNULL_mock, STDOUT_mock, logging_mock
    ):
        config_mock.SELENIUM_REMOTE_URL = "http://local.selenium:4444/wd/hub"
        Popen_mock.return_value.wait.return_value = 1

        sut = CheckingConnectionTask()
        actual = sut._check_connection()

        self.assertFalse(actual)
        Popen_mock.assert_called_once_with(
            ["nc", "-zv", sut.host, sut.port],
            stdout=DEVNULL_mock,
            stderr=STDOUT_mock,
        )
        Popen_mock.return_value.wait.assert_called_once_with()
        logging_mock.warning.assert_called_once_with(
            f"⛔ Unable to communicate with {sut.host}:{sut.port}."
        )


class LoadingUserTaskTestCase(TestCase):
    def test__init(self):
        sut = LoadingUserTask()

        self.assertEqual(sut.users, [])

    @patch("booker.tasks.config")
    @patch("booker.tasks.read_jsonlines_s3")
    def test__call(self, read_jsonlines_s3_mock, config_mock):
        sut = LoadingUserTask()
        actual = sut()

        self.assertIsNone(actual)
        self.assertEqual(sut.users, read_jsonlines_s3_mock.return_value)
        read_jsonlines_s3_mock.assert_called_once_with(
            config_mock.USERS_FILE_PATH
        )


class ReservationTaskTestCase(TestCase):
    def test__init(self):
        user = MagicMock(spec=User)

        sut = ReservationTask(user)

        self.assertEqual(sut.user, user)
        self.assertEqual(sut.reservations, [])

    @patch("booker.tasks.ReservationTask._start")
    @patch("booker.tasks.webdriver")
    @patch("booker.tasks.config")
    def test__call(self, config_mock, webdriver_mock, start_mock):
        user = MagicMock(spec=User)
        config_mock.SELENIUM_REMOTE_URL = "http://local.selenium:4444/wd/hub"
        options = webdriver_mock.ChromeOptions.return_value
        driver = webdriver_mock.Remote.return_value

        sut = ReservationTask(user)
        actual = sut()

        self.assertIsNone(actual)
        options.add_argument.assert_has_calls(
            [
                call("--no-sandbox"),
                call("--disable-dev-shm-usage"),
            ]
        )
        webdriver_mock.Remote.assert_called_once_with(
            command_executor="http://local.selenium:4444/wd/hub",
            desired_capabilities=options.to_capabilities.return_value,
            options=options,
        )
        driver.set_window_size.assert_called_once_with(1200, 900)
        start_mock.assert_called_once_with(driver)

    @patch("booker.tasks.ReservationTask._reserve")
    @patch("booker.tasks.ReservationTask._is_reservable")
    @patch("booker.tasks.ReservationTask._match_date_pattern")
    def test_start(
        self,
        match_date_pattern_mock,
        is_reservable_mock,
        reserve_mock,
    ):
        user = MagicMock(spec=User)
        driver = MagicMock()
        driver_find_elements_return_value = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        driver.find_elements.return_value = driver_find_elements_return_value
        match_date_pattern_mock.side_effect = [False, True, True]
        is_reservable_mock.side_effect = [True, True]

        sut = ReservationTask(user)
        actual = sut._start(driver)

        self.assertIsNone(actual)
        driver.find_elements.assert_called_once_with(
            By.CSS_SELECTOR, metadata.CSS_SELECTOR
        )
        is_reservable_mock.assert_has_calls([call(driver), call(driver)])
        reserve_mock.assert_has_calls(
            [
                call(driver, driver_find_elements_return_value[1].text),
                call(driver, driver_find_elements_return_value[2].text),
            ]
        )
        driver.close.assert_has_calls([call(), call()])

    @patch("booker.tasks.ReservationTask._save_screenshot")
    @patch("booker.tasks.ReservationTask._store_reservation")
    def test_reserve(self, store_reservation_mock, save_screenshot_mock):
        from fixtures.tasks_reserve_fixtures import xpath_values

        user = MagicMock(spec=User)
        user.name_kanji = "潜行密用"
        user.name_kana = "センコウミツヨウ"
        user.telephone = "012-345-6789"
        user.email = "test@example.com"
        driver = MagicMock()
        date = "5月4日（水・祝）"

        sut = ReservationTask(user)
        actual = sut._reserve(driver, date)

        self.assertIsNone(actual)
        for xpath, value in xpath_values:
            driver.find_element.assert_has_calls([call(By.XPATH, xpath)])
            driver.find_element.return_value.send_keys.assert_has_calls(
                [call(value)]
            )
        driver.find_element.assert_has_calls(
            [call(By.XPATH, metadata.XPATH_CONFIRMATION_BUTTON)]
        )
        driver.find_element.return_value.click.assert_has_calls([call()])
        driver.find_element.assert_has_calls(
            [call(By.XPATH, metadata.XPATH_APPLY_BUTTON)]
        )
        driver.find_element.return_value.click.assert_has_calls([call()])
        store_reservation_mock.assert_called_once_with(driver, date)
        save_screenshot_mock.assert_called_once_with(driver, date)

    @patch("booker.tasks.ReservationTask._is_reservable")
    def test_reserve_same_user_error(self, is_reservable_mock):
        from fixtures.tasks_reserve_fixtures import xpath_values

        user = MagicMock(spec=User)
        user.name_kanji = "潜行密用"
        user.name_kana = "センコウミツヨウ"
        user.telephone = "012-345-6789"
        user.email = "test@example.com"
        driver = MagicMock()
        date = "5月4日（水・祝）"
        is_reservable_mock.return_value = False

        sut = ReservationTask(user)
        actual = sut._reserve(driver, date)

        self.assertIsNone(actual)
        for xpath, value in xpath_values:
            driver.find_element.assert_has_calls([call(By.XPATH, xpath)])
            driver.find_element.return_value.send_keys.assert_has_calls(
                [call(value)]
            )
        driver.find_element.assert_has_calls(
            [call(By.XPATH, metadata.XPATH_CONFIRMATION_BUTTON)]
        )
        driver.find_element.return_value.click.assert_has_calls([call()])
        driver.find_element.assert_has_calls(
            [call(By.XPATH, metadata.XPATH_APPLY_BUTTON)]
        )
        driver.find_element.return_value.click.assert_has_calls([call()])
        is_reservable_mock.assert_called_once_with(driver)

    def test_store_reservation(self):
        user = MagicMock(spec=User)
        driver = MagicMock()
        date = "5月4日（水・祝）"
        driver.find_element.return_value.text.split.return_value = [
            "到達番号：123_456_789_0123",
            "問合せ番号：AbCdEf",
        ]

        sut = ReservationTask(user)
        actual = sut._store_reservation(driver, date)

        self.assertIsNone(actual)
        driver.find_element.assert_called_once_with(
            By.XPATH, metadata.XPATH_APPLICATION_NUMBERS
        )
        self.assertEqual(
            sut.reservations[0],
            Reservation(
                user=user,
                reserved_date=date,
                application_number="123_456_789_0123",
                inquiry_number="AbCdEf",
            ),
        )

    def test_save_screenshot(self):
        user = MagicMock(spec=User)
        driver = MagicMock()
        date = "5月4日（水・祝）"
        driver.execute_script.side_effect = [1200, 900]

        sut = ReservationTask(user)
        actual = sut._save_screenshot(driver, date)

        driver.execute_script.assert_has_calls(
            [
                call("return document.body.scrollWidth"),
                call("return document.body.scrollHeight"),
            ]
        )
        driver.set_window_size.assert_called_once_with(1200, 900)
        driver.save_screenshot.assert_called_once_with(f"{date}.png")


@pytest.mark.parametrize(
    "date",
    ["5月5日（木・祝）", "5月6日（金）", "5月7日（土）"],
)
def test_match_date_pattern(date):
    user = MagicMock(spec=User)
    user.date_pattern = "（土,（日,祝）"
    expected = None
    for pattern in user.date_pattern.split(","):
        if pattern in date:
            expected = True
            break

    sut = ReservationTask(user)
    actual = sut._match_date_pattern(date)

    assert actual == expected


@pytest.mark.parametrize(
    "title",
    ["申込みページ", "エラーページ"],
)
def test_is_reservable(title):
    user = MagicMock(spec=User)
    driver = MagicMock()
    driver.title = title

    sut = ReservationTask(user)
    actual = sut._is_reservable(driver)

    if "エラー" in title:
        assert not actual
    else:
        assert actual


class NotificationTaskTestCase(TestCase):
    def setUp(self):
        self.user = User(
            name_kanji="潜行密用",
            name_kana="センコウミツヨウ",
            telephone="012-345-6789",
            email="test@example.com",
            date_pattern="（土,（日,祝）",
        )
        self.reservations = [
            Reservation(
                user=self.user,
                reserved_date="5月3日（火・祝）",
                application_number="123_456_789_0001",
                inquiry_number="AbCdEf",
            ),
            Reservation(
                user=self.user,
                reserved_date="5月4日（水・祝）",
                application_number="123_456_789_0002",
                inquiry_number="GhIjKl",
            ),
        ]

    def test__init(self):
        sut = NotificationTask(self.reservations)

        self.assertEqual(sut.reservations, self.reservations)
        self.assertEqual(sut.token, config.SLACK_TOKEN)
        self.assertEqual(sut.channel, config.SLACK_CHANNEL)

    @patch("booker.tasks.NotificationTask._notify")
    def test__call(self, notify_mock):
        sut = NotificationTask(self.reservations)
        actual = sut()

        self.assertIsNone(actual)
        notify_mock.assert_has_calls(
            [
                call(self.reservations[0]),
                call(self.reservations[1]),
            ]
        )

    @patch("booker.tasks.os")
    @patch("booker.tasks.requests")
    @patch("booker.tasks.datetime")
    def test_notify(self, datetime_mock, requests_mock, os_mock):
        reservation = self.reservations[0]
        filename = f"{reservation.reserved_date}.png"
        comment = f"""予約が完了しました。
```
到達日時：
  {datetime_mock.now.return_value.strftime.return_value}
到達番号：
  {reservation.application_number}
問い合わせ番号：
  {reservation.inquiry_number}
申込内容：
お名前:
  {reservation.user.name_kanji}
お名前(フリガナ):
  {reservation.user.name_kana}
電話番号:
  {reservation.user.telephone}
メールアドレス:
  {reservation.user.email}
来館利用日時 :
  {reservation.reserved_date} 14:00-17:30
```"""
        m = mock_open()
        files = {"file": m.return_value}

        sut = NotificationTask(self.reservations)
        param = {
            "token": sut.token,
            "channels": sut.channel,
            "filename": filename,
            "initial_comment": comment,
            "title": filename,
        }
        with patch("builtins.open", m):
            actual = sut._notify(reservation)

        self.assertIsNone(actual)
        datetime_mock.now.return_value.strftime.assert_called_once_with(
            "%Y年%m月%d日 %H時%M分"
        )
        m.assert_called_once_with(filename, "rb")
        requests_mock.post.assert_called_once_with(
            url="https://slack.com/api/files.upload",
            params=param,
            files=files,
        )
        os_mock.remove.assert_called_once_with(filename)
