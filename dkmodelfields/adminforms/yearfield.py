# -*- coding: utf-8 -*-

"""Admin support code for YearFields.
"""

import ttcal
from django.forms.fields import Field
from django.forms import ValidationError
from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode


class YearInput(TextInput):
    """Year input widget.
    """
    def render(self, name, value, attrs=None):
        if value is None:
            value = u''
        final_attrs = self.build_attrs(attrs, type='number', name=name)
        if value != u'':
            if isinstance(value, (int, long)):
                value = ttcal.Year(value)
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class YearField(Field):
    """Year field widget.
    """
    widget = YearInput

    def __init__(self, *args, **kwargs):
        super(YearField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super(YearField, self).clean(value)
        try:
            return ttcal.Year(int(value))
        except:
            raise ValidationError('Invalid year: %r' % value)

    def to_python(self, value):  # pylint:disable=R0201
        """convert value to ttcal.Year().
        """
        try:
            return ttcal.Year(int(value))
        except:
            raise ValidationError('Invalid year: %r' % value)
