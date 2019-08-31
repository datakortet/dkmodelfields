#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""dkmodelfields - Django model fields
"""

import io, setuptools

version = '1.0.1'

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Topic :: Software Development :: Libraries
"""


setuptools.setup(
    name='dkmodelfields',

    version=version,
    maintainer="Norsk Test",
    maintainer_email="itdrift@norsktest.no",
    include_package_data=True,
    packages=setuptools.find_packages(exclude=['tests']),
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=io.open('README.rst', encoding='utf-8').read(),

    install_requires=[
        'dk',
        'Django',
    ],
    zip_safe=False,
)
