#!/usr/bin/python
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
import inspect

from pymfony.component.system.exception import StandardException

class StandardExceptionTest(unittest.TestCase):

    def __raiseException(self, arg1=None, arg2=list()):
        try:
            try:
                raise Exception('Basic exception message');
            except Exception as e:
                raise StandardException("Standard exception message", 1, e);
        except StandardException as e:
            return e;

    def setUp(self):
        self.__e = self.__raiseException();

    def testConstructor(self):
        e = self.__e;
        currentFile = inspect.getsourcefile(self.__class__)
        self.assertEqual(e.getMessage(), "Standard exception message");
        self.assertEqual(e.getCode(), 1);
        self.assertTrue(isinstance(e.getPrevious(), (BaseException, type(None))));
        self.assertEqual(e.getLine(), 26);
        self.assertEqual(e.getFile(), currentFile);
        expectedLocals = {
            'arg1': 'None',
            'arg2': '[]',
            'e': "Exception('Basic exception message',)",
            'self': repr(self),
        };

        self.assertEqual(e._function, "__raiseException");
        self.assertEqual(e._locals, expectedLocals);

        stack = {
            'file'     : "filename",
            'line'     : "10",
            'function' : "functionName",
            'locals'   : {'arg1': repr(None)},
        };
        expected = '#0 filename(10): functionName()\n';
        self.assertEqual(e._formatStack("0", stack), expected);

    def testToString(self):
        self.__e.__str__();

if __name__ == "__main__":
    unittest.main();
