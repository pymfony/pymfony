# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.system.types import Convert;
from pymfony.component.system.types import Array;

"""
"""

class ConvertTest(unittest.TestCase):
    def testStr2Int(self):
        data = [
            ("10.5", 10),
            ("-1.3e3", -1300),
            ("bob-1.3e3", 0),
            ("bob3", 0),
            ("11 Small Pigs", 11),
            ("12.2 Little Piggies", 12),
            ("13.0 pigs ", 13),
        ];
        for value, expect in data:
            response = Convert.str2int(value);
            self.assertEqual(response, expect);

class ArrayTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testUniq(self):
        in_lst = ["B", "A", "B", "a", "1", "b", "/", "", "2"];
        expected = ["B", "A", "a", "1", "b", "/", "", "2"];
        result = Array.uniq(in_lst);
        self.assertEqual(result, expected);

        in_lst = {"B":0, "A":1, "B":0, "a":2, "1":3, "b":4, "/":5, "":"d", "2":6};
        expected = {"B":0, "A":1, "a":2, "1":3, "b":4, "/":5, "":"d", "2":6};
        result = Array.uniq(in_lst);
        self.assertEqual(result, expected);

    def testDiffKeyBasic(self):
        array1 = {'blue' : 1, 'red': 2, 'green' : 3, 'purple' : 4};
        array2 = {'green': 5, 'blue' : 6, 'yellow': 7, 'cyan' : 8};
        self.assertEqual({"red":2,"purple":4}, Array.diffKey(array1, array2));

    def testDiffKeyName(self):
        input_array = {0 : '0', 1 : '1', -10 : '-10', 'True' : 1, 'False' : 0};
        boolean_indx_array = {True : 'boolt', False : 'boolf', True : 'boolT', False : 'boolF'};
        expected = {-10 :"-10","True":1,"False":0}
        self.assertEqual(expected, Array.diffKey(input_array, boolean_indx_array));


if __name__ == '__main__':
    unittest.main();
