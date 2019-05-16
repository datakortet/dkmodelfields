# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
import re
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from dk.collections import pset
from collections import defaultdict
from django.db.models.fields import Field
from django.db import models
from django import forms


class StatusValue(object):
    def __init__(self, name=None, verbose=None, categories=()):
        self.name = name.strip()
        self.verbose = verbose.strip() if verbose else ""
        if isinstance(categories, basestring):
            self.categories = re.split(r'[,\s]+', categories)
        else:
            self.categories = categories

    def __unicode__(self):
        print "UNICODE:STATUS:VALUE", self.name
        return self.name

    def __str__(self):
        print "STR:STATUS:VALUE:", self.name
        return self.name

    def __repr__(self):
        return 'StatusValue(name=%r, verbose=%r, categories=%r)' % (
            self.name, self.verbose, self.categories)


class StatusDef(object):
    """Compact way to define status fields, that takes care of most of
       the manual drudgery involved.

       Usage::

           class MyModel(models.Model):
               ..fields..
               STATUSDEF = statusdef.StatusDef(u'''

                    @start-tagname
                    =========== =================================== ==========
                    status      verbose explanation                 category
                    =========== =================================== ==========
                    ok          Ny Bestilling                       # [init]
                    locked      Last (legges til ny jobb)           # [init]
                    produseres  Klar for QA (lagt til ny jobb)      # [ready]
                    hentet      Kort trykkes                        # [done]
                    sendt       Kort er trykket og sendt med posten # [done]
                    dblbest     Fjernet fordi det var flere         # [err]
                    fnr-feil    Feil i fnr                          # [err]
                    =========== =================================== ==========
                    @end-tagname
               ''')
               status = models.CharField(max_length=10,  # max length of status
                                         choices=STATUSDEF.options)

       @something and @something-else can be used with the sphinx
       `include <http://docutils.sourceforge.net/docs/ref/rst/directives.html#include>`_
       directive's :start-after: and :end-before: options.

       Empty lines, and lines starting with `@` are disregarded.

       You are not required to format the string as a rst table, but it seems
       foolish not to do so.

    """

    # TODO:  create a custom model field that maps to <select>

    defre = re.compile(ur'''
    \s*(?P<name>[a-z][-a-z0-9]*)\s*(?P<verbose>[^\#]*)\#\s*\[(?P<categories>[^]]*)\]
    ''', re.VERBOSE)

    # noinspection PyMethodMayBeStatic
    def _parse(self, txt):  # pylint:disable=R0201
        lines = [line for line in txt.split('\n') if line.strip()]
        defs = pset()

        in_header = False  # a state-machine...

        for line in lines:
            line = line.strip()

            # skip header lines
            if in_header and not line.startswith('='):
                continue
            if line.startswith('@'):
                continue
            if line.startswith('=') and not in_header:
                in_header = True
                continue
            if line.startswith('=') and in_header:
                in_header = False
                continue

            m = StatusDef.defre.match(line)
            if m:
                gdict = pset((str(k), v)
                             for (k, v) in m.groupdict().items())
                sval = StatusValue(name=gdict.name,
                                   verbose=gdict.verbose,
                                   categories=gdict.categories)
                defs[sval.name] = sval
            else:  # pragma: nocover
                print 'error parsing:', repr(line)

        return defs

    def __init__(self, txt):
        self.status = self._parse(txt)
        self._defs = self.status.values()
        self._categories = set()
        for d in self._defs:
            for cat in d.categories:
                self._categories.add(cat)
        self._cat2status = defaultdict(set)
        for d in self._defs:
            for cat in d.categories:
                self._cat2status[cat].add(d)

    @property
    def namelength(self):
        if not self._defs:
            return 0  # pragma: nocover
        return max(len(d.name) for d in self._defs)

    def is_category(self, txt):
        return txt in self._categories

    def category(self, status):
        """Return the category that status belongs to.
        """
        return self.status[status].category

    def category2status(self, category):
        """Return all statuses belonging to `category`.
        """
        return self._cat2status[category]

    def valid_status(self, s):
        """Is `s` a well-defined status value?
        """
        return s in self.status.keys()

    @property
    def options(self):
        """Return list of pairs of (status, description), useful for
           selects boxes etc.
        """
        return [(name, gdict) for name, gdict in self.status]
        # return [(name, gdict.verbose) for name, gdict in self.status]


