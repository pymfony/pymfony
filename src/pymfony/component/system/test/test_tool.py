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

import unittest;

from pymfony.component.system.tool import Convert;

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
            response = Convert.str2Int(value);
            self.assertEqual(response, expect);

if __name__ == '__main__':
    unittest.main();