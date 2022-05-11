import locale
import logging
import sys
from subprocess import DEVNULL, STDOUT, Popen
from time import sleep

from booker import config, io
from booker.tasks import NotificationTask, ReservationTask
from booker.types import User

locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")

HOST = "localhost"
PORT = 4444


def check_connection():
    process = Popen(
        ["nc", "-zv", HOST, str(PORT)], stdout=DEVNULL, stderr=STDOUT
    )
    if process.wait() != 0:
        logging.warning(f"⛔ Unable to communicate with {HOST}:{PORT}.")
        return False
    else:
        logging.info(f"✅ Can communicate with {HOST}:{PORT}!")
        return True


RETRY = 10


def main():
    for _ in range(RETRY):
        if check_connection():
            break
        logging.info("Sleeping.")
        sleep(1)
    else:
        logging.error(f"🚨 Failed to connect to {HOST}:{PORT}!")
        sys.exit(1)

    users = io.read_jsonlines_s3(config.USERS_FILE_PATH)
    for user_kwargs in users:
        do_task(user_kwargs)


def do_task(user_kwargs):
    user = User(**user_kwargs)

    reservation_task = ReservationTask(user)
    reservation_task()

    notification_task = NotificationTask(reservation_task.reservations)
    notification_task()
