# -*- coding: utf-8 -*-
import pytest
from django.db import connection
from dkmodelfields.statusfield import StatusField, StatusValue
from django.utils.translation import ugettext_lazy as _


def test_status_field():
    sf = StatusField(u"""
        @start-saleStatusdef
        =========== =================================== =======================
        status      verbose explanation (for web)       category
        =========== =================================== =======================
        new         Ordren er opprettet                 # [init]
        sale        Ordren er fakturert                 # [done]
        cancelled   Ordren er kansellert                # [done]
        error       Det har oppstått en feil            # [err]
        credit      Ordren er kreditert                 # [done]
        =========== =================================== =======================
        @end-saleStatusdef
    """)
    assert sf.description == _('Status field')
    assert sf.get_internal_type() == 'StatusField'
    assert sf.db_type(connection) == 'VARCHAR(9)'

    assert sf.to_python('sale').verbose == u'Ordren er fakturert'
    assert sf.to_python('') is None
    assert sf.to_python({'a': 42}) == {'a': 42}
    with pytest.raises(ValueError):
        sf.to_python('asdf')

    assert set(sf.get_prep_lookup('in', 'done')) == ({'cancelled', 'credit', 'sale'})
    sv = StatusValue(name='cancelled', verbose='Ordren er kansellert', categories=('done'))
    assert sf.get_prep_lookup('in', (sv,)) == ['cancelled']
    assert sf.get_prep_lookup('', 'init') == 'init'
    assert sf.get_prep_lookup('exact', 'init') == 'init'
