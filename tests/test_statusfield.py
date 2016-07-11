# -*- coding: utf-8 -*-
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
    assert sf.to_python('sale').verbose == u'Ordren er fakturert'
    assert set(sf.get_prep_lookup('in', 'done')) == ({'cancelled', 'credit', 'sale'})
    sv = StatusValue(name='cancelled', verbose='Ordren er kansellert', categories=('done'))
    assert sf.get_prep_lookup('in', (sv,)) == ['cancelled']
    assert sf.get_prep_lookup('', 'init') == ({'init'})
