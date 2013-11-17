MassUploadLibrary
=================

Managing a mass-upload to Wikimedia Commons.

Overview
--------

This library provides all is needed (hopefully) to mass-upload content media
and its associated metadata to Wikimedia Commons.

Its philosophy is to provide a nearly fully featured codebase, with entry points
to tailor the behaviour to each specific case.

Features include:
* Attachment of metadata post-processors per metadata field
* Mapping metadata with a wiki-based alignment
* Use of a [Data ingestion template]


Dependencies
------------

Actual upload is made using [Pywikibot] (in its core version), its [upload.py] and data_ingestion.py.


Usage
-----

This library by itself does not do much. See the [TrutatBis] project for a minimal implementation.

It basically consists of overloading some methods, and passing new ones.

### Pre-processing

Pre-processing is triggered through `--prepare-alignment` CLI parameter

It consists in: 
* indexing all the metadata, per field, counting each field value.
* outputing it as a Template-based wikitable − see [1] or [2].

This wiki table is to be used by volunteers to match the insitution metadata
to Wikimedia Commons metadata − either in values for the (typically) {{Artwork}} template,
or in categories to be added. 

### Post-processing

Pre-processing is triggered through `--post-process` CLI parameter

In this step, we associate (through a dictionary) a field to a post-processing method.

For example, we can associate the `Date` field to a method which parses the date
to fill out a `{{Other date}}` template.

The `PostProcessing.py` module holds a bunch of useful processors, and is expected
to grow over time. Very specific processors do not have to be integrated in the library.

#### Alignments

A specific processor makes use of the alignment performed in the previous step.

The process is the following:
* Getting back on local disk the wikitables now holding all the mapping thanks to awesome volunteers.
* Specifying which fields are to be retrieved.
* Retrieving the fields
* Instructing, in the mapping dictionary, that such fields is to be processed with the alignment.

Here is an example of the code from the [TrutatBis] project:
```python
mapping_fields = ['Type de document', 'Support', 'Technique', 'Auteur']
mapper = commonprocessors.retrieve_metadata_alignments(mapping_fields, alignment_template)
mapping_methods = {
    'Format': (processors.parse_format, {}),
    'Analyse': (processors.look_for_date, {}),
    'Auteur': (commonprocessors.process_with_alignment, {'mapper': mapper}),
    'Support': (commonprocessors.process_with_alignment, {'mapper': mapper}),
    'Technique': (commonprocessors.process_with_alignment, {'mapper': mapper}),
    }
reader = collection.post_process_collection(mapping_methods)
```


### Dry-run

Dry-run is triggered through `--dry-run` CLI parameter.

It outputs the transformed metadata in Wikimedia Commons format, useful either
for [peer review] at the batch uploading coordination page, or to be sent to the GLAM
if they really want to upload themselves through good old upload form.


### Upload

Triggered through `--upload` CLI parameter.

What it says on the tin: upload to Wikimedia Commons using Pywikibot.


### Data ingestion template

In this process, metadata is formatted as a MediaWiki template:
```
{{CoolInstitutionIngestionTemplate
|key1=value1
|key2=value2
}}
```

Where `{{CoolInstitutionIngestionTemplate}}` is a cool [Data ingestion template].

* it can be made to use `{{Artwork}}`, `{{Photograph}}`, whatever is better.
* it maps the various insitution fields to our fields.
* It is to be susbst-ed recursively at upload time.

What is nice with it is that people do not need to get their hands into the code to help out,
they can just edit the template.

Data ingestion templates can be made arbitrarily complex, with crazy `{{#if}}` parser functions
triggering categorisation or whatever. Some problems are more easily solved this
way rather than implementing it in Python.

Installation
------------

Easiest way to install should be to use `pip`:

    pip install git+git://github.com/JeanFred/MassUploadLibrary.git#egg=uploadlibrary

But this usually fails when failing to solve the Pywikibot dependency.

Alternatively, you can clone the repository and install it using `setuptools`:

    python setup.py install


Note that Pywikibot dependency is sometimes tricky to resolve automatically.
If it fails, consider installing it manually.

[1]: https://commons.wikimedia.org/wiki/Commons:Batch_uploading/Fonds_Eug%C3%A8ne_Trutat_bis/Places
[2]: https://commons.wikimedia.org/wiki/Commons:Batch_uploading/Fonds_Eug%C3%A8ne_Trutat_bis/Auteur
[peer review]: https://commons.wikimedia.org/wiki/Commons:Batch_uploading/Fonds_Eug%C3%A8ne_Trutat_bis/test
[TrutatBis]: https://github.com/JeanFred/TrutatBis/blob/master/TrutatBis.py
[Data ingestion template]: https://commons.wikimedia.org/wiki/Category:Data_ingestion_layout_templates
[Pywikibot]: http://www.mediawiki.org/wiki/Manual:Pywikibot
[upload.py]: http://www.mediawiki.org/wiki/Manual:Pywikibot/upload.py
