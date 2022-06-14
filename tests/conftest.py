# -*- coding: utf-8 -*-
import os

import django
import sys

DIRNAME=os.path.dirname(__file__)


def pytest_configure():
    sys.path.append(DIRNAME)
    from django.conf import settings
    settings.configure(
        PRODUCTION=False,
        DEBUG=True,
        TESTING=True,
        APPNAME='dkmodelfields',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
                'NAME': os.path.join(DIRNAME, 'dkmodelfields-testing.db'),  # Or path to database file if using sqlite3.
                # 'NAME': ':memory:',
                # The following settings are not used with sqlite3:
                'USER': '',
                'PASSWORD': '',
                'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
                'PORT': '',  # Set to empty string for default.
            }
        },
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.admin',
            'django.contrib.sites',
            'dkmodelfields',
            'testapp_dkmodelfields',
        ),
    )
    # Need this line to avoid: AppRegistryNotReady: Models aren't loaded yet.
    django.setup()
    from django.core.management import call_command
    call_command('migrate', interactive=False)
