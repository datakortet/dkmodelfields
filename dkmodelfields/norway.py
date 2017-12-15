# -*- coding: utf-8 -*-

from django.core import validators
from django.db.models.fields import CharField
from django.utils.translation import ugettext_lazy as _
# from south.modelsinspector import add_introspection_rules


class TelefonField(CharField):
    """A Norwegian telephone number.
    """
    description = _("Phone number")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 8
        self.min_length = 8
        super(TelefonField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MinLengthValidator(self.min_length))

    def deconstruct(self):  # pragma: nocover
        # not strictly necessary
        name, path, args, kwargs = super(TelefonField, self).deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs


class GateField(CharField):
    """A Norwegian street address.
    """
    description = _("Norwegian street address field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 50
        super(GateField, self).__init__(*args, **kwargs)

    def deconstruct(self):  # pragma: nocover
        # not strictly necessary
        name, path, args, kwargs = super(GateField, self).deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs


class PostnrField(CharField):
    """A 4 digit Norwegian zip code value (leading zeroes are significant
       so it is stored as character data).
    """
    description = _("Norwegian zip code field")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 4
        self.min_length = 4
        super(PostnrField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MinLengthValidator(self.min_length))

    def formfield(self, **kwargs):
        # should be transitioned to use the new django-localflavor package
        from localflavor.no.forms import NOZipCodeField
        defaults = {'form_class': NOZipCodeField}
        defaults.update(kwargs)
        return super(PostnrField, self).formfield(**defaults)

    def deconstruct(self):  # pragma: nocover
        # not strictly necessary
        name, path, args, kwargs = super(PostnrField, self).deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs


class PoststedField(CharField):
    """The name of a Norwegian zip code.
    """
    description = _("Norwegian zip code name")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 50
        super(PoststedField, self).__init__(*args, **kwargs)

    def deconstruct(self):  # pragma: nocover
        # not strictly necessary
        name, path, args, kwargs = super(PoststedField, self).deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs
