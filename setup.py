#!/usr/bin/env python

from setuptools import setup

setup(name='MassUploadLibrary',
    version      = '0.5',
    description  = 'Managing a mass-upload to Wikimedia Commons.',
    author       = 'Jean-Frederic',
    author_email = 'JeanFred@github',
    license      = 'GPL',
    packages     = ['uploadlibrary'],
    install_requires = ['Pywikipediabot'],
    dependency_links = ['http://pywikipedia.org/nightly/package/pywikipedia-rewrite/pywikipedia-rewrite-nightly.tgz#egg=Pywikipediabot'],
    )
