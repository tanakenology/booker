import locale

from booker.tasks import (
    CheckingConnectionTask,
    LoadingUserTask,
    NotificationTask,
    ReservationTask,
)
from booker.types import User

locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")


def main():
    checking_connection_task = CheckingConnectionTask()
    checking_connection_task()

    if checking_connection_task.is_connectable:
        loading_user_task = LoadingUserTask()
        loading_user_task()

        for user_kwargs in loading_user_task.users:
            do_tasks(user_kwargs)


def do_tasks(user_kwargs):
    user = User(**user_kwargs)

    reservation_task = ReservationTask(user)
    reservation_task()

    notification_task = NotificationTask(reservation_task.reservations)
    notification_task()
