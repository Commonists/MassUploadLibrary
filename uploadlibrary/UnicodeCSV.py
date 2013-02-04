# -*- coding: latin-1 -*-

"""Managing CSV in Unicode."""

import csv


def unicode_csv_dictreader(unicode_csv_data, dialect=csv.excel, **kwargs):
    """Behave like a csv.DictReader but with Unicode support."""
    csv_reader = csv.DictReader(utf_8_encoder(unicode_csv_data),
                                dialect=dialect, **kwargs)
    for row in csv_reader:
        for key, value in row.items():
            row[key] = unicode(value, 'utf-8')
        yield row


def utf_8_encoder(unicode_csv_data):
    """Encode a given csv as UTF-8 and yield each line."""
    for line in unicode_csv_data:
        yield line.encode('utf-8')
