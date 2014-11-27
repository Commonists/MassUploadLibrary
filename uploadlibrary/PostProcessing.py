# -*- coding: latin-1 -*-

"""Mass Upload Libray - processing metadata values."""

__authors__ = 'User:Jean-Frédéric'

import re
import os
import codecs
from collections import defaultdict
import pywikibot.textlib as textlib

def remove_linebreaks(field, old_field_value):
    new_value = old_field_value.replace('\n', ' ').replace('\r', '').replace('  ', ' ')
    return {field: new_value}

def wrap_with_template(template='fr'):
    pattern = '{{' + template + '|%s}}'
    return wrap_within_pattern_i, {'pattern': pattern}

def wrap_within_pattern(pattern='%s'):
    return wrap_within_pattern_i, {'pattern': pattern}

def wrap_within_pattern_i(field, old_field_value, pattern='%s'):
    new_value = pattern % old_field_value.replace('/', '-')
    new_field = "%s_wrapped" % field
    return {new_field: new_value, field: old_field_value}

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
        'velin': 'Vellum',
        'tissu': 'fabric'
        }
    return (split_and_apply_template_on_each, {'template': 'Technique',
                                               'mapper': support_mapper,
                                               'separator': separator
                                               })


def split_and_apply_template_on_each(field, old_field_value, template, mapper, separator=","):
    """Split the old value against the given separator and apply the template on each part"""
    bits = [x.strip().lower() for x in old_field_value.split(separator)]
    translated_bits = [mapper.get(x, x) for x in bits]
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
    try:
        DIMS_BIS = dict(zip([str(x) for x in splitted[0::3]],
                            [float(x.replace(',', '.')) for x in splitted[1::3]]))
        if len(splitted[2::3]) > 0:
            DIMS_BIS['unit'] = splitted[2::3][0]
        return {'%s_commons' % field: make_size_template(DIMS_BIS)}
        return DIMS_BIS
    except ValueError:
        return {field: old_field_value}

def make_size_template(dictionary):
    #{u'JOCONDE_DIMS_l': 77.0, u'JOCONDE_DIMS_unit': u'cm', u'JOCONDE_DIMS_H': 71.0, u'JOCONDE_DIMS_L': 191.0}
    template = "Size|unit={0[unit]}|length={0[L]}|height={0[H]}|width={0[l]}|depth={0[P]}|diameter={0[D]}|thickness={0[P]}"
    return "{{" + template.format(defaultdict(str, dictionary)) + "}}"


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


def process_with_alignment_on_list(field, old_field_value, mapper=None):
    new_value = dict()
    all_value = set()
    all_categories = set()
    for content in old_field_value:
        content = content.strip()
        (value, categories) = mapper[field].get(content, ("", []))
        if value:
            all_value.add(value)
        if categories:
            #TODO Handle several categories given in the alignment
            all_categories.add(categories)
    if all_value:
        new_value[field] = all_value
    else:
        new_value[field] = old_field_value
    new_value['categories'] = all_categories
    return new_value

def parse_categories(some_string):
    """Returns the categories contained in a string."""
    pattern = u'\[\[:?Category:(.+?)\]]'
    black_list = [u'', u'\n']
    splitted = filter(lambda a: a not in black_list,
                      re.split(pattern, some_string))
    return splitted

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
                    field = x[1]['item'].strip()
                    raw_categories = x[1]['categories']
                    categories = parse_categories(raw_categories)
                    raw_value = x[1]['value'].strip()
                    field_mapper[field] = (raw_value, categories)
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



def parse_format(field, old_field_value):
    """Parse a foramt and return the parsed."""
    new_value = parse_format_unwrapped(old_field_value)
    return {field: new_value}


def _clean_dim(dim):
    """Clean a dimension-like string"""
    return re.sub(r"\s?,\s?", '.', dim).strip()


def _pattern_to_size(m):
    """Convert the pattern matched in {{Size}}."""
    unit = 'cm'
    elements = m.groupdict()
    l = filter(None, [elements[x] for x in sorted(elements.keys())])
    s = '|'.join([_clean_dim(dim) for dim in l])
    return " {{Size|%s|%s}}" % (unit, s)


def parse_format_unwrapped(text):
    format_pattern = re.compile(r"""
        (?P<a>[\d,\.]+?)   # Digits, comma or dot, captured as group
        \s*[x×]\s*         # Whitespace, x, whitespace
        (?P<b>[\d,\.]+?)   # Same
        \s*cm?             # Whitespace until the end
        """, re.X)
    new_value = re.sub(format_pattern, _pattern_to_size, text)
    return new_value


def look_for_date(field, old_field_value):
    """Wrapper around look_for_date_unwrapped.

    Retrieve the values found by look_for_date_unwrapped
    Re-add the old_field_value to the dictionary
    Add the date and the year if they were found

    """
    (date, year) = look_for_date_unwrapped(old_field_value)
    result = {field: old_field_value}
    if date:
        result['date'] = date
    if year:
        result['year'] = year
    return result


