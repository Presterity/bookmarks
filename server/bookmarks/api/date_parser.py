"""Parser for display dates. Primary use case is for requests to the bookmark manager REST API that modify bookmarks
 by specifying a display date.
"""
import datetime

from typing import Tuple


class DateParser(object):

    # TODO this probably belongs somewhere besides under api/

    _formats = [
        "%Y.%m.%d %H:%M",
        "%Y.%m.%d %H",
        "%Y.%m.%d",
        "%Y.%m",
        "%Y",
    ]

    @classmethod
    def parse_date(cls, display_date: str) -> Tuple[datetime.datetime, str]:
        """
        Parses a display date and returns that date in ISO format and its inferred display format.

        :param display_date: a date in display format. Valid formats are: YYYY, YYYY.mm, YYYY.mm.dd, YYYY.mm.dd HH,
        YYYY.mm.dd HH:MM
        :return: the parsed date as a datetime, and the inferred display format
        """
        for date_format in cls._formats:
            try:
                date = datetime.datetime.strptime(display_date, date_format)
                return date, date_format
            except ValueError:
                pass

        # no known formats match the string
        raise DateParseError(display_date)


class DateParseError(Exception):
    """Indicates that a date string couldn't be parsed."""

    def __init__(self, parse_str):
        msg = 'can\'t parse date from: "{0}"'.format(parse_str)
        super(DateParseError, self).__init__(msg)

