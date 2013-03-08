# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.system.reflection import ReflectionObject;

"""
"""

class ReflectionObjectEx(ReflectionObject):
    def __init__(self, argument):
        ReflectionObject.__init__(self, argument);

        self.bla = None;

    def getMethodNames(self):
        res = list();
        for m in self.getMethods():
            res.append(m.getClassName() + '.' + m.getName());

        return res;

class ReflexionObjectTest(unittest.TestCase):
    def setUp(self):
        self._obj = ReflectionObjectEx(self);
        self._ref = ReflectionObjectEx(self._obj);

    def testGetMethods(self):
        names = [
            '__init__',
            'exists',
            'getFileName',
            'getMethod',
            'getMethodNames',
            'getMethods',
            'getName',
            'getNamespaceName',
            'getParentClass',
            'getmro',
            'newInstance',
        ];

        exp = list();
        for name in names:
            exp.append(self._ref.getName() + '.' + name);

        res = self._ref.getMethodNames();

        miss = list();
        for m in exp:
            if m not in res:
                miss.append(m);

        self.assertFalse(miss, res);

if __name__ == '__main__':
    unittest.main();
