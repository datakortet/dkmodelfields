# -*- coding: utf-8 -*-
from datetime import timedelta
from dkmodelfields.utils import xstr_to_timedelta


def test_xstr_to_timedelta():
    assert xstr_to_timedelta("1 day, 00:00:00") == timedelta(days=1)
    assert xstr_to_timedelta("") is None
