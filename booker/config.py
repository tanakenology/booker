import os

from dotenv import load_dotenv

load_dotenv()


USERS_FILE_PATH = os.getenv("USERS_FILE_PATH")
SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL")
RESERVATION_URL = os.getenv("RESERVATION_URL")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
