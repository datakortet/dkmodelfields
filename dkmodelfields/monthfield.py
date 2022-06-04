"""
A database field class that goes with ttcal.Year.
"""

import datetime

import ttcal
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ValidationError
from django.db import models, connection as cn
from django.db.models import Transform, IntegerField
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from dkmodelfields.adminforms import MonthField as MonthFormField
from .creator import Creator


class Month2YearTransform(Transform):
    """Handles __year filter on month fields.

       I.e.::

           MyModel.objects(my_month_field__year__gt=2022)

    """
    lookup_name = 'year'
    function = 'YEAR'

    @property
    def output_field(self):
        return IntegerField()

    def as_sql(self, compiler, connection, function=None, template=None):
        lhs, lhs_params = compiler.compile(self.lhs)
        return '%s(%s)' % (self.function, lhs), lhs_params


class MonthField(models.Field, Creator):
    """MySQL date <-> ttcal.Month() mapping.
       Maps the month to the first day of the month.
    """
    description = "A generic Month field"

    def __init__(self, *args, **kwargs):
        super(MonthField, self).__init__(*args, **kwargs)
        self.month_year_filter = True

    def db_type(self, connection):
        return 'DATE'

    def from_db_value(self, value, expression, connection, context):
        """Converts a value as returned by the database to a Python object.
           It is the reverse of get_prep_value().
        """
        return self.to_python(value)

    # converts python object to value that can be used in db-queries.
    def get_prep_value(self, value):
        """Convert to a value usable as a paramter in a query.
        """
        value = super().get_prep_value(value)

        if isinstance(value, (bytes, str)):
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
            return [force_text(value)]

        return super(MonthField, self).get_prep_lookup(lookup_type, value)

    def get_transform(self, lookup_name):
        """Handles __year filter on month fields.

           I.e.::

               MyModel.objects(my_month_field__year__gt=2022)

        """
        if lookup_name == 'year':
            return Month2YearTransform
        return super().get_transform(lookup_name)

    def get_db_prep_save(self, value, connection):
        """Convert to a value suitable for saving.
        """
        if isinstance(value, ttcal.Month):
            return '%04d-%02d-01' % (value.year, value.month)

        if isinstance(value, (bytes, str)):
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
            return [force_text(value)]

        return super(MonthField, self).get_db_prep_lookup(
            lookup_type, value, connection=connection, prepared=prepared)

    # converts from a database value to a python value
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

        if isinstance(value, (bytes, str)):
            return self._str_to_month(value)

        raise ValidationError("Value/month: %r, %r" % (value, type(value)))

    # def get_db_prep_value(self, value, connection, prepared):
    #     return self.to_python(value)

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


# for admin..
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