class StatusField(Field):
    """Character status field.
    """
    __metaclass__ = models.SubfieldBase

    description = _("Status field")

    def __init__(self, *args, **kw):
        self.txt = args[0] if args else ""
        self.statusdef = StatusDef(self.txt)
        self.max_length = kw['max_length'] = kw.get('max_length', self.statusdef.namelength)
        kw['choices'] = self.statusdef.options
        super(StatusField, self).__init__(**kw)
        self.validators.append(validators.MaxLengthValidator(self.max_length))
        
    def deconstruct(self):
        name, path, args, kwargs = super(StatusField, self).deconstruct()
        # del kwargs['max_length']
        # print "OPTIONS:", self.statusdef.options
        kwargs['choices'] = self.statusdef.options
        return name, path, [self.txt], kwargs

    def to_python(self, value):
        """Converts the input ``value`` into a StatusValue instance,
           raising ValueError if the data can't be converted.
        """
        print "TO:PYTHON:", value
        if not value:
            print "NOT:VALUE:", None
            return None

        if isinstance(value, StatusValue):
            print "STSTUS:VALUE:", value
            return value

        if isinstance(value, basestring):
            if value in self.statusdef.status:
                print "FOUND_STATUSVAL:", self.statusdef.status[value]
                #return value
                return self.statusdef.status[value]
            raise ValueError("Unknown status: %r", value)

        print "RETURNING:DEFULT:", value
        return value

    # def get_internal_type(self):
    #     return "StatusField"

    def db_type(self, connection):
        return 'VARCHAR(%s)' % self.max_length

    def get_db_prep_value(self, value, connection, prepared=False):
        print "GET:DB:PREP:VALUE:", value
        return self.get_prep_value(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def get_prep_lookup(self, lookup_type, value):
        """Return a value prepared for database lookup.
        """
        print "GET:PREP:LOOKUP:", lookup_type, value
        if lookup_type == 'in':
            res = set()
            if isinstance(value, basestring):
                if self.statusdef.is_category(value):
                    res |= self.statusdef.category2status(value)
                else:
                    res.add(value)
            else:
                for v in value:
                    if self.statusdef.is_category(v):
                        res |= self.statusdef.category2status(v)
                    else:
                        res.add(v)
            res = [self.get_prep_value(v) for v in res]
            return res
        elif lookup_type == 'exact':
            return value
        else:
            return value

    def get_prep_value(self, value):
        """Convert to a value useable as a parameter in a query.
        """
        print "GET:PREP:VALUE:", value
        if value is None:
            return value
        return self.to_python(value).name

    def formfield(self, *args, **kwargs):
        # Passing max_length to forms.CharField means that the value's length
        # will be validated twice. This is considered acceptable since we want
        # the value in the form field (to pass into widget for example).
        def status2txt(v):
            print "CALLING:STATUS2:TXT:", v
            if isinstance(v, StatusValue):
                return v.name
            return v

        # print "FORMFIELD:", args, kwargs
        defaults = {'choices_form_class': StatusSelectForm, 'max_length': self.max_length, 'coerce': status2txt}
        defaults.update(kwargs)
        return super(StatusField, self).formfield(**defaults)


class StatusSelectForm(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        print "STATUS:SELECT:FORM:", args, kwargs
        kwargs['choices'] = [(k, s.verbose if isinstance(s, StatusValue) else None) for k, s in kwargs['choices']]
        super(StatusSelectForm, self).__init__(*args, **kwargs)

    def clean(self, value):
        print "CLEAN:", value, type(value)
        return super(StatusSelectForm, self).clean(value)
