# -*- coding: utf-8 -*-
import pytest
from django.core.exceptions import ValidationError

from dkmodelfields import TelefonField, GateField, PostnrField, PoststedField
from django.utils.translation import ugettext_lazy as _

#### TELEFON FIELD ####
def test_telefon_field():
    tf = TelefonField()
    assert tf.description == _("Phone number")


def test_tel_get_prep_value():
    tf = TelefonField()
    assert tf.get_prep_value("93420252") == "93420252"


def test_tel_validate():
    tf = TelefonField()
    assert tf.run_validators("93420252") == None
    assert tf.run_validators("93420252") == None

    with pytest.raises(ValidationError):
        assert not tf.run_validators("123456") == ValidationError
        assert not tf.run_validators("4793420252") == ValidationError


#### GATE FIELD ####
def test_gate_field():
    gf = GateField()
    assert gf.description == _("Norwegian street address field")


def test_gate_get_prep_value():
    gf = GateField()
    assert gf.get_prep_value("Storgata 5") == "Storgata 5"


def test_gate_validate():
    gf = GateField()
    assert gf.run_validators("Storgata 5") == None
    assert gf.run_validators("PB 3") == None

    with pytest.raises(ValidationError):
        assert not gf.run_validators("") == ValidationError
        assert not gf.run_validators(
            u"""Inni granskauen så langt gatenavn at man må skjemmes for å bo der
            """
        ) == ValidationError


#### POSTNR FIELD ####
def test_postnr_field():
    pf = PostnrField()
    assert pf.description == _("Norwegian zip code field")


def test_postnr_get_prep_value():
    pf = PostnrField()
    assert pf.get_prep_value("9900") == "9900"


def test_postnr_validate():
    pf = PostnrField()
    assert pf.run_validators("9900") == None
    assert pf.run_validators("7054") == None

    with pytest.raises(ValidationError):
        assert not pf.run_validators("78") == ValidationError

    with pytest.raises(TypeError):
        assert not pf.run_validators(874) == TypeError


#### POSTSTED FIELD ####
def test_poststed_field():
    pf = PoststedField()
    assert pf.description == _("Norwegian zip code name")


def test_poststed_get_prep_value():
    pf = PoststedField()
    assert pf.get_prep_value("Kirkenes") == "Kirkenes"


def test_poststed_validate():
    pf = PoststedField()
    assert pf.run_validators("Kirkenes") == None
    assert pf.run_validators("") == None

    with pytest.raises(ValidationError):
        assert not pf.run_validators("Tulliball sted ingen steds. Her der eller i utlandet.") == ValidationError

    with pytest.raises(TypeError):
        assert not pf.run_validators(9900) == TypeError
