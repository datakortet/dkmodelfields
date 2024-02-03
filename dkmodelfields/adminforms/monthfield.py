"""Admin support code for MonthFields.
"""
from builtins import str as text

from django.forms.fields import CharField
from django.forms import ValidationError
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt

import ttcal


class MonthInput(TextInput):
    """Month input widget.
    """
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
            
        final_attrs = self.build_attrs(attrs, {'type': 'month', 'name': name})
            
        if value != '':
            # if isinstance(value, int):
            #     value = ttcal.Month(value)
            if isinstance(value, text):
                parts = value.split('-')
                y = int(parts[0])
                m = int(parts[1])
                value = ttcal.Month(y, m)
            assert isinstance(value, ttcal.Month), type(value)
            final_attrs['value'] = text(value.format("Y-m"))
        return mark_safe(f'<input{flatatt(final_attrs)} />')


class MonthField(CharField):
    """Month field widget.
    """
    widget = MonthInput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _str_to_month(self, sval):
        # type: (str) -> ttcal.Month
        # 2008-01
        if not isinstance(sval, str):
            print("NOT ISINSTANCE:", repr(sval))
        return ttcal.Month.parse(sval) if sval.strip() else None

    def clean(self, value):
        super().clean(value)
        try:
            return self._str_to_month(value)
        except:  # pragma: nocover  # noqa
            raise ValidationError(f'Invalid month: {value!r}')   # pylint:disable=W0707

    def to_python(self, value):
        """convert value to ttcal.Month().
        """
        try:
            return self._str_to_month(value)
        except:  # pragma: nocover # noqa
            raise ValidationError(f'Invalid month: {value!r}')   # pylint:disable=W0707
