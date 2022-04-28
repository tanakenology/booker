from unittest import TestCase
from unittest.mock import MagicMock, call, patch, mock_open

import pytest
from booker.tasks import (
    By,
    NotificationTask,
    Reservation,
    ReservationTask,
    User,
    config,
    metadata,
)


class ReservationTaskTestCase(TestCase):
    def test__init(self):
        user = MagicMock(spec=User)

        actual = ReservationTask(user)

        self.assertEqual(actual.user, user)
        self.assertEqual(actual.reservations, [])

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
        webdriver_mock.Remote.assert_called_once_with(
            command_executor="http://local.selenium:4444/wd/hub",
            desired_capabilities=options.to_capabilities.return_value,
            options=options,
        )
        driver.set_window_size.assert_called_once_with(1200, 900)
        start_mock.assert_called_once_with(driver)

    @patch("booker.tasks.ReservationTask._start")
    @patch("booker.tasks.webdriver")
    @patch("booker.tasks.config")
    def test_call_in_lambda(self, config_mock, webdriver_mock, start_mock):
        user = MagicMock(spec=User)
        config_mock.SELENIUM_REMOTE_URL = None
        options = webdriver_mock.ChromeOptions.return_value
        driver = webdriver_mock.Chrome.return_value

        sut = ReservationTask(user)
        actual = sut()

        self.assertIsNone(actual)
        options.add_argument.assert_has_calls(
            [call("--headless"), call("--no-sandbox")]
        )
        webdriver_mock.Chrome.assert_called_once_with(
            executable_path="/opt/chrome/chromedriver",
            options=options,
        )
        driver.set_window_size.assert_called_once_with(1200, 900)
        start_mock.assert_called_once_with(driver)

    @patch("booker.tasks.ReservationTask._reserve")
    @patch("booker.tasks.ReservationTask._is_reservable")
    @patch("booker.tasks.ReservationTask._match_date_pattern")
    @patch("booker.tasks.metadata")
    def test_start(
        self,
        metadata_mock,
        match_date_pattern_mock,
        is_reservable_mock,
        reserve_mock,
    ):
        user = MagicMock(spec=User)
        driver = MagicMock()
        metadata_mock.XPATH_DATE_LINKS = [
            "xpath_1",
            "xpath_2",
            "xpath_3",
        ]
        driver_find_element_side_effects = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]
        driver.find_element.side_effect = driver_find_element_side_effects
        match_date_pattern_mock.side_effect = [False, True, True]
        is_reservable_mock.side_effect = [True, True]

        sut = ReservationTask(user)
        actual = sut._start(driver)

        self.assertIsNone(actual)
        driver.find_element.assert_has_calls(
            [
                call(By.XPATH, "xpath_1"),
                call(By.XPATH, "xpath_2"),
                call(By.XPATH, "xpath_3"),
            ]
        )
        match_date_pattern_mock.assert_has_calls(
            [
                call(driver_find_element_side_effects[0].text),
                call(driver_find_element_side_effects[1].text),
                call(driver_find_element_side_effects[2].text),
            ]
        )
        driver_find_element_side_effects[1].click.assert_called_once_with()
        driver_find_element_side_effects[2].click.assert_called_once_with()
        driver.switch_to.window.assert_has_calls(
            [
                call(driver.window_handles[1]),
                call(driver.window_handles[0]),
                call(driver.window_handles[1]),
                call(driver.window_handles[0]),
            ]
        )
        is_reservable_mock.assert_has_calls([call(driver), call(driver)])
        reserve_mock.assert_has_calls(
            [
                call(driver, driver_find_element_side_effects[1].text),
                call(driver, driver_find_element_side_effects[2].text),
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

    def test_store_reservation(self):
        user = MagicMock(spec=User)
        driver = MagicMock()
        date = "5月4日（水・祝）"
        driver.find_element.return_value.text.split.return_value = [
            "a001",
            "i001",
        ]

        sut = ReservationTask(user)
        actual = sut._store_reservation(driver, date)

        self.assertIsNone(actual)
        driver.find_element.assert_called_once_with(
            By.XPATH, metadata.XPATH_APPLICATION_NUMBERS
        )
        sut.reservations[0] = Reservation(
            user=user,
            reserved_date=date,
            application_number="a001",
            inquiry_number="i001",
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
@patch("booker.tasks.config")
def test_match_date_pattern(config_mock, date):
    user = MagicMock(spec=User)
    config_mock.DATE_PATTERN = "（土,（日,祝）"
    expected = None
    for pattern in config_mock.DATE_PATTERN.split(","):
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
        )
        self.reservations = [
            Reservation(
                user=self.user,
                reserved_date="5月3日（火・祝）",
                application_number="a001",
                inquiry_number="i001",
            ),
            Reservation(
                user=self.user,
                reserved_date="5月4日（水・祝）",
                application_number="a002",
                inquiry_number="i002",
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
    def test_notify(self, requests_mock, os_mock):
        reservation = self.reservations[0]
        filename = f"{reservation.reserved_date}.png"
        comment = f"""
        予約が完了しました。```
        {reservation.application_number}
        {reservation.inquiry_number}
        利用日：{reservation.reserved_date}
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
        m.assert_called_once_with(filename, "rb")
        requests_mock.post.assert_called_once_with(
            url="https://slack.com/api/files.upload",
            params=param,
            files=files,
        )
        os_mock.remove.assert_called_once_with(filename)
