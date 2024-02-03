"""Admin support code for YearFields.
"""
from django.forms.fields import Field
from django.forms import ValidationError
from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

import ttcal


class YearInput(TextInput):
    """Year input widget.
    """
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
            
        final_attrs = self.build_attrs(attrs, {'type': 'number', 'name': name})
        
        if value != '':
            if isinstance(value, int):
                value = ttcal.Year(value)
            final_attrs['value'] = force_text(value)
        return mark_safe(f'<input{flatatt(final_attrs)} />')


class YearField(Field):
    """Year field widget.
    """
    widget = YearInput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, value):
        super().clean(value)
        try:
            return ttcal.Year(int(value))
        except:  # pragma: nocover  # noqa
            raise ValidationError(f'Invalid year: {value!r}')  # pylint:disable=W0707

    def to_python(self, value):
        """convert value to ttcal.Year().
        """
        try:
            return ttcal.Year(int(value))
        except:  # pragma: nocover  # noqa
            raise ValidationError(f'Invalid year: {value!r}')  # pylint:disable=W0707
