#!/usr/bin/env python

from distutils.core import setup

version = '0.1'

setup(name='convert-bibtex',
      version=version,
      description='Conversions and cite key generation for BibTeX files.',
      packages=['conbib', 'conbib/tests'],
      scripts=['bin/convert-bibtex'],
      package_data={'conbib': ['tests/*']},
      author='Joseph W. May',
      author_email='jwmay@uw.edu',
      url='http://www.gaussiantoolkit.org',
     )
