from dataclasses import dataclass


@dataclass
class User:
    name_kanji: str
    name_kana: str
    telephone: str
    email: str


@dataclass
class Reservation:
    user: User
    reserved_date: str
    application_number: str
    inquiry_number: str
