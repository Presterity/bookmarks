"""Tests for DateParser
"""

import datetime
import unittest

from bookmarks.dao.date_parser import DateParser, DateParseError


class DateParserTests(unittest.TestCase):

    def assert_success(self, date_str: str, expected_format: str, expected_date: datetime.datetime):
        date, date_format = DateParser.parse_date(date_str)
        self.assertEqual(date_format, expected_format)
        self.assertEqual(date, expected_date)

    def test_parse_date__Y(self):
        self.assert_success('1975', '%Y', datetime.datetime(1975, 1, 1))

    def test_parse_date__YM(self):
        self.assert_success('1985.03', '%Y.%m', datetime.datetime(1985, 3, 1))

    def test_parse_date__YMD(self):
        self.assert_success('1993.01.21', '%Y.%m.%d', datetime.datetime(1993, 1, 21))

    def test_parse_date__YMD_H(self):
        self.assert_success('2001.12.23 07', '%Y.%m.%d %H', datetime.datetime(2001, 12, 23, 7))

    def test_parse_date__YMD_HM(self):
        self.assert_success('2017.03.23 06:28', '%Y.%m.%d %H:%M', datetime.datetime(2017, 3, 23, 6, 28))

    def test_parse_date_invalid(self):
        with self.assertRaises(DateParseError):
            DateParser.parse_date('blarg')
