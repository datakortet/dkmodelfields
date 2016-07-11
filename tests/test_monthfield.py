# -*- coding: utf-8 -*-
import pytest
from datetime import date, timedelta

from django.db import connection
from django.forms import Form

from dk import ttcal
from dkmodelfields import MonthField
from dkmodelfields import adminforms


@pytest.fixture
def monthform():
    class MonthForm(Form):
        mnth = adminforms.MonthField(label='Month')
    return MonthForm


def test_formfield():
    mf = MonthField()
    assert isinstance(mf.formfield(), adminforms.monthfield.MonthField)


def test_month_form_field(monthform):
    f = monthform()
    assert str(f) == '<tr>' \
                     '<th>' \
                     '<label for="id_mnth">Month:</label>' \
                     '</th>' \
                     '<td>' \
                     '<input id="id_mnth" name="mnth" type="month" />' \
                     '</td>' \
                     '</tr>'


def test_month_form_field_empty(monthform):
    f = monthform({'mnth': u''})
    assert str(f) == '<tr>' \
                     '<th>' \
                     '<label for="id_mnth">Month:</label>' \
                     '</th>' \
                     '<td>' \
                     '<ul class="errorlist">' \
                     '<li>This field is required.</li>' \
                     '</ul>' \
                     '<input id="id_mnth" name="mnth" type="month" />' \
                     '</td>' \
                     '</tr>'


def test_month_form_field_strval(monthform):
    f = monthform({'mnth': u'2016-07'})
    assert str(f) == \
        '<tr>' \
        '<th>' \
        '<label for="id_mnth">Month:</label>' \
        '</th>' \
        '<td>' \
        '<input id="id_mnth" name="mnth" type="month" value="2016-07" />' \
        '</td>' \
        '</tr>'


# def test_month_form_field_intval(monthform):
#     f = monthform({'mnth': 201607})
#     assert str(f) == \
#         '<tr>' \
#         '<th>' \
#         '<label for="id_mnth">Month:</label>' \
#         '</th>' \
#         '<td>' \
#         '<input id="id_mnth" name="mnth" type="month" value="2016-07" />' \
#         '</td>' \
#         '</tr>'


def test_create():
    mf = MonthField()
    assert mf.month_year_filter


def test_get_prep_value():
    mf = MonthField()
    assert mf.get_prep_value('2015-01-05') == '2015-01-05'
    assert mf.get_prep_value(ttcal.Month(2015, 6)) == '2015-06-01'
    day = date(2015, 6, 1)
    nextday = day + timedelta(days=1)
    assert mf.get_prep_value([day, nextday]) == '2015-06-01'


def test_get_prep_lookup():
    mf = MonthField()
    assert mf.get_prep_lookup('year', '2016') == [
        '2016-01-01',
        '2016-12-31 23:59:59.999999'
    ]
    assert mf.get_prep_lookup('year', ttcal.Year(2016)) == [
        '2016-01-01',
        '2016-12-31 23:59:59.999999'
    ]
    assert mf.get_prep_lookup('month', ttcal.Month(2016, 4)) == [u'2016-04']

    with pytest.raises(ValueError):
        mf.get_prep_lookup('year', 'XX')


def test_get_db_prep_value():
    mf = MonthField()
    assert mf.get_db_prep_value('2016-04', None) == '2016-04'
    assert mf.get_db_prep_value(ttcal.Month(2016, 4), None) == '2016-04-01'
    day = date(2015, 6, 1)
    nextday = day + timedelta(days=1)
    assert mf.get_db_prep_value([day, nextday], None) == '2015-06-01'


def test_get_db_prep_lookup():
    mf = MonthField()
    assert mf.get_db_prep_lookup('year', '2016', connection) == [
        '2016-01-01',
        '2016-12-31 23:59:59.999999'
    ]
    assert mf.get_db_prep_lookup('year', ttcal.Year(2016), connection) == [
        '2016-01-01',
        '2016-12-31 23:59:59.999999'
    ]
    assert mf.get_db_prep_lookup('month', ttcal.Month(2016, 4), connection) == [u'2016-04']

    with pytest.raises(ValueError):
        assert mf.get_db_prep_lookup('year', 'XX', None) == ValueError


def test_to_python():
    mf = MonthField()
    assert mf.to_python('') is None
    assert mf.to_python('2015-02-4') == ttcal.Month(2015, 2)
    assert mf.to_python(date(2016, 4, 2)) == ttcal.Month(2016, 4)
    assert mf.to_python(ttcal.Month(2015, 6)) == ttcal.Month(2015, 6)


def test_get_db_prep_save():
    mf = MonthField()
    assert mf.get_db_prep_save('2016-04', None) == '2016-04'
    assert mf.get_db_prep_save(ttcal.Month(2016, 4), None) == '2016-04-01'
    day = date(2015, 6, 1)
    nextday = day + timedelta(days=1)
    assert mf.get_db_prep_save([day, nextday], None) == '2015-06-01'


# def test_month_field_year_simple_filter():
#     filter = MonthFieldYearSimpleFilter()

