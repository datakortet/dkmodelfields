# -*- coding: utf-8 -*-

"""Admin support code for DurationFields.
"""

import ttcal
from django.forms.fields import Field
from django.forms import ValidationError
from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text


class DurationInput(TextInput):
    """Duration input widget.
    """
    def render(self, name, value, attrs=None):
        """output.append(u'<li>%(cb)s<label%(for)s>%(label)s</label></li>' %
           {"for": label_for, "label": option_label, "cb": rendered_cb})
        """
        if value is None:
            value = u''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != u'':
            # Only add the 'value' attribute if a value is non-empty.
            if isinstance(value, int):
                # Database backends serving different types
                value = ttcal.Duration(seconds=value)

            # Otherwise, we've got a timedelta already

            final_attrs['value'] = force_text(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class DurationField(Field):
    """Form field for DurationField custom database field.
    """
    widget = DurationInput

    def __init__(self, *args, **kwargs):
        super(DurationField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """Returns a datetime.timedelta object.
        """
        super(DurationField, self).clean(value)
        try:
            return ttcal.Duration.parse(value)
        except (ValueError, TypeError):
            raise ValidationError('Enter a valid duration.')

    def to_python(self, value):  # pylint:disable=R0201
        """Convert form input to python value.
        """
        try:
            return ttcal.Duration.parse(value)
        except (ValueError, TypeError):
            raise ValidationError('Enter a valid duration.')
