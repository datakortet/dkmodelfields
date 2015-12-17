# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

import pytest
from django.db import connection

from dk.ttcal import Duration
from dkmodelfields import DurationField


def test_create():
    df = DurationField()
    assert df.description == 'A duration of time'


def test_get_internal_type():
    df = DurationField()
    df.get_internal_type() == 'DurationField'


def test_get_prep_value():
    df = DurationField()
    df.get_prep_value(60*60*2) == 'Duration(hours=2, minutes=0, seconds=0)'


def test_get_db_prep_save():
    df = DurationField()
    assert df.get_db_prep_save(Duration(hours=1, minutes=20), connection) == 60*80
    assert df.get_db_prep_save(60*80, connection) == Duration(hours=1, minutes=20).toint()
    assert df.get_db_prep_save(None, connection) == None


def test_to_python():
    df = DurationField()
    assert df.to_python(None) == None
    assert df.to_python(Duration(hours=1, minutes=40)) == Duration(hours=1, minutes=40)
    assert df.to_python(timedelta(hours=3, minutes=30)) == Duration(hours=3, minutes=30)
    assert df.to_python(60*60*3) == Duration(hours=3, minutes=0, seconds=0)
    assert df.to_python('2:20:0') == Duration(hours=2, minutes=20)


def test_formfield():
    df = DurationField()
    assert df.formfield().to_python('4:30') == Duration(hours=4, minutes=30)
