from booker import metadata
from selenium.webdriver.common.keys import Keys

xpath_values = [
    [metadata.XPATH_NAME_KANJI_FORM, "潜行密用"],
    [metadata.XPATH_NAME_KANA_FORM, "センコウミツヨウ"],
    [metadata.XPATH_TELEPHONE_FORM, "012-345-6789"],
    [metadata.XPATH_EMAIL_FORM, "test@example.com"],
    [metadata.XPATH_EMAIL_CONFIRMATION_FORM, "test@example.com"],
    [metadata.XPATH_CHECK_TIME_FORM, Keys.SPACE],
]
