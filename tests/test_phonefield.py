# -*- coding: utf-8 -*-
import pytest
from django.core.exceptions import ValidationError

from dkmodelfields.phonefield import TelephoneField
from django.utils.translation import ugettext_lazy as _


def test_create_phonefield():
    pf = TelephoneField()
    assert pf.description == _("International phone number")


def test_get_prep_value():
    pf = TelephoneField()
    assert pf.get_prep_value("+47.93420252") == "+47.93420252"


def test_validate():
    pf = TelephoneField()
    assert pf.run_validators("+47.93420252") is None
    assert pf.run_validators("+010.1234567890") is None

    with pytest.raises(ValidationError):
        assert not pf.run_validators("1234")

    with pytest.raises(ValidationError):
        assert not pf.run_validators("93420252")
