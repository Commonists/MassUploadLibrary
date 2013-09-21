# -*- coding: latin-1 -*-

"""Mass Upload Libray − handling metadata."""

__authors__ = 'User:Jean-Frédéric'
import sys
import pickle
import codecs
import csv
import os
from os.path import join
from collections import Counter
from uploadlibrary import UnicodeCSV
import pywikibot.textlib as textlib
from scripts.data_ingestion import Photo
from uploadlibrary.PostProcessing import MetadataMapping, make_categories


class MetadataRecord(Photo):

    """Represent a Record, with its associated metadata."""

    def get_field_names(self):
        """Return the field values from the records."""
        return self.metadata.keys()

    def post_process(self, mapping):
        """Post-process the MetadataRecord with the given mapping.

        For each field of the record,
        call the relevant post-processing method.

        """
        for field in self.metadata.keys():
            if field in mapping.keys():
                self.post_process_wrapper(field, mapping[field])

    def post_process_wrapper(self, field, method):
        """Wrap the post-processing methods.

        Pop the value for the given field from the record
        Apply the given method on it
        Update the record with it

        """

        def _smart_update_dict(aDict, other_dict):
            for key, value in other_dict.items():
                if key in aDict:
                    try:
                        aDict[key].extend(value)
                    except:
                        aDict[key] = value.append(aDict[key])
                else:
                    aDict[key] = value

        old_field_value = self.metadata.pop(field, None)
        new_field_value = method(field, old_field_value)
        _smart_update_dict(self.metadata, new_field_value)

    def to_template(self, template=u'Ingestion layout'):
        """Return the Record as a MediaWiki template."""
        return textlib.glue_template_and_params((template,
                                                 self.__dict__))

    #def to_disk(self, directory):
        #"""Write the Record on disk in a given repository.

        #Serialise the record and name it as the file title,
        #do nothing if anything goes wrong.

        #"""
        #fileName = join(directory, self.get_title() + '.dump')
        #try:
            #with open(fileName, 'w') as f:
                #pickle.dump(self, f)
        #except Exception, e:
            #print "Could not pickle record %s \n %s" % (fileName, e)


class MetadataCollection(object):

    """Processing a metadata collection in various ways."""

    def __init__(self):
        """Constructor."""
        self.records = []
        self.fields = set()
        self.post_processor = MetadataMapping()

    def retrieve_metadata_from_csv(self, csv_file, delimiter=','):
        """Retrieve metadata from the given CSV file."""
        file_handler = codecs.open(csv_file, 'r', 'utf-8')
        csvReader = UnicodeCSV.unicode_csv_dictreader(file_handler,
                                                      delimiter=delimiter)
        try:
            for row in csvReader:
                metadata_record = self.handle_record(row)
                self.records.append(metadata_record)
                self.fields.update(metadata_record.get_field_names())
        except csv.Error, e:
            sys.exit('file %s, line %d: %s' % (csv_file,
                                               csvReader.line_num, e))

    def retrieve_metadata_from_files(self, files_path):
        """Retrieve metadata from the files themselves in a given path."""
        print "Iterating in %s" % files_path
        assert os.path.exists(files_path)
        files = os.listdir(files_path)
        for image in files:
            metadata_record = self.handle_record(join(files_path, image))
            self.records.append(metadata_record)
            self.fields.update(metadata_record.get_field_names())

    def handle_record(self, items):
        """Handle a record.

        Default handling behaviour: return a new MetadataRecord
        initialised with the items as record values.

        """
        return MetadataRecord(None, items)

    def post_process_collection(self, method_mapping):
        """Call on each record its post_process method."""
        for record in self.records:
            record.metadata['categories'] = set()
            record.post_process(method_mapping, self.post_processor)
            categories = record.metadata.get('categories', None)
            record.metadata['categories'] = make_categories(categories)
            yield record

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
            for field, field_value in record.metadata.items():
                _add_to_set_dict(sets_dict, field, field_value)
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
            for field, field_value in record.metadata.items():
                _add_to_counter_dict(field_values_counters_dict,
                                     field, field_value)
        return field_values_counters_dict

    @staticmethod
    def write_dict_as_wiki(aDict, name, directory, template):
        """Write a given dictionary on disk, in template alignment format."""
        filename = os.path.join(directory, name.replace("/", ""))
        with codecs.open(filename, 'w', 'utf-8') as wikipage:
            wikipage.write("""\
{| class='wikitable' border='1'
|-
! Item
! Count
! Tag
! Categories
""")
            items = aDict.items()
            items.sort(key=lambda x: x[1], reverse=True)
            for item in items:
                try:
                    values = (template,
                            {'item': item[0], 'count': item[1],
                            'value': "", 'categories': ""})
                    table_line = ('\n' +
                                  textlib.glue_template_and_params(values))
                    wikipage.write(unicode(table_line))
                except:
                    pass
            wikipage.write("\n|}")

    def _retrieve_from_wiki(self, filename, alignment_template):
        """Retrieve the metadata mapping from a given wikipage on disk.

        Iterate over the given alignment template occurences,
        retrieve and return the mapping values.

        """

        print "retrieve_from_wiki " + filename
        wiki_file = os.path.join('wiki', filename.replace("/", ""))
        try:
            with codecs.open(wiki_file, mode='r', encoding='utf-8') as f:
                all_templates = textlib.extract_templates_and_params(f.read())
                field_mapper = dict()
                for x in all_templates:
                    if x[0] == alignment_template:
                        categories = x[1]['categories'].split(']]')[0].split(':')[-1]
                        field_mapper[x[1]['item']] = (x[1]['value'], categories)
                return field_mapper
        except Exception, e:
            print e

    def retrieve_metadata_alignments(self, fields=None,
                                     alignment_template=None):
        """Retrieve metadata alignments from disk for all given fields.

        Iterates over the given fields, determines the associate wikipage
        and calls retrieve_alignment_from_wiki on each.

        """
        if fields is None:
            fields = self.fields
        alignments = dict()
        for field in fields:
            wikipage = field
            alignments[field] = self._retrieve_from_wiki(wikipage,
                                                         alignment_template)
        self.post_processor = MetadataMapping(mapper=alignments)

    def write_metadata_to_csv(self, file_object):
        """Write the metadata collection as a CSV file."""
        writer = csv.DictWriter(file_object, self.fields)
        writer.writeheader()
        for record in self.records:
            writer.writerow(record.metadata)
