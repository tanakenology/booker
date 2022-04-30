# import locale
import sys

from booker import parser
from booker.tasks import NotificationTask, ReservationTask
from booker.types import User

# locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")


def main():
    args = parser.parse_args(sys.argv[1:])

    user = User(
        name_kanji=args.name_kanji,
        name_kana=args.name_kana,
        telephone=args.telephone,
        email=args.email,
    )

    reservation_task = ReservationTask(user)
    reservation_task()

    notification_task = NotificationTask(reservation_task.reservations)
    notification_task()
