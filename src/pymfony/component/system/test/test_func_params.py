# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

"""
"""

class ParamsTest(unittest.TestCase):

    def setParamList(self, param = []):
        self._list = param;

        self._list.append('foo');

    def testParamList(self):
        self.setParamList();
        self.setParamList();
        self.assertEqual(self._list, ['foo', 'foo']);

    def setParamDict(self, param = {}):
        self._dict = param;
        i = 0;
        while i in self._dict:
            i += 1;
        self._dict[i] = 'foo';

    def testParamDict(self):
        self.setParamDict();
        self.setParamDict();
        self.assertEqual(self._dict, {0:'foo', 1:'foo'});


if __name__ == '__main__':
    unittest.main();
