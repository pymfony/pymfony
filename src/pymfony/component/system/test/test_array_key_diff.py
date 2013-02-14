# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""
"""

from __future__ import absolute_import;

import unittest

from pymfony.component.system import Array

class TestArrayDiffKey(unittest.TestCase):

    def testBasic(self):
        array1 = {'blue' : 1, 'red': 2, 'green' : 3, 'purple' : 4};
        array2 = {'green': 5, 'blue' : 6, 'yellow': 7, 'cyan' : 8};
        self.assertEqual({"red":2,"purple":4}, Array.diffKey(array1, array2));

    def testName(self):
        input_array = {0 : '0', 1 : '1', -10 : '-10', 'True' : 1, 'False' : 0};
        boolean_indx_array = {True : 'boolt', False : 'boolf', True : 'boolT', False : 'boolF'};
        expected = {-10 :"-10","True":1,"False":0}
        self.assertEqual(expected, Array.diffKey(input_array, boolean_indx_array));


if __name__ == "__main__":
    unittest.main();
