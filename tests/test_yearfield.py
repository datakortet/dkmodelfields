# -*- coding: utf-8 -*-
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from django.forms import Form

from dk import ttcal
from dkmodelfields import YearField
from dkmodelfields import adminforms
import datetime


@pytest.fixture
def yearform():
    class YearForm(Form):
        yr = adminforms.YearField(label="Year")
    return YearForm


def test_formfield():
    yf = YearField()
    assert isinstance(yf.formfield(), adminforms.yearfield.YearField)


def test_year_form_field(yearform):
    f = yearform()
    assert str(f) == \
        '<tr>' \
        '<th>' \
        '<label for="id_yr">Year:</label>' \
        '</th>' \
        '<td>' \
        '<input id="id_yr" name="yr" type="number" />' \
        '</td>' \
        '</tr>'


def test_year_form_str(yearform):
    f = yearform({'yr': u'2016'})
    assert str(f) == \
        '<tr>' \
        '<th>' \
        '<label for="id_yr">Year:</label>' \
        '</th>' \
        '<td>' \
        '<input id="id_yr" name="yr" type="number" value="2016" />' \
        '</td>' \
        '</tr>'


def test_year_form_int(yearform):
    f = yearform({'yr': 2016})
    assert str(f) == \
        '<tr>' \
        '<th>' \
        '<label for="id_yr">Year:</label>' \
        '</th>' \
        '<td>' \
        '<input id="id_yr" name="yr" type="number" value="2016" />' \
        '</td>' \
        '</tr>'


def test_create():
    yf = YearField()
    assert yf.db_type(connection) == 'YEAR(4)'


def test_get_prep_value():
    yf = YearField()
    assert yf.get_prep_value('2015-01-05') == '2015-01-05'
    assert yf.get_prep_value(ttcal.Year(2015)) == 2015
    day = date(2016, 6, 1)
    nextday = day + timedelta(days=1)
    assert yf.get_prep_value([day, nextday]) == [
        datetime.date(2016, 6, 1),
        datetime.date(2016, 6, 2)
    ]


def test_get_db_prep_value():
    yf = YearField()
    assert yf.get_db_prep_value(2016, connection) == 2016
    assert yf.get_db_prep_value(ttcal.Year(2015), connection) == 2015


def test_to_python():
    yf = YearField()
    assert yf.to_python('') is None
    assert yf.to_python('2015') == '2015'
    assert yf.to_python(2015) == ttcal.Year(2015)
