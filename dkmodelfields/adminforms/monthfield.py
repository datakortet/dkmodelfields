# -*- coding: utf-8 -*-

"""Admin support code for MonthFields.
"""

from dk import ttcal
from django.forms.fields import CharField
from django.forms import ValidationError
from django.forms.util import flatatt
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe


class MonthInput(TextInput):
    """Month input widget.
    """
    def render(self, name, value, attrs=None):
        if value is None:
            value = u''
        final_attrs = self.build_attrs(attrs, type='month', name=name)
        if value != u'':
            # if isinstance(value, (int, long)):
            #     value = ttcal.Month(value)
            if isinstance(value, unicode):
                parts = value.split('-')
                y = int(parts[0])
                m = int(parts[1])
                value = ttcal.Month(y, m)
            assert isinstance(value, ttcal.Month), type(value)
            final_attrs['value'] = unicode(value.format("Y-m"))
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class MonthField(CharField):
    """Month field widget.
    """
    widget = MonthInput

    def __init__(self, *args, **kwargs):
        super(MonthField, self).__init__(*args, **kwargs)

    def _str_to_month(self, sval):  # pylint:disable=R0201
        # type: (basestring) -> ttcal.Month
        # 2008-01
        if not isinstance(sval, (str, unicode)):
            print "NOT ISINSTANCE:", repr(sval)
        if not sval.strip():
            return None
        return ttcal.Month.parse(sval)

    def clean(self, value):
        super(MonthField, self).clean(value)
        try:
            return self._str_to_month(value)
        except:
            raise ValidationError('Invalid month: %r' % value)

    def to_python(self, value):  # pylint:disable=R0201
        """convert value to ttcal.Month().
        """
        try:
            return self._str_to_month(value)
        except:
            raise ValidationError('Invalid month: %r' % value)
