import logging
import os
import sys
from subprocess import DEVNULL, STDOUT, Popen
from time import sleep
from urllib.parse import urlparse

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from booker import config, metadata
from booker.io import read_jsonlines_s3
from booker.types import Reservation, User


class CheckingConnectionTask:
    def __init__(self):
        o = urlparse(config.SELENIUM_REMOTE_URL)
        host, port = o.netloc.split(":")
        self.host = host
        self.port = port
        self.is_connectable = False

    def __call__(self):
        retry = 10
        for _ in range(retry):
            if self._check_connection():
                self.is_connectable = True
                break
            logging.info("Sleeping.")
            sleep(1)
        else:
            logging.error(f"🚨 Failed to connect to {self.host}:{self.port}!")
            sys.exit(1)

    def _check_connection(self):
        process = Popen(
            ["nc", "-zv", self.host, self.port], stdout=DEVNULL, stderr=STDOUT
        )
        if process.wait() != 0:
            logging.warning(
                f"⛔ Unable to communicate with {self.host}:{self.port}."
            )
            return False
        else:
            logging.info(f"✅ Can communicate with {self.host}:{self.port}!")
            return True


class LoadingUserTask:
    def __init__(self):
        self.users = []

    def __call__(self):
        self.users = read_jsonlines_s3(config.USERS_FILE_PATH)


class ReservationTask:
    def __init__(self, user: User):
        self.user = user
        self.reservations = []

    def __call__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Remote(
            command_executor=config.SELENIUM_REMOTE_URL,
            desired_capabilities=options.to_capabilities(),
            options=options,
        )
        driver.set_window_size(1200, 900)
        self._start(driver)

    def _start(self, driver):
        # open reservation top page
        driver.get(config.RESERVATION_URL)

        date_elements = driver.find_elements(
            By.CSS_SELECTOR, metadata.CSS_SELECTOR
        )
        for date_element in date_elements:
            date = date_element.text
            if self._match_date_pattern(date):
                # click a date link
                date_element.click()

                # switch to date application page
                driver.switch_to.window(driver.window_handles[1])

                # reserve date if reservable
                if self._is_reservable(driver):
                    self._reserve(driver, date)

                # close date application form page
                driver.close()

                # switch to reservation top page
                driver.switch_to.window(driver.window_handles[0])

        driver.quit()

    def _match_date_pattern(self, date):
        date_pattern = self.user.date_pattern
        for pattern in date_pattern.split(","):
            if pattern in date:
                return True

    def _is_reservable(self, driver):
        return "エラー" not in driver.title

    def _reserve(self, driver, date):
        # fill kanji name form
        driver.find_element(
            By.XPATH, metadata.XPATH_NAME_KANJI_FORM
        ).send_keys(self.user.name_kanji)

        # fill kana name form
        driver.find_element(By.XPATH, metadata.XPATH_NAME_KANA_FORM).send_keys(
            self.user.name_kana
        )

        # fill telephone form
        driver.find_element(By.XPATH, metadata.XPATH_TELEPHONE_FORM).send_keys(
            self.user.telephone
        )

        # fill email form
        driver.find_element(By.XPATH, metadata.XPATH_EMAIL_FORM).send_keys(
            self.user.email
        )

        # fill email confirmation form
        driver.find_element(
            By.XPATH, metadata.XPATH_EMAIL_CONFIRMATION_FORM
        ).send_keys(self.user.email)

        # check time
        driver.find_element(
            By.XPATH, metadata.XPATH_CHECK_TIME_FORM
        ).send_keys(Keys.SPACE)

        # click confirmation button
        driver.find_element(
            By.XPATH, metadata.XPATH_CONFIRMATION_BUTTON
        ).click()

        # click apply button
        driver.find_element(By.XPATH, metadata.XPATH_APPLY_BUTTON).click()

        self._store_reservation(driver, date)

        self._save_screenshot(driver, date)

    def _store_reservation(self, driver, date):
        application_number, inquiry_number = driver.find_element(
            By.XPATH, metadata.XPATH_APPLICATION_NUMBERS
        ).text.split("\n")
        self.reservations.append(
            Reservation(
                user=self.user,
                reserved_date=date,
                application_number=application_number,
                inquiry_number=inquiry_number,
            )
        )

    def _save_screenshot(self, driver, date):
        w = driver.execute_script("return document.body.scrollWidth")
        h = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(w, h)
        driver.save_screenshot(f"{date}.png")


class NotificationTask:
    def __init__(self, reservations: list[Reservation]):
        self.reservations = reservations
        self.token = config.SLACK_TOKEN
        self.channel = config.SLACK_CHANNEL

    def __call__(self):
        for reservation in self.reservations:
            self._notify(reservation)

    def _notify(self, reservation):
        filename = f"{reservation.reserved_date}.png"
        comment = f"""予約が完了しました。
```
{reservation.application_number}
{reservation.inquiry_number}
利用日：{reservation.reserved_date}
```"""
        files = {"file": open(filename, "rb")}
        param = {
            "token": self.token,
            "channels": self.channel,
            "filename": filename,
            "initial_comment": comment,
            "title": filename,
        }
        requests.post(
            url="https://slack.com/api/files.upload",
            params=param,
            files=files,
        )
        os.remove(filename)
