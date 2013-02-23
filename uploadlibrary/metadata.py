# -*- coding: latin-1 -*-

"""Mass Upload Libray − handling metadata."""

__authors__ = 'User:Jean-Frédéric'

import re
import sys
import pickle
import codecs
import csv
from os.path import join
import os
from collections import Counter
import pywikibot
from pywikibot import textlib
import UnicodeCSV


class MetadataRecord(object):

    """Represent a Record, with its associated metadata."""

    def __init__(self, **entries):
        """Constructor.

        Update the object with dictionary passed as argument.

        """
        self.__dict__.update(entries)

    def get_field_names(self):
        """Return the field values from the records."""
        return self.__dict__.keys()

    def post_process(self, mapping):
        """Post-process the MetadataRecord with the given mapping.

        For each field of the record,
        call the relevant post-processing method.

        """
        for field in self.__dict__.keys():
            if field in mapping.keys():
                self.post_process_wrapper(field, mapping[field])

    def post_process_wrapper(self, field, method):
        """Wrap the post-processing methods.

        Pop the value for the given field from the record
        Apply the given method on it
        Update the record with it

        """
        old_field_value = self.__dict__.pop(field, None)
        new_field_value = method(field, old_field_value)
        self.__dict__.update(**new_field_value)

    def to_template(self, template=u'Ingestion layout'):
        """Return the Record as a MediaWiki template."""
        return textlib.glue_template_and_params((template,
                                                 self.__dict__))

    def get_title(self):
        """Return the title for the file."""
        raise NotImplementedError("This should be handled in subclasses.")

    def to_disk(self, directory):
        """Write the Record on disk in a given repository.

        Serialise the record and name it as the file title,
        do nothing if anything goes wrong.

        """
        fileName = join(directory, self.get_title() + '.dump')
        try:
            with open(fileName, 'w') as f:
                pickle.dump(self, f)
        except Exception, e:
            print "Could not pickle record %s \n %s" % (fileName, e)


class MetadataCollection(object):

    """Processing a metadata collection in various ways."""

    def __init__(self):
        """Constructor."""
        self.records = []

    def retrieve_metadata_from_csv(self, csv_file, delimiter=','):
        """Retrieve metadata from the given CSV file."""
        file_handler = codecs.open(csv_file, 'r', 'utf-8')
        csvReader = UnicodeCSV.unicode_csv_dictreader(file_handler,
                                                      delimiter=delimiter)
        try:
            for row in csvReader:
                self.records.append(self.handle_record(row))
        except csv.Error, e:
            sys.exit('file %s, line %d: %s' % (self.csv_file,
                                               csvReader.line_num, e))

    def retrieve_metadata_from_files(self, files_path):
        """Retrieve metadata from the files themselves in a given path."""
        print "Iterating in %s" % files_path
        assert os.path.exists(files_path)
        files = os.listdir(files_path)
        for image in files:
            self.records.append(self.handle_record(join(files_path, image)))

    def handle_record(self, items):
        """Handle a record.

        Default handling behaviour: return a new MetadataRecord
        initialised with the items as record values.

        """
        return MetadataRecord(**items)

    def post_process_collection(self, method_mapping):
        """Call on each record its post_process method."""
        for record in self.records:
            record.post_process(method_mapping)

    def print_metadata_of_record(self, index):
        """Print the metadata of the record.

        Print the result of get_title and of to_template.

        """
        print self.records[index].get_title()
        print self.records[index].to_template()

    def index_unique_metadata_values(self):
        """Count unique metadata values.

        Loop over the metadata collection.
        Return a dictionary of Sets (?)

        """

        def _add_to_set_dict(aDict, key, value):
            if key not in aDict:
                aDict[key] = set()
            try:
                aDict[key].add(value)
            except TypeError, e:
                aDict[key].update(value)

        sets_dict = dict()
        for record in self.records:
            for field, field_value in record.__dict__.items():
                add_to_set_dict(sets_dict, field, field_value)
        return sets_dict

    def count_metadata_values(self):
        """Count the metadata values for earch record field.

        Return a dictionary of Counters.

        """

        def _add_to_counter_dict(aCounter_dict, field, value):
            """Add to a dictionary of Counter the value for good Counter."""
            if field not in aCounter_dict:
                aCounter_dict[field] = Counter()
            try:
                aCounter_dict[field][value] += 1
            except TypeError, e:
                for item in value:
                    aCounter_dict[field][item] += 1

        field_values_counters_dict = {}
        for record in self.records:
            for field, field_value in record.__dict__.items():
                _add_to_counter_dict(field_values_counters_dict,
                                     field, field_value)
        return field_values_counters_dict
