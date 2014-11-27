# -*- coding: latin-1 -*-

"""Mass Upload Libray − handling metadata."""

__authors__ = 'User:Jean-Frédéric'
import sys
import pickle
import codecs
import csv
import os
import re
from xml.dom import minidom
from os.path import join
from collections import Counter
from lxml import etree
from uploadlibrary import UnicodeCSV
import pywikibot.textlib as textlib
from scripts.data_ingestion import Photo
from uploadlibrary.PostProcessing import make_categories

class UnreadableRecordException(Exception):
    pass

class MetadataRecord(Photo):

    """Represent a Record, with its associated metadata."""

    def get_field_names(self):
        """Return the field values from the records."""
        return self.metadata.keys()

    def post_process(self, method_mapping):
        """Post-process the MetadataRecord with a method in the given mapping.

        For each field of the record,
        call the relevant post-processing method.

        """
        for field in self.metadata.keys():
            if field in method_mapping.keys():
                self.post_process_wrapper(field, method_mapping[field])

    def post_process_wrapper(self, field, method_info):
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
        (method, kwargs) = method_info
        new_field_value = method(field, old_field_value, **kwargs)
        categories = new_field_value.pop('categories', None)
        if categories:
            try:
                self.metadata['categories'].add(categories)
            except:
                self.metadata['categories'].update(categories)
        _smart_update_dict(self.metadata, new_field_value)

    def to_template(self, template=u'Ingestion layout'):
        """Return the Record as a MediaWiki template."""
        return textlib.glue_template_and_params((template,
                                                 self.__dict__))

    def to_xml(self):
        """Return the Record as an XML Element."""
        record_element = etree.Element('record')
        params = self.metadata
        for field, value in params.items():
            field = re.sub(' ', '_', field)
            field = re.sub(':', '-', field)
            field = re.sub('/', '-', field)
            if isinstance(value, set) or isinstance(value, list):
                for index, item in enumerate(value, start=1):
                    name = field + '_' + str(index)
                    field_element = etree.SubElement(record_element, name)

                    try:
                        field_element.text = item
                    except ValueError:
                        field_element.text = item.encode('utf-8')
            else:
                field_element = etree.SubElement(record_element, unicode(field))
                try:
                    field_element.text = value
                except TypeError:
                    field_element.text = str(value)
                except ValueError:
                    #field_element.text = value.encode('utf-8')
                    #field_element.text = unicode(value)
                    field_element.text = "REDACTED"
                    pass
        return record_element

    def to_disk(self, title_format, directory):
        """Write the Record on disk in a given repository.

        Serialise the record and name following the given format,
        do nothing if anything goes wrong.

        """
        file_name = join(directory, self.getTitle(title_format) + '.dump')
        try:
            with open(file_name, 'w') as f:
                pickle.dump(self, f)
        except Exception, e:
            print "Could not pickle record %s \n %s" % (file_name, e)


