import ast
import base64
import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()


def get_secret():
    secret_name = "booker"
    region_name = "ap-northeast-1"

    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    else:
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(
                get_secret_value_response["SecretBinary"]
            )
    return secret


secret = ast.literal_eval(get_secret())


USERS_FILE_PATH = os.getenv("USERS_FILE_PATH") or secret["USERS_FILE_PATH"]
SELENIUM_REMOTE_URL = (
    os.getenv("SELENIUM_REMOTE_URL") or secret["SELENIUM_REMOTE_URL"]
)
RESERVATION_URL = os.getenv("RESERVATION_URL") or secret["RESERVATION_URL"]
SLACK_TOKEN = os.getenv("SLACK_TOKEN") or secret["SLACK_TOKEN"]
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL") or secret["SLACK_CHANNEL"]
