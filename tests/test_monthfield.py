# -*- coding: utf-8 -*-
import pytest
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import connection
from django.forms import Form
from django.test import RequestFactory
import ttcal
from dkmodelfields import MonthField
from dkmodelfields import adminforms
from dkmodelfields.monthfield import MonthFieldYearSimpleFilter
from testapp.models import M, AM


@pytest.fixture
def monthform():
    class MonthForm(Form):
        mnth = adminforms.MonthField(label='Month')
    return MonthForm


def test_formfield():
    mf = MonthField()
    assert isinstance(mf.formfield(), adminforms.monthfield.MonthField)
    assert mf.db_type(connection) == 'DATE'


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


def test_adminform_topython():
    mf = MonthField()
    with pytest.raises(ValidationError):
        mf.to_python(3.14)


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
    assert mf.get_prep_value({}) == {}


def test_get_prep_lookup():
    mf = MonthField()
    assert mf.get_prep_lookup('year', '2016') == [
        date(2016, 1, 1),
        date(2016, 12, 31)
    ]
    assert mf.get_prep_lookup('year', ttcal.Year(2016)) == [
        date(2016, 1, 1),
        date(2016, 12, 31)
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
    assert mf.get_db_prep_value({}, connection) == {}


def test_get_db_prep_lookup():
    mf = MonthField()
    assert mf.get_db_prep_lookup('year', '2016', connection) == [
        date(2016, 1, 1),
        date(2016, 12, 31)
    ]
    assert mf.get_db_prep_lookup('year', 2016, connection) == [
        date(2016, 1, 1),
        date(2016, 12, 31)
    ]

    assert mf.get_db_prep_lookup('year', ttcal.Year(2016), connection) == [
        date(2016, 1, 1),
        date(2016, 12, 31)
    ]
    assert mf.get_db_prep_lookup('year', [date(2017, 1, 1), date(2017, 12, 31)], connection) == [
        date(2017, 1, 1),
        date(2017, 12, 31)
    ]
    assert mf.get_db_prep_lookup('year', ['2017-01-01 0:00:00',
                                          '2017-12-31 0:00:00'], connection) == [
       date(2017, 1, 1),
       date(2017, 12, 31)
   ]
    assert mf.get_db_prep_lookup('month', ttcal.Month(2016, 4), connection) == [u'2016-04']

    assert mf.get_db_prep_lookup('gt', ttcal.Month(2016, 4), connection) == [u'2016-04-01']

    with pytest.raises(ValueError):
        mf.get_db_prep_lookup('year', (), connection)


def test_to_python():
    mf = MonthField()
    assert mf.to_python('') is None
    assert mf.to_python('2015-02-4') == ttcal.Month(2015, 2)
    assert mf.to_python(date(2016, 4, 2)) == ttcal.Month(2016, 4)
    assert mf.to_python(ttcal.Month(2015, 6)) == ttcal.Month(2015, 6)

    with pytest.raises(ValidationError):
        mf.to_python(5)


def test_get_db_prep_save():
    mf = MonthField()
    assert mf.get_db_prep_save('2016-04', None) == '2016-04'
    assert mf.get_db_prep_save(ttcal.Month(2016, 4), None) == '2016-04-01'
    day = date(2015, 6, 1)
    nextday = day + timedelta(days=1)
    assert mf.get_db_prep_save([day, nextday], None) == '2015-06-01'


def test_value_to_string():
    dec = ttcal.Month(2017, 12)
    m = M(month=dec)
    mf = M._meta.get_field('month')
    assert mf.value_to_string(None) == ''
    assert mf.value_to_string(m) == '2017-12'


def test_month_field_year_simple_filter(db):
    M.objects.all().delete()
    jan = ttcal.Month(2017, 1)
    M.objects.create(month=jan)
    feb = ttcal.Month(2017, 2)
    M.objects.create(month=feb)
    rf = RequestFactory()
    f = MonthFieldYearSimpleFilter(
        request=rf.get('/'),
        params=(),
        model=M,
        model_admin=AM(M, None)
    )
    assert f.parameter_name == 'month_year'
    assert f.lookups(rf.get('/'), AM(M, None)) == [
        ('2017', 2017)
    ]

    assert [jan, feb] == [m.month
                          for m in f.queryset(
                              rf.get('/?month_year=2017-01'), M.objects.all()
                          ).all()
                         ]

