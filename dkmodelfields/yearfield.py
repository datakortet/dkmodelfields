# -*- coding: utf-8 -*-

"""A database field class that goes with ttcal.Year.
"""

# pylint:disable=R0904

from django.db import models
from dk import ttcal
from dkmodelfields.adminforms import YearField as YearFormField


class YearField(models.Field):
    """MySQL YEAR(4) <-> ttcal.Year() mapping.
    """

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(YearField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'YEAR(4)'

    def to_python(self, value):
        if not value:
            return None
        
        if isinstance(value, (int, long)):
            #print 'inthandler'
            return ttcal.Year(value)

        return value

    def get_prep_value(self, value):
        if isinstance(value, (int, long)):
            return value

        if isinstance(value, ttcal.Year):
            return value.year

        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, (int, long)):
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
        #print "value_to_string", repr(obj)
        val = self._get_val_from_obj(obj)
        return self.get_prep_value(val)


from south.modelsinspector import add_introspection_rules
add_introspection_rules(
    [],
    ["^dkmodelfields\.yearfield\.YearField"])
