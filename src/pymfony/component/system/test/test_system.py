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

from pymfony.component.system import Tool;
from pymfony.component.system import Object;
from pymfony.component.system import CloneBuilder;
from pymfony.component.system import ClassLoader;
from pymfony.component.system import SourceFileLoader;
from pymfony.component.system.reflection import ReflectionObject;
from pymfony.component.system.types import OrderedDict;

"""
"""

class TestReflextion(unittest.TestCase, Object):
    def setUp(self):
        self.subject = ReflectionObject(self);

    def testConstructor(self):
        self.assertEqual(self.subject._class, self.__class__);

    def testGetFileName(self):
        self.assertEqual(
            inspect.getabsfile(self.__class__),
            self.subject.getFileName()
        );

    def testGetmro(self):
        self.assertEqual(self.__class__.__mro__, self.subject.getmro());

class TestTool(unittest.TestCase):
    def testStripcslashes(self):
        self.assertEqual(Tool.stripcslashes('\H\e\l\l\o \W\or\l\d'), "Hello World")
        self.assertEqual(Tool.stripcslashes('Hello World\\r\\n'), 'Hello World\r\n')
        self.assertEqual(Tool.stripcslashes('\x48\x65\x6c\x6c\x6f \x57\x6f\x72\x6c\x64'), "Hello World")
        self.assertEqual(Tool.stripcslashes('\110\145\154\154\157 \127\157\162\154\144'), "Hello World")

class CloneBuilderTest(unittest.TestCase):
    def testBuild(self):
        self._orderdedDict = OrderedDict();
        clone = CloneBuilder.build(self);
        self.assertFalse(self is clone);
        self.assertFalse(self._orderdedDict is clone._orderdedDict);
        self.assertEqual(self._orderdedDict, clone._orderdedDict);
        self.assertFalse(self.testBuild is clone.testBuild);


class ClassLoaderTest(unittest.TestCase):
    def testLoad(self):
        ClassLoader.load('os.path').sep;
        self.assertEqual(ClassLoader.load('Exception'), Exception);


class SourceFileLoaderTest(unittest.TestCase):
    def testLoad(self):
        SourceFileLoader.load(inspect.getabsfile(self.__class__)).SourceFileLoaderTest;


if __name__ == "__main__":
    unittest.main();
