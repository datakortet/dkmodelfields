# -*- coding: utf-8 -*-
import pytest
from django.db import connection
from django.forms import ChoiceField

from dkmodelfields.statusfield import StatusField, StatusValue
from django.utils.translation import ugettext_lazy as _
from testapp_dkmodelfields.models import S


def test_status_field():
    txt = u"""
        @start-saleStatusdef
        =========== =================================== =======================
        status      verbose explanation (for web)       category
        =========== =================================== =======================
        new         Ordren er opprettet                 # [init]
        sale        Ordren er fakturert                 # [done]
        cancelled   Ordren er kansellert                # [done]
        error       Det har oppstått en feil            # [err]
        credit      Ordren er kreditert                 # [done]
        foo         Bar, baz                            # [bar,baz]
        =========== =================================== =======================
        @end-saleStatusdef
    """
    sf = StatusField(txt)
    assert sf.description == _('Status field')
    assert sf.get_internal_type() == 'StatusField'
    assert sf.db_type(connection) == 'VARCHAR(9)'

    assert sf.to_python('sale').verbose == u'Ordren er fakturert'
    assert sf.to_python('') is None
    assert sf.to_python({'a': 42}) == {'a': 42}
    with pytest.raises(ValueError):
        sf.to_python('asdf')

    sd = sf.statusdef
    assert sd.category('sale') == u'done'
    assert sd.categories('sale') == [u'done']
    assert sd.categories('foo') == [u'bar', u'baz']
    assert sd.valid_status('sale')

    assert set(sf.get_prep_lookup('in', 'done')) == ({'cancelled', 'credit', 'sale'})
    assert set(sf.get_prep_lookup('in', 'new')) == ({'new'})
    assert set(sf.get_prep_lookup('in', ['new', 'err'])) == ({'new', 'error'})
    assert set(sf.get_prep_lookup('in', None)) == ({None})
    sv = StatusValue(name='cancelled', verbose='Ordren er kansellert', categories=('done', 'ready'))
    assert sv.__unicode__() == sv.name
    assert str(sv) == sv.name
    assert repr(sv).startswith('StatusValue(')

    assert sf.get_prep_lookup('in', (sv,)) == ['cancelled']
    assert sf.get_prep_lookup('', 'init') == 'init'
    assert sf.get_prep_lookup('exact', 'init') == 'init'

    assert sv.__json__()['name'] == 'cancelled'

    name, path, args, kwargs = sf.deconstruct()
    assert name is None
    # print "PATH:", path
    assert path == 'dkmodelfields.statusfield.StatusField'
    assert args == [txt]
    assert kwargs == dict(
        max_length=9,
        choices=[
            (u'new',         u'Ordren er opprettet'),
            (u'sale',        u'Ordren er fakturert'),
            (u'cancelled',   u'Ordren er kansellert'),
            (u'error',       u'Det har oppstått en feil'),
            (u'credit',      u'Ordren er kreditert'),
            (u'foo',         u'Bar, baz'),
        ]
    )

    assert isinstance(sf.formfield(), ChoiceField)


def test_s_model(db):
    s = S.objects.create()
    a = S.objects.get(id=s.id)
    assert isinstance(a.status, StatusValue)
    assert isinstance(s.status, StatusValue)
