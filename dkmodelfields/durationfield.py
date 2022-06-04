"""
Based on https://github.com/johnpaulett/django-durationfield.
"""
# pylint:disable=R0904
import datetime
import sys

import ttcal
from django.db import models
from django.utils.encoding import smart_str, smart_text
from dkmodelfields.adminforms import DurationField as DurationFormField
from .creator import Creator


class DurationField(models.Field, Creator):
    """A duration field is used.
    """
    description = "A duration of time"

    def __init__(self, *args, **kwargs):
        super(DurationField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "DurationField"

    def db_type(self, connection):
        """Returns the database column data type for this field, for the
           provided connection. Django 1.1.X does not support multiple db's
           and therefore does not pass in the db connection string.
           Called by Django only when the framework constructs the table.
        """
        return "BIGINT"

    def get_prep_value(self, value):
        """Returns field's value prepared for interacting with the database
           backend. In our case this is an integer representing the number
           of seconds elapsed.
        """
        if value is None:
            return None  # db NULL
        if isinstance(value, int):
            value = ttcal.Duration(seconds=value)
        return value.toint()

    def get_db_prep_save(self, value, connection):
        return self.get_db_prep_value(value, connection=connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        """Returns field's value prepared for interacting with the database
           backend. In our case this is an integer representing the number
           of seconds elapsed.
        """
        if value is None:
            return None  # db NULL
        if isinstance(value, int):
            value = ttcal.Duration(seconds=value)
        return value.toint()

    def from_db_value(self, value, expression, connection, context):
        """Converts a value as returned by the database to a Python object.
           It is the reverse of get_prep_value().
        """
        return self.to_python(value)

    def to_python(self, value):
        """Converts the input ``value`` into the ttcal.Duration data type,
           raising ValueError if the data can't be converted. Returns
           the converted value as a ttcal.Duration instance.
        """

        # Note that value may be coming from the database column or
        # a serializer so we should handle a timedelta, string or an integer
        if value is None:
            return value

        if isinstance(value, ttcal.Duration):
            return value

        if isinstance(value, datetime.timedelta):
            return ttcal.Duration(value)

        if isinstance(value, int):
            return ttcal.Duration(seconds=value)

        if sys.version_info < (3,) and isinstance(value, long):  # pragma: nocover
            return ttcal.Duration(seconds=value)

        # Try to parse the value
        str_val = smart_str(value)
        if isinstance(str_val, str):
            try:
                return ttcal.Duration.parse(str_val)
            except ValueError:  # pragma: nocover
                raise ValueError(
                    "This value must be in 'w d h min s ms us' format, not:" +
                    repr(value)
                )

        raise ValueError("The value's type could not be converted")  # pragma: nocover

    def value_to_string(self, obj):
        "Serialize."
        value = self._get_val_from_obj(obj)
        return smart_text(value)

    def formfield(self, **kwargs):  # pylint:disable=W0221
        "Formfield declaration for admin site."
        defaults = {'form_class': DurationFormField}
        defaults.update(kwargs)
        return super(DurationField, self).formfield(**defaults)