def look_for_date_unwrapped(text):
    """Look for a date in the given text.

    Search a given string for a date pattern, using regular expressions.
    Return the date (either using the ISO YYY-MM-DD format
    or the {{Other date}} template) and the year.

    """
    monthList = {
        u'janvier': 1, u'février': 2, u'mars': 3, u'avril': 4,
        u'mai': 5, u'juin': 6, 'juillet': 7, u'août': 8,
        u'septembre': 9, u'octobre': 10, u'novembre': 11, u'décembre': 12
        }

    fullDatePattern = re.compile("""
        (?P<day>\d+?)           # Some digits
        \s?                     # Whitespace
        (?P<month>[\w]+?)       # Some letters, captured as 'month'
        \s                      # Whitespace
        (?P<year>\d{3,4})       # Three or four digits, captured
        """, re.UNICODE + re.X)
    monthDatePattern = re.compile("""
        (?P<month>\w\w\w[\w]+?)  # Some letters, captured as 'month'
        \s                       # Whitespace
        (?P<year>\d\d\d\d)       # Four digits, captured as 'year'
        """, re.UNICODE + re.X)
    circaYearPattern = re.compile("""
        Vers                    # The 'Vers' word
        \s*?                    # Maybe some whitespace
        (?P<year>\d\d\d\d)      # Four digits, captured as 'year'
        """, re.UNICODE + re.X)
    yearPattern = re.compile("""
        (?P<year>\d\d\d\d)      # Four digits, captured as 'year'
        """, re.UNICODE + re.X)
    circaDatePattern = re.compile("""
        Vers                    # The 'Vers' word
        \s                      # Whitespace
        (?P<month>\w*?)         # Some letters, captured as 'month'
        \s                      # Whitespace
        (?P<year>\d\d\d\d)      # Four digits, captured as 'year'>
        """, re.UNICODE + re.X)
    betweenDatePattern = re.compile("""
        Entre                   # The 'Entre' word
        [\s\w]*?                # Whatever words and whitespace
        \s                      # Whitespace
        (?P<year1>\d\d\d\d)     # Four digits
        \s                      # Whitespace
        et                      # The 'Et' word
        \s                      # Whitespace
        (?P<year2>\d\d\d\d)     # Four digits
        """, re.UNICODE + re.X)
    orDatePattern = re.compile("""
        (?P<year1>\d\d\d\d)
        \sou\s
        (?P<year2>\d\d\d\d)
        """, re.UNICODE + re.X)
    decadeDatePattern = re.compile("""
        Ann\wes                 # The 'Années' word
        \s                      # Whitespace
        (?P<year>\d\d\d\d)      # Four digits
        """, re.UNICODE + re.X)
    centuryPattern = re.compile("""
        (?P<qualifier>Fin)?\s?  # The 'Fin' word, possibly
        (?P<century>\d\d)       # Two digits
        e                       # The 'e' letter
        \s                      # Whitespace
        si\wcle                 # The 'Siècle' word
        """, re.UNICODE + re.X)

    fullDateR = re.search(fullDatePattern, text)
    monthDateR = re.search(monthDatePattern, text)
    circaYearR = re.search(circaYearPattern, text)
    circaDateR = re.search(circaDatePattern, text)
    betweenDateR = re.search(betweenDatePattern, text)
    orDateR = re.search(orDatePattern, text)
    decadeDateR = re.search(decadeDatePattern, text)
    centuryR = re.search(centuryPattern, text)

    if betweenDateR:
        date = u'{{Other date|between|%s|%s}}' % (betweenDateR.group('year1'),
                                                  betweenDateR.group('year2'))
        return (date, None)

    elif orDateR:
        date = u'{{Other date|or|%s|%s}}' % (orDateR.group('year1'),
                                             orDateR.group('year2'))
        return (date, None)

    elif decadeDateR:
        date = u'{{Other date|decade|%s}}' % (decadeDateR.group('year'))
        return (date, None)

    elif fullDateR:
        month = fullDateR.group('month').lower()
        if month in monthList.keys():
            monthNum = monthList[month]
            year = fullDateR.group('year')
            date = u'%s-%s-%s' % (year,
                                  '%02d' % monthList[month],
                                  '%02d' % int(fullDateR.group('day')))
            dateCategory = u"%s in " % fullDateR.group('year')
            return (date, year)
        else:
            return (None, None)

    elif circaDateR:
        month = circaDateR.group('month').lower()
        if month in monthList.keys():
            year = circaDateR.group('year')
            date = u'{{Other date|circa|%s-%s}}' % (year,
                                                    '%02d' % monthList[month])
            return (date, year)

    elif circaYearR:
        circaYear = circaYearR.group('year')
        date = u'{{Other date|circa|%s}}' % (circaYear)
        return (date, circaYear)

    elif monthDateR:
        month = monthDateR.group('month').lower()
        if month in monthList.keys():
            year = monthDateR.group('year')
            date = u'%s-%s' % (year, '%02d' % monthList[month])
            dateCategory = u"%s in " % monthDateR.group('year')
            return (date, year)
        else:
            return (None, None)

    elif centuryR:
        century = centuryR.group('century')
        date = '{{Other date|century|%s}}' % (century)

        if centuryR.groupdict()['qualifier']:
            qualifier = centuryR.group('qualifier').lower()
            table = {'fin': 'end'}
            date = u'{{Other date|%s|%s}}' % (table[qualifier], date)
        return (date, None)

    else:
        return (None, None)

