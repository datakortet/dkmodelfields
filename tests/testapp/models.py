# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models

from dkmodelfields import MonthField, YearField


class M(models.Model):
    month = MonthField()

    def __unicode__(self):
        return unicode(self.month)


class Y(models.Model):
    yr = YearField()

    def __unicode__(self):
        return unicode(self.yr)


class AM(admin.ModelAdmin):
    pass
