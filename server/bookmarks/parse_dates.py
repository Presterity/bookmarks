# -*- coding: utf-8 -*-

import datetime
import unittest


FORMAT_YMD_HM = "%Y.%m.%d %H:%M"
FORMAT_YMD_H  = "%Y.%m.%d %H"
FORMAT_YMD    = "%Y.%m.%d"
FORMAT_YM     = "%Y.%m"
FORMAT_Y      = "%Y"

FORMATS = [
    FORMAT_YMD_HM,
    FORMAT_YMD_H,
    FORMAT_YMD,
    FORMAT_YM,
    FORMAT_Y,
]


def find_date_format(d: str) -> str:
    for f in FORMATS:
        try:
            dt = datetime.datetime.strptime(d, f)
            return f
        except ValueError:
            pass
    return None

