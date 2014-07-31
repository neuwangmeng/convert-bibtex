#!/usr/bin/env python

from distutils.core import setup
from conbib import __version__ as version


with open('README.md') as f:
    long_description = f.read()

setup(
    name='convert-bibtex',
    version=version,
    description='Conversions and cite key generation for BibTeX files.',
    author='Joseph W. May (Li Research Group)',
    author_email='jwmay@uw.edu',
    url='http://www.gaussiantoolkit.org',
    license = 'http://opensource.org/licenses/MIT',
    long_description = long_description,
    packages=['conbib', 'conbib/tests'],
    scripts=['bin/convert-bibtex'],
    package_data={'conbib': ['tests/*']},
)
