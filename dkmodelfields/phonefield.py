# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
import re
from django.core import validators
from django.db.models.fields import CharField
from django.utils.translation import ugettext_lazy as _
from south.modelsinspector import add_introspection_rules


def e164_validator(value):
    if not re.match(r'^\+[0-9]{1,3}\.[0-9]{4,14}(?:x.+)?$', value):
        raise ValidationError(
            u"The phone number is not correctly formatted (e164)")



class TelephoneField(CharField):
    """International phone number corresponding to E.164.
    """
    description = _("International phone number")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 16
        self.min_length = 8
        super(TelephoneField, self).__init__(*args, **kwargs)
        self.validators.extend([
            validators.MinLengthValidator(self.min_length),
            e164_validator
        ])


add_introspection_rules([],
    ["^dkmodelfields\.phonefield\.TelephoneField"])
