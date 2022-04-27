import argparse

from booker import config


def parse_args(args: list):
    parser = argparse.ArgumentParser()
    parser.add_argument("--name-kanji", type=str, default=config.NAME_KANJI)
    parser.add_argument("--name-kana", type=str, default=config.NAME_KANA)
    parser.add_argument("--telephone", type=str, default=config.TELEPHONE)
    parser.add_argument("--email", type=str, default=config.EMAIL)
    return parser.parse_args(args)
