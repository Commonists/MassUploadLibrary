# -*- coding: latin-1 -*-

"""Mass Upload Libray − processing metadata values."""

__authors__ = 'User:Jean-Frédéric'

import re

"""Post processing Record values."""


def join_all(field, old_field_value, separator=" ; "):
    """Join the values together.

    Return a dictionary of one item
    (key is field, element is the values joined together)

    """
    return {field: separator.join(old_field_value)}


def process_DIMS(field, old_field_value):
    """Process the Joconde DIMS field.

    Split the field by each dimension
    Build a dictionary with it
    Return the dictionary

    """
    DIMS = old_field_value
    print DIMS
    pattern = '(\w+?)[\.:]\s?([\d,]*)\s?(\w*)\s?;?\s?'
    splitted = filter(lambda a: a != u'', re.split(pattern, DIMS))
    DIMS_BIS = dict(zip(["_".join([field, x]) for x in splitted[0::3]],
                        [float(x.replace(',', '.')) for x in splitted[1::3]]))
    if len(splitted[2::3]) > 0:
        DIMS_BIS["_".join([field, 'unit'])] = splitted[2::3][0]
    return DIMS_BIS
