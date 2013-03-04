#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import unittest;
import inspect;

from pymfony.component.system.exception import StandardException;

"""
"""

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
        self.assertEqual(e.getLineno(), 26);
        self.assertEqual(e.getFile(), currentFile);

        self.assertEqual(e.getTrace()[0]['name'], "__raiseException");
        self.assertEqual(str(e.getTrace()[0]['locals']['e']), 'Basic exception message');


    def testFormatStack(self):
        stack = {
            'filename' : "file",
            'lineno'   : 10,
            'name'     : "functionName",
            'line'     : 'raise Exception()',
            'locals'   : {'arg1': repr(None)},
            'argcount' : 1,
        };

        stackFormated = StandardException.STACK_PATTERN.format(**stack);

        expected = stackFormated + ", with (arg1='None')";
        self.assertEqual(self.__e._formatStack(stack), expected);

    def testToString(self):
        str(self.__e);

if __name__ == "__main__":
    unittest.main();
