#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""Unit tests."""

import unittest
from uploadlibrary.UploadBot import _cut_title


class TestUploadBot(unittest.TestCase):

    """Testing UploadBot methods."""

    def test_cut_title_witout_cutting(self):
        """Test _cut_title() without cutting"""
        inputs = [("", "ABC", ""),
                  ("", "ABC", " 123456789"),
                  ("1234 ", "ABC", ""),
                  ("1234 ", "ABC", " 123456789")]
        outputs = [_cut_title(*x, MAX_LENGTH=25) for x in inputs]
        expected_results = ['ABC',
                            'ABC 123456789',
                            '1234 ABC',
                            '1234 ABC 123456789']
        self.assertListEqual(outputs, expected_results)

    def test_cut_title_with_cutting(self):
        """Test _cut_title() with cutting."""
        inputs = [("1234 ", "ABC DEF G H", " 123456789"),
                  ("1234 ", "ABC DE FG H", " 123456789"),
                  ("1234 ", "ABC D E FG H", " 123456789")]
        outputs = [_cut_title(*x, MAX_LENGTH=25) for x in inputs]
        expected_results = ['1234 ABC DEF... 123456789',
                            '1234 ABC DE... 123456789',
                            '1234 ABC D E... 123456789']
        self.assertListEqual(outputs, expected_results)