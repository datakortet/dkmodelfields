# -*- coding: utf-8 -*-
import sys
from datetime import timedelta, datetime

import django
import pytest
import ttcal
from django.core.exceptions import ValidationError
from django.db import connection
from django.forms import Form
from ttcal import Duration
from dkmodelfields import DurationField
from dkmodelfields import adminforms


@pytest.fixture
def durationform():
    class DurationForm(Form):
        duration = adminforms.DurationField(label='Duration', required=False)
    return DurationForm


def test_formfield1():
    df = DurationField()
    assert isinstance(df.formfield(), adminforms.durationfield.DurationField)
    assert df.db_type(connection) == 'BIGINT'


def test_duration_form_field(durationform):
    f = durationform()
    assert str(f) == '''<tr><th><label for="id_duration">Duration:</label></th><td><input id="id_duration" name="duration" type="text" /></td></tr>'''


@pytest.mark.skipif(django.VERSION[:2] >= (1, 10), reason="field set to not required for dj19/110 test compatibility")
def test_duration_form_field_empty(durationform):
    f = durationform({'duration': u''})
    assert str(f) == '''<tr><th><label for="id_duration">Duration:</label></th><td><ul class="errorlist"><li>This field is required.</li></ul><input id="id_duration" name="duration" type="text" /></td></tr>'''


def test_duration_form_field_strval(durationform):
    f = durationform({'duration': u'2:20:00'})
    assert str(f) == '''<tr><th><label for="id_duration">Duration:</label></th><td><input id="id_duration" name="duration" type="text" value="2:20:00" /></td></tr>'''


def test_duration_form_field_duration_val(durationform):
    f = durationform({'duration': ttcal.Duration.parse(u'2:20:00')})
    assert str(f) == '''<tr><th><label for="id_duration">Duration:</label></th><td><ul class="errorlist"><li>Enter a valid duration.</li></ul><input id="id_duration" name="duration" type="text" /></td></tr>'''


def test_duration_form_field_invalid(durationform):
    f = durationform({'duration': u'asdf'})
    f.full_clean()
    assert f.clean() == {
        'duration': ttcal.Duration()
    }


def test_adminform_clean():
    df = adminforms.DurationField()
    with pytest.raises(ValidationError):
        assert df.clean(['3.14'])

    with pytest.raises(ValidationError):
        assert df.to_python(3.14)


def test_create():
    df = DurationField()
    assert df.description == 'A duration of time'
    assert df.db_type(connection) == 'BIGINT'


def test_get_internal_type():
    df = DurationField()
    assert df.get_internal_type() == 'DurationField'


def test_get_prep_value():
    df = DurationField()
    assert df.get_prep_value(None) is None
    assert df.get_prep_value(60*60*2) == Duration(hours=2, minutes=0, seconds=0).seconds


def test_get_db_prep_save():
    df = DurationField()
    assert df.get_db_prep_save(Duration(hours=1, minutes=20), connection) == 60*80
    assert df.get_db_prep_save(60*80, connection) == Duration(hours=1, minutes=20).toint()
    assert df.get_db_prep_save(None, connection) == None


def test_to_python():
    df = DurationField()
    assert df.to_python(None) is None
    assert df.to_python(Duration(hours=1, minutes=40)) == Duration(hours=1, minutes=40)
    assert df.to_python(timedelta(hours=3, minutes=30)) == Duration(hours=3, minutes=30)
    assert df.to_python(60*60*3) == Duration(hours=3, minutes=0, seconds=0)
    assert df.to_python('2:20:0') == Duration(hours=2, minutes=20)
    assert df.to_python('asdf') == Duration()
    if sys.version_info < (3,):
        assert df.to_python(long(687876)) == Duration(hours=191, minutes=4, seconds=36)


def test_formfield():
    df = DurationField()
    assert df.formfield().to_python('4:30') == Duration(hours=4, minutes=30)


def test_value_to_string():
    df = DurationField()
    assert df.value_to_string(None) == ''
