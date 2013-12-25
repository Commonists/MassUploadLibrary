#!/usr/bin/python
# -*- coding: latin-1 -*-

"""Setup script"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = 0.5
classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Utilities'
]
packages = ['uploadlibrary']
requires = ['argparse', 'lxml', 'Pywikibot']
dependency_links = ['http://tools.wmflabs.org/pywikibot/core.tar.gz#egg=Pywikibot']

setup(name='MassUploadLibrary',
      version=version,
      description='Managing a mass-upload to Wikimedia Commons.',
      long_description=open('README.md').read(),
      author='Jean-Frederic',
      author_email='JeanFred@github',
      license='MIT',
      packages=packages,
      install_requires=requires,
      dependency_links=dependency_links)
