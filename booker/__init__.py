import locale

from booker import config, io
from booker.tasks import NotificationTask, ReservationTask
from booker.types import User

locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")


def main():
    users = io.read_jsonlines_s3(config.USERS_FILE_PATH)
    for user_kwargs in users:
        do_task(user_kwargs)


def do_task(user_kwargs):
    user = User(**user_kwargs)

    reservation_task = ReservationTask(user)
    reservation_task()

    notification_task = NotificationTask(reservation_task.reservations)
    notification_task()
