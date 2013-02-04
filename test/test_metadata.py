#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""Unit tests."""

import unittest
import pickle
from os.path import join, dirname
from uploadlibrary.metadata import MetadataRecord


class TestRecord(unittest.TestCase):

    """Testing methods from MetadataRecord."""

    @classmethod
    def setUpClass(cls):
        """Retrieve the record from disk by deserialiazation."""
        values = {'A': 'a', 'B': 'b'}
        dummy_record = MetadataRecord(**values)
        cls.records = [dummy_record]

    def test_init(self):
        """Test __init__."""
        values = {'A': 'a'}
        record = MetadataRecord(**values)
        self.assertEqual(record.__dict__, values)

    def test_to_template(self):
        """Test to_template."""
        expected_result = u'{{Dummy\n|A=a\n|B=b\n}}'
        self.assertEqual(expected_result,
                         self.records[-1].to_template(template='Dummy'))


if __name__ == "__main__":
    unittest.main()
