# -*- coding: latin-1 -*-

"""Mass Upload Libray - processing metadata values."""

__authors__ = 'User:Jean-Frédéric'

import re
import os
import codecs
import pywikibot.textlib as textlib

def remove_linebreaks(field, old_field_value):
    new_value = old_field_value.replace('\n', ' ').replace('\r', '').replace('  ', ' ')
    return {field: new_value}

def split_and_keep_as_list(separator=" ; "):
    """Split and make a list

    Return a dictionary of one item
    (key is field, element is the splitted values)

    """
    return split_and_keep_as_list_i, {'separator': separator}


def split_and_keep_as_list_i(field, old_field_value, separator=" ; "):
    """Split and make a list

    Return a dictionary of one item
    (key is field, element is the splitted values)

    """
    return {field: [x.strip() for x in old_field_value.split(separator)]}


def join_all(field, old_field_value, separator=" ; "):
    """Join the values together.

    Return a dictionary of one item
    (key is field, element is the values joined together)

    """
    return {field: separator.join(old_field_value)}


def map_and_apply_technique(separator=","):
    """Return a list of technique converted to use {{Technique}}."""
    support_mapper = {
        'papier': 'paper',
        'parchemin': 'parchment',
        'cire': 'wax',
        'cuir': 'leather',
        'plâtre': 'plaster',
        'bois': 'wood',
        'érable': 'maple',
        'velin': 'Vellum'
        }
    return (split_and_apply_template_on_each, {'template': 'Technique',
                                               'mapper': support_mapper,
                                               'separator': separator
                                               })


def split_and_apply_template_on_each(field, old_field_value, template, mapper, separator=","):
    """Split the old value against the given separator and apply the template on each part"""
    bits = old_field_value.split(separator)
    translated_bits = [mapper.get(x.strip(), x.strip()) for x in bits]
    new_value = ', '.join(["{{%s|%s}}" % (template, x) for x in translated_bits])
    return {field: new_value}


def process_DIMS(field, old_field_value):
    """Process the Joconde DIMS field.

    Split the field by each dimension
    Build a dictionary with it
    Return the dictionary

    """
    DIMS = old_field_value
    pattern = '(\w+?)[\.:]\s?([\d,]*)\s?(\w*)\s?;?\s?'
    splitted = filter(lambda a: a != u'', re.split(pattern, DIMS))
    DIMS_BIS = dict(zip(["_".join([field, x]) for x in splitted[0::3]],
                        [float(x.replace(',', '.')) for x in splitted[1::3]]))
    if len(splitted[2::3]) > 0:
        DIMS_BIS["_".join([field, 'unit'])] = splitted[2::3][0]
    return DIMS_BIS


def make_categories(categories):
    """Build the wikitext for a given list of category names."""
    return "\n".join(["[[Category:%s]]" % x for x in categories])


def process_with_alignment(field, old_field_value, mapper=None):
    """Retrieve the alignment for a given record contents."""
    new_value = dict()
    (value, categories) = mapper[field].get(old_field_value, ("", []))
    if value:
        new_value[field] = value
    else:
        new_value[field] = old_field_value
    if categories:
        new_value['categories'] = categories
    return new_value


def _retrieve_from_wiki(filename, alignment_template):
    """Retrieve a metadata mapping from a given wikipage on disk.

    Iterate over the given alignment template occurences,
    retrieve and return the mapping values.

    """

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


def retrieve_metadata_alignments(fields, alignment_template):
    """Retrieve metadata alignments from disk for all given fields.

    Iterates over the given fields, determines the associate wikipage
    and calls retrieve_alignment_from_wiki on each.

    """

    alignments = dict()
    for field in fields:
        wikipage = field
        alignments[field] = _retrieve_from_wiki(wikipage, alignment_template)
    return alignments
