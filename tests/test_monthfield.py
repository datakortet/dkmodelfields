# -*- coding: utf-8 -*-
import pytest
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import connection
from django.forms import Form

from dk import ttcal
from dkmodelfields import MonthField
from dkmodelfields import adminforms
from dkmodelfields.monthfield import MonthFieldYearSimpleFilter


def test_create():
    mf = MonthField()
    assert mf.month_year_filter == True


def test_get_prep_value():
    mf = MonthField()
    assert mf.get_prep_value('2015-01-05') == '2015-01-05'
    assert mf.get_prep_value(ttcal.Month(2015, 6)) == '2015-06-01'
    day = date(2015, 6, 1)
    nextday = day + timedelta(days=1)
    assert mf.get_prep_value([day, nextday]) == '2015-06-01'


def test_get_prep_lookup():
    mf = MonthField()
    assert mf.get_prep_lookup('year', '2016') == ['2016-01-01 00:00:00', '2016-12-31 23:59:59.999999']
    assert mf.get_prep_lookup('year', ttcal.Year(2016)) == ['2016-01-01 00:00:00', '2016-12-31 23:59:59.999999']
    assert mf.get_prep_lookup('month', ttcal.Month(2016, 4)) == [u'2016-04']

    with pytest.raises(ValueError):
        mf.get_prep_lookup('year', 'XX') == ValueError


def test_get_db_prep_value():
    mf = MonthField()
    assert mf.get_db_prep_value('2016-04', None) == '2016-04'
    assert mf.get_db_prep_value(ttcal.Month(2016, 4), None) == '2016-04-01'
    day = date(2015, 6, 1)
    nextday = day + timedelta(days=1)
    assert mf.get_db_prep_value([day, nextday], None) == '2015-06-01'


def test_get_db_prep_lookup():
    mf = MonthField()
    assert mf.get_db_prep_lookup('year', '2016', connection) == ['2016-01-01 00:00:00', '2016-12-31 23:59:59.999999']
    assert mf.get_db_prep_lookup('year', ttcal.Year(2016), connection) == ['2016-01-01 00:00:00', '2016-12-31 23:59:59.999999']
    assert mf.get_db_prep_lookup('month', ttcal.Month(2016, 4), connection) == [u'2016-04']

    with pytest.raises(ValueError):
        mf.get_db_prep_lookup('year', 'XX', None) == ValueError


def test_to_python():
    mf = MonthField()
    assert mf.to_python('') == None
    assert mf.to_python('2015-02-4') == ttcal.Month(2015, 2)
    assert mf.to_python(date(2016, 4, 2)) == ttcal.Month(2016, 4)
    assert mf.to_python(ttcal.Month(2015, 6)) == ttcal.Month(2015, 6)

    with pytest.raises(ValidationError):
        form = Form()
        mf.to_python(form) == ValidationError


def test_get_db_prep_save():
    mf = MonthField()
    assert mf.get_db_prep_save('2016-04', None) == '2016-04'
    assert mf.get_db_prep_save(ttcal.Month(2016, 4), None) == '2016-04-01'
    day = date(2015, 6, 1)
    nextday = day + timedelta(days=1)
    assert mf.get_db_prep_save([day, nextday], None) == '2015-06-01'


def test_formfield():
    mf = MonthField()
    print "DIR: ", dir(mf.formfield())
    assert isinstance(mf.formfield(), adminforms.monthfield.MonthField)


# def test_month_field_year_simple_filter():
#     filter = MonthFieldYearSimpleFilter()

