"""
Admin support code for DurationFields.
"""
from django.forms.fields import Field
from django.forms import ValidationError
from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

import ttcal


class DurationInput(TextInput):
    """Duration input widget.
    """
    def render(self, name, value, attrs=None, renderer=None):
        """output.append(u'<li>%(cb)s<label%(for)s>%(label)s</label></li>' %
           {"for": label_for, "label": option_label, "cb": rendered_cb})
        """
        if value is None:
            value = ''
            
        final_attrs = self.build_attrs(attrs, {'type': self.input_type, 'name': name})
            
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            if isinstance(value, int):
                # Database backends serving different types
                value = ttcal.Duration(seconds=value)

            # Otherwise, we've got a timedelta already

            final_attrs['value'] = force_text(value)
        return mark_safe(f'<input{flatatt(final_attrs)} />')


class DurationField(Field):
    """Form field for DurationField custom database field.
    """
    widget = DurationInput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, value):
        """Returns a datetime.timedelta object.
        """
        super().clean(value)
        try:
            return ttcal.Duration.parse(value)
        except (ValueError, TypeError) as e:
            raise ValidationError('Enter a valid duration.') from e

    def to_python(self, value):
        """Convert form input to python value.
        """
        try:
            return ttcal.Duration.parse(value)
        except (ValueError, TypeError) as e:
            raise ValidationError('Enter a valid duration.') from e
