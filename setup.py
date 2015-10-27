#!/usr/bin/python
# -*- coding: latin-1 -*-

"""Setup script"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = 0.6
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
requires = ['argparse', 'lxml', 'pywikibot==2.0rc3']

setup(name='MassUploadLibrary',
      version=version,
      description='Managing a mass-upload to Wikimedia Commons.',
      long_description=open('README.md').read(),
      author='Jean-Frederic',
      author_email='JeanFred@github',
      license='MIT',
      packages=packages,
      install_requires=requires)
