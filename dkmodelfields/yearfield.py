"""
A database field class that goes with ttcal.Year.
"""

# pylint:disable=R0904

import ttcal
from django.db import models
from dkmodelfields.adminforms import YearField as YearFormField
from .subclassing import SubfieldBase


class YearField(models.Field, metaclass=SubfieldBase):
    """MySQL YEAR(4) <-> ttcal.Year() mapping.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'YEAR(4)'

    def from_db_value(self, value, *args):
        """Converts a value as returned by the database to a Python object.
           It is the reverse of get_prep_value().
        """
        return self.to_python(value)

    def to_python(self, value):
        if not value:
            return None
        
        if isinstance(value, int):
            return ttcal.Year(value)

        return value

    def get_prep_value(self, value):
        if isinstance(value, int):
            return value

        if isinstance(value, ttcal.Year):
            return value.year

        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, int):
            return value

        if isinstance(value, ttcal.Year):
            return value.year

        return value

    def formfield(self, **kwargs):
        #print "formfield", kwargs
        defaults = {'form_class': YearFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def value_to_string(self, obj):
        "Serialization."
        if obj is None:
            return ""
        val = self.value_from_object(obj)
        return self.get_prep_value(val)