class MetadataCollection(object):

    """Processing a metadata collection in various ways."""

    def __init__(self):
        """Constructor."""
        self.records = []
        self.fields = set()

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
            try:
                metadata_record = self.handle_record(join(files_path, image))
                self.records.append(metadata_record)
                self.fields.update(metadata_record.get_field_names())
            except UnreadableRecordException as e:
                print "Skip record, could not read"
                continue

    def retrieve_metadata_from_xml(self, xml_file, element_root):
        """Retrieve metadata from the given XML file."""
        xmldoc = minidom.parse(xml_file)
        for item in xmldoc.getElementsByTagName(element_root):
            try:
                metadata_record = self.handle_record(item)
                self.records.append(metadata_record)
                self.fields.update(metadata_record.get_field_names())
            except UnreadableRecordException as e:
                #print "Skip record, could not read"
                continue

    def handle_record(self, items):
        """Handle a record.

        Default handling behaviour: return a new MetadataRecord
        initialised with the items as record values.

        """
        return MetadataRecord(None, items)

    def get_metadata_from_xml_element(self, xml_elements):
        """Return a metadata dictionary by parsing the given XML element children"""
        elements = [child for child in xml_elements.childNodes
                    if isinstance(child, minidom.Element)]
        image_metadata = {}
        for element in elements:
            key = element.nodeName
            try:
                value = element.childNodes.item(0).data.strip()
            except AttributeError:
                value = ''
            try:
                image_metadata[key] = value.decode('utf-8').strip()
            except:
                try:
                    image_metadata[key] = value.decode('latin-1').strip()
                except:
                    image_metadata[key] = value
        return image_metadata

    def post_process_collection(self, method_mapping):
        """Call on each record its post_process method."""
        categories_counter = Counter()
        categories_count_per_file = Counter()
        for record in self.records:
            record.metadata['categories'] = set()
            record.post_process(method_mapping)
            categories = record.metadata.get('categories', None)
            categories_counter.update(categories)
            categories_count_per_file[record.URL] = len(categories)
            #record.metadata['categories'] = make_categories(categories)

        return categories_counter, categories_count_per_file

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

    def write_metadata_to_csv(self, file_object):
        """Write the metadata collection as a CSV file."""
        writer = csv.DictWriter(file_object, self.fields)
        writer.writeheader()
        for record in self.records:
            writer.writerow(record.metadata)

    def write_metadata_to_xml(self, file_object):
        """Write the metadata collection as an XML file."""
        records_element = etree.Element("records")
        for record in self.records:
            records_element.append(record.to_xml())
        tree = etree.ElementTree(records_element)
        tree.write(file_object, encoding='utf-8', pretty_print=True)


def categorisation_statistics(all_categories, categories_count_per_file):
    """Computes statistics on the categorisation."""
    numpy_available = True
    try:
        import numpy
    except ImportError:
        numpy_available = False
    text = list()
    text.append("= Categoriation statistics =")
    text.append("== Per category ==")
    text.append("The collection has {0:d} categories, {1:d} distinct ones".format(sum(all_categories.values()),
                                                                                  len(all_categories)))
    try:
        text.append("The most used category is on {0:d} files".format(max(all_categories.values())))
        text.append("The less used on {0:d} files".format(min(all_categories.values())))
    except ValueError:
        pass
    if numpy_available:
        text.append("On average, a category is used {0:.1f} times (mean)".format(numpy.mean(all_categories.values())))
        text.append("The median is: {0:.1f}".format(numpy.median(all_categories.values())))
    text.append("The 10 most used categories are:")
    text.append(" - ".join([unicode(x[0]) + ' - ' + unicode(x[1])
                            for x in all_categories.most_common(10)]))
    text.append("The 10 less used categories are:")
    text.append(" - ".join([unicode(x[0]) + ' - ' + unicode(x[1])
                            for x in all_categories.most_common()[-10:]]))

    text.append("== Per file ==")
    text.append("The most categorized file has {0:d} categories".format(max(categories_count_per_file.values())))
    text.append("The less categorized file has {0:d} categories".format(min(categories_count_per_file.values())))
    text.append("We have {0:d} uncategorized files".format(len([x for x in categories_count_per_file
                                                           if categories_count_per_file[x] is 0])))
    more_than_two = len([x for x in categories_count_per_file
                         if categories_count_per_file[x] >= 2])
    more_than_two_percentage = float(more_than_two) / len(categories_count_per_file) * 100
    text.append("We have {0:d} files with two categories or more, which makes {1:.1f}%".format(more_than_two,
                                                                                               more_than_two_percentage))
    if numpy_available:
        text.append("On average, a file has {0:.1f} categories (mean)".format(numpy.mean(categories_count_per_file.values())))
        text.append("The median is: {0:.1f}".format(numpy.median(categories_count_per_file.values())))
    return '\n'.join(text)
