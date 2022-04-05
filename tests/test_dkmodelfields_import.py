# -*- coding: utf-8 -*-

"""Test that all modules are importable.
"""

import dkmodelfields
import dkmodelfields.adminforms
import dkmodelfields.adminforms.durationfield
import dkmodelfields.adminforms.monthfield
import dkmodelfields.adminforms.yearfield
import dkmodelfields.apps
import dkmodelfields.durationfield
import dkmodelfields.monthfield
import dkmodelfields.norway
import dkmodelfields.phonefield
import dkmodelfields.statusfield
import dkmodelfields.utils
import dkmodelfields.yearfield


def test_import_dkmodelfields():
    """Test that all modules are importable.
    """
    
    assert dkmodelfields
    assert dkmodelfields.adminforms
    assert dkmodelfields.adminforms.durationfield
    assert dkmodelfields.adminforms.monthfield
    assert dkmodelfields.adminforms.yearfield
    assert dkmodelfields.apps
    assert dkmodelfields.durationfield
    assert dkmodelfields.monthfield
    assert dkmodelfields.norway
    assert dkmodelfields.phonefield
    assert dkmodelfields.statusfield
    assert dkmodelfields.utils
    assert dkmodelfields.yearfield
