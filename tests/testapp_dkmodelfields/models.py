# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db import models

from dkmodelfields import MonthField, YearField
from dkmodelfields.statusfield import StatusField


class M(models.Model):
    month = MonthField()

    def __str__(self):
        return str(self.month)


class Y(models.Model):
    yr = YearField()

    def __str__(self):
        return str(self.yr)


class AM(admin.ModelAdmin):
    pass


class S(models.Model):
    S_STATUSDEF = u"""
        =============== =========================================== ============
        status          verbose explanation                         category
        =============== =========================================== ============
        first           First status                                # [init]
        second          Second status                               # [ok]
        third           Third status                                # [post]
        =============== =========================================== ============
        @end-progress-status
    """
    
    status = StatusField(S_STATUSDEF, max_length=15,
                         verbose_name='Status', db_index=True, default='first')

    def __str__(self):
        return f'<class S status:{self.status} type:{type(self.status)})'
