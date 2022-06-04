"""
A database field class that goes with ttcal.Year.
"""

# pylint:disable=R0904

import ttcal
from django.db import models
from dkmodelfields.adminforms import YearField as YearFormField
from .creator import Creator


class YearField(models.Field, Creator):
    """MySQL YEAR(4) <-> ttcal.Year() mapping.
    """

    def __init__(self, *args, **kwargs):
        super(YearField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'YEAR(4)'

    def from_db_value(self, value, expression, connection, context):
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
        return super(YearField, self).formfield(**defaults)

    def value_to_string(self, obj):
        "Serialization."
        val = self._get_val_from_obj(obj)
        return self.get_prep_value(val)
