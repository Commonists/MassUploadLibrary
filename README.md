MassUploadLibrary
=================

Managing a mass-upload to Wikimedia Commons.

Overview
--------

This library provides all is needed to mass-upload content 
and its associated metadata to Wikimedia Commons.

Its philosophy is to provide a nearly fully featured codebase, with entry points
to tailor the behaviour to each specific case.

Features include:
* Attachment of metadata post-processors per metadata field
* Mapping metadata with a wiki-based alignment
* Use of a 
  [Data ingestion template](https://commons.wikimedia.org/wiki/Category:Data_ingestion_layout_templates)

Dependencies
------------

Actual upload is made using
[Pywikibot](http://www.mediawiki.org/wiki/Manual:Pywikibot) (in its core version),
its [upload.py](http://www.mediawiki.org/wiki/Manual:Pywikibot/upload.py)
and data_ingestion.py.

Installation
------------
`python setup.py install`

Will install the library and its dependencies.
