from unittest import TestCase

from booker import config, parser


class ParseArgsTestCase(TestCase):
    def test_parse_args_without_args(self):
        args = []

        actual = parser.parse_args(args)

        self.assertEqual(actual.name_kanji, config.NAME_KANJI)
        self.assertEqual(actual.name_kana, config.NAME_KANA)
        self.assertEqual(actual.telephone, config.TELEPHONE)
        self.assertEqual(actual.email, config.EMAIL)

    def test_parse_args_with_args(self):
        args = [
            "--name-kanji",
            "潜行密用",
            "--name-kana",
            "センコウミツヨウ",
            "--telephone",
            "012-345-6789",
            "--email",
            "test@example.com",
        ]

        actual = parser.parse_args(args)

        self.assertEqual(actual.name_kanji, "潜行密用")
        self.assertEqual(actual.name_kana, "センコウミツヨウ")
        self.assertEqual(actual.telephone, "012-345-6789")
        self.assertEqual(actual.email, "test@example.com")
