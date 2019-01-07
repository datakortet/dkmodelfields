# -*- coding: utf-8 -*-

"""A database field class that goes with ttcal.Year.
"""

# pylint:disable=R0904
# R0904 too many public methods

import datetime
from django.db import models, connection as cn
from django.core.exceptions import ValidationError
# from django.contrib.admin.filterspecs import FilterSpec
from django.utils.encoding import force_unicode

import ttcal
from dkmodelfields.adminforms import MonthField as MonthFormField

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter


class MonthField(models.Field):
    """MySQL date <-> ttcal.Month() mapping.
       Maps the month to the first day of the month.
    """

    __metaclass__ = models.SubfieldBase

    description = "A generic Month field"

    def __init__(self, *args, **kwargs):
        super(MonthField, self).__init__(*args, **kwargs)
        self.month_year_filter = True

    # # needed in Django 1.7 (? this is default implementation..)
    # def deconstruct(self):
    #     name, path, args, kwargs = super(MonthField, self).deconstruct()
    #     return name, path, args, kwargs

    def db_type(self, connection):
        return 'DATE'

    def get_prep_value(self, value):
        """Convert to a value usable as a paramter in a query.
        """
        if isinstance(value, (str, unicode)):
            return value

        if isinstance(value, ttcal.Month):
            return '%04d-%02d-01' % (value.year, value.month)

        if isinstance(value, list):
            return '%04d-%02d-01' % (value[0].year, value[0].month)

        return value

    def get_prep_lookup(self, lookup_type, value):
        """Convert to a value suitable for saving.
        """
        if lookup_type == 'year':
            if isinstance(value, ttcal.Year):
                value = value.year
            else:
                try:
                    value = int(value)
                except ValueError:
                    raise ValueError(
                        "The __year lookup type requires an integer argument")

            return cn.ops.year_lookup_bounds_for_date_field(value)

        if lookup_type == 'month':
            return [force_unicode(value)]

        return super(MonthField, self).get_prep_lookup(lookup_type, value)

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert to a value usable as a paramter in a query.
        """
        if isinstance(value, (str, unicode)):
            return value

        if isinstance(value, ttcal.Month):
            return '%04d-%02d-01' % (value.year, value.month)

        if isinstance(value, list):
            return '%04d-%02d-01' % (value[0].year, value[0].month)

        return value

    def get_db_prep_save(self, value, connection):
        """Convert to a value suitable for saving.
        """
        if isinstance(value, ttcal.Month):
            return '%04d-%02d-01' % (value.year, value.month)

        if isinstance(value, (str, unicode)):
            return value

        if isinstance(value, list):
            return '%04d-%02d-01' % (value[0].year, value[0].month)

        return value  # pragma: nocover

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        """Return value prepared for database lookup.
        """
        if lookup_type == 'year':
            try:
                if isinstance(value, ttcal.Year):
                    value = value.year
                elif isinstance(value, list) and len(value) > 0:
                    v = value[0]
                    if isinstance(v, datetime.date):
                        value = v.year
                    else:
                        date = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                        value = date.year
                value = int(value)
            except TypeError:
                raise ValueError(
                    "The __year lookup type does not understand " + repr(value)
                )

            return connection.ops.year_lookup_bounds_for_date_field(value)

        if lookup_type == 'month':
            return [force_unicode(value)]

        return super(MonthField, self).get_db_prep_lookup(
            lookup_type, value, connection=connection, prepared=prepared)

    def to_python(self, value):
        """Converts the input ``value`` into a ttcal.Month instance,
           raising ValueError if the data can't be converted. 
        """
        if not value:
            return None

        if isinstance(value, ttcal.Month):
            return value

        if isinstance(value, datetime.date):
            return ttcal.Month(value.year, value.month)

        if isinstance(value, (str, unicode)):
            return self._str_to_month(value)

        raise ValidationError("Value/month: %r, %r" % (value, type(value)))

    def _str_to_month(self, sval):  # pylint:disable=R0201
        # 2008-01
        if not sval.strip():
            return None  # pragma: nocover
        y = int(sval[:4])
        m = int(sval[5:7])
        return ttcal.Month(y, m)
        
    def value_to_string(self, obj):
        """Serialization.
        """
        val = self._get_val_from_obj(obj)
        if not val:
            return val
        return '%04d-%02d' % (val.year, val.month)

    def formfield(self, **kwargs):  # pylint:disable=W0221
        """Formfield declaration for admin site.
        """
        defaults = {'form_class': MonthFormField}
        defaults.update(kwargs)
        return super(MonthField, self).formfield(**defaults)


class MonthFieldYearSimpleFilter(SimpleListFilter):
    title = _(u'år')

    parameter_name = 'month_year'

    def lookups(self, request, model_admin):
        links = []
        months = model_admin.get_queryset(
            request
        ).distinct().order_by(
            'month'
        ).values('month')
        choices = [val['month'] for val in months]
        choices = [v for v in choices if v is not None]
        choices = set(m.year for m in choices)
        for val in sorted(choices):
            links.append((str(val), val))
        return links

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(month__year=self.value())
