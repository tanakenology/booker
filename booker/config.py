import os

from dotenv import load_dotenv

load_dotenv()


SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL")
RESERVATION_URL = os.getenv("RESERVATION_URL")
DATE_PATTERN = os.getenv("DATE_PATTERN")
NAME_KANJI = os.getenv("NAME_KANJI")
NAME_KANA = os.getenv("NAME_KANA")
TELEPHONE = os.getenv("TELEPHONE")
EMAIL = os.getenv("EMAIL")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
