# -*- coding: utf-8 -*-

"""A database field class that goes with ttcal.Year.
"""

# pylint:disable=R0904
# R0904 too many public methods

import datetime
from django.db.models.fields import Field
from django.db import models, connection as cn
from django.core.exceptions import ValidationError
# from django.contrib.admin.filterspecs import FilterSpec
from django.utils.encoding import force_unicode

from dk import ttcal
from dkmodelfields.adminforms import MonthField as MonthFormField

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter


class MonthField(Field):
    """MySQL date <-> ttcal.Month() mapping.
       Maps the month to the first day of the month.
    """

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(MonthField, self).__init__(*args, **kwargs)
        self.month_year_filter = True

    def get_internal_type(self):
        return "MonthField"
    
    def db_type(self, connection):
        return 'DATE'

    # def _get_FIELD_display(self, field):
    #     print field, self
    #     return u'42'

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
        if isinstance(value, (str, unicode)):
            return value

        if isinstance(value, ttcal.Month):
            return '%04d-%02d-01' % (value.year, value.month)

        if isinstance(value, list):
            return '%04d-%02d-01' % (value[0].year, value[0].month)

        return value

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        """Return value prepared for database lookup.
        """

        if lookup_type == 'year':
            if isinstance(value, ttcal.Year):
                value = value.year
            else:
                try:
                    if isinstance(value, list):
                        date = datetime.datetime.strptime(value[0],
                                                          "%Y-%m-%d %H:%M:%S")
                        value = date.year
                    value = int(value)
                except TypeError:
                    raise ValueError(
                        "The __year lookup type requires an integer argument")

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
        
        if isinstance(value, datetime.date):
            return ttcal.Month(value.year, value.month)

        if isinstance(value, ttcal.Month):
            return value
        
        if isinstance(value, (str, unicode)):
            return self._str_to_month(value)

        if not isinstance(value, ttcal.Month):
            print "TOPYTHON:", value, type(value), repr(value)
            raise ValidationError("Value/month: %r, %r" %
                                  (value, type(value)))
        
        return value

    def _str_to_month(self, sval):  # pylint:disable=R0201
        # 2008-01
        if not sval.strip():
            return None
        y = int(sval[:4])
        m = int(sval[5:7])
        return ttcal.Month(y, m)
        
    def value_to_string(self, obj):
        """Serialization.
        """
        val = self._get_val_from_obj(obj)
        return '%04d-%02d' % (val.year, val.month)

    def formfield(self, **kwargs):  # pylint:disable=W0221
        """Formfield declaration for admin site.
        """
        defaults = {'form_class': MonthFormField}
        defaults.update(kwargs)
        return super(MonthField, self).formfield(**defaults)


from south.modelsinspector import add_introspection_rules
add_introspection_rules(
    [],
    ["^dkmodelfields\.monthfield\.MonthField"])


# class MonthFieldYearFilterSpec(FilterSpec):
#     """This is a filter for the admin site, that enables filtering on
#        the year of the month.
#     """
#     def __init__(self, f, request, params, model, model_admin):
#         super(MonthFieldYearFilterSpec, self).__init__(f, request, params,
#                                                        model, model_admin)
#         self.lookup_kwarg = '%s__year' % f.name
#         self.lookup_val = request.GET.get(self.lookup_kwarg, None)
#         self.lookup_choices = model_admin.queryset(
#             request).distinct().order_by(
#             f.name).values(f.name)
#
#         self.links = []
#
#         choices = [val[self.field.name] for val in self.lookup_choices]
#         choices = [v for v in choices if v is not None]
#         choices = set(m.year for m in choices)
#         for val in sorted(choices):
#             self.links.append((unicode(val),
#                                {'%s__year' % self.field.name: str(val)}))
#         self.lookup_choices = [v[0] for v in self.links]
#
#     def title(self):
#         return "year"
#
#     def choices(self, cl):
#         yield {'selected': self.lookup_val is None,
#                 'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
#                 'display': _('All')}
#         for val, param_dict in self.links:
#             yield {'selected': self.lookup_val == val,
#                    'query_string': cl.get_query_string(param_dict),
#                    'display': val}
        

# FilterSpec.register(lambda f: isinstance(f, MonthField),
#                     MonthFieldYearFilterSpec)
# FilterSpec.filter_specs.insert(
#     0, (lambda f: getattr(f, 'month_year_filter', False),
#                                    MonthFieldYearFilterSpec))


class MonthFieldYearSimpleFilter(SimpleListFilter):
    title = _(u'år')

    parameter_name = 'month_year'

    def lookups(self, request, model_admin):
        links = []
        months = model_admin.queryset(
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
