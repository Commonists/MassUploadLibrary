#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""Unit tests."""

import unittest
from uploadlibrary.PostProcessing import join_all, process_DIMS


class TestRecord(unittest.TestCase):

    """Testing methods from Record."""

    def test_join_all(self):
        """Test join_all"""
        name = 'Res'
        values = ['A', 'B', 'C']
        expected_result = {name: 'A ; B ; C'}
        self.assertEqual(expected_result,
                         join_all(name, values))

    def test_process_DIMS(self):
        """Test process_DIMS"""
        input_values = ['L. 53 cm ; l. 26 cm ; E. 11 cm',
                        'L: 53 cm ; l: 32 cm ; h: 11 cm',
                        'Diam: 20 cm ; h: 10 cm',
                        ]
        expected_values = [{u'JOCONDE_DIMS_unit': u'cm',
                            u'JOCONDE_DIMS_L': 53.0,
                            u'JOCONDE_DIMS_l': 26.0,
                            u'JOCONDE_DIMS_E': 11.0},
                           {u'JOCONDE_DIMS_unit': u'cm',
                            u'JOCONDE_DIMS_L': 53.0,
                            u'JOCONDE_DIMS_l': 32.0,
                            u'JOCONDE_DIMS_h': 11.0},
                            {}]
        output_values = map(lambda x: process_DIMS(*x),
                            zip(['JOCONDE_DIMS'] * 3, input_values))
        toto = zip(output_values, expected_values)
        for (out, expected) in toto:
            print out
            print expected
            self.assertEqual(out, expected)


if __name__ == "__main__":
    unittest.main()
