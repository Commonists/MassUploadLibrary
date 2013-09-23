#!/usr/bin/env python

from setuptools import setup

setup(name='MassUploadLibrary',
    version      = '0.5',
    description  = 'Managing a mass-upload to Wikimedia Commons.',
    author       = 'Jean-Frederic',
    author_email = 'JeanFred@github',
    license      = 'MIT',
    packages     = ['uploadlibrary'],
    install_requires = ['Pywikipediabot'],
    dependency_links = ['http://tools.wmflabs.org/pywikibot/core.tar.gz#egg=Pywikipediabot'],
    )
