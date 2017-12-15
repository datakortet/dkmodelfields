# -*- coding: utf-8 -*-

"""Test to verify that all modules are importable.
"""
import dkmodelfields.apps
import dkmodelfields.adminforms.durationfield
import dkmodelfields.adminforms.monthfield
import dkmodelfields.adminforms.yearfield
import dkmodelfields.durationfield
import dkmodelfields.monthfield
import dkmodelfields.norway
import dkmodelfields.phonefield
import dkmodelfields.statusfield
import dkmodelfields.utils
import dkmodelfields.yearfield


def test_import():
    assert dkmodelfields.apps
    assert dkmodelfields.adminforms.durationfield
    assert dkmodelfields.adminforms.monthfield
    assert dkmodelfields.adminforms.yearfield
    assert dkmodelfields.durationfield
    assert dkmodelfields.monthfield
    assert dkmodelfields.norway
    assert dkmodelfields.phonefield
    assert dkmodelfields.statusfield
    assert dkmodelfields.utils
    assert dkmodelfields.yearfield
