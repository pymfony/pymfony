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

from pymfony.component.system import Array;
from pymfony.component.system import Tool;
from pymfony.component.system import Object, abstract;
from pymfony.component.system import final;
from pymfony.component.system import interface
from pymfony.component.system import ReflectionObject;
from pymfony.component.system import CloneBuilder;

"""
"""

class TestArray(unittest.TestCase):
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

@interface
class ClassInterface(Object):
    def method(self):
        pass;

class CommonClass(ClassInterface):
    pass;

@abstract
class AbstractClass(Object):
    def method(self):
        pass;

class AbstractMethod(AbstractClass):
    @abstract
    def method(self):
        pass;

@final
class FinalClass(Object):
    def method(self):
        pass;



class FinalMethod(Object):
    @final
    def method(self):
        pass;

class ChildFinalMethod(FinalMethod):
    pass;



class RegularClass(AbstractMethod):
    def method(self):
        AbstractClass.method(self);

class TestMetaclass(unittest.TestCase):
    def testGlobals(self):
        self.assertRaises(
            AttributeError,
            lambda args: args['self'].__metaclass__,
            locals()
        );

    def testAbstract(self):
        self.assertFalse(Tool.isAbstract(type(self)));
        self.assertTrue(Tool.isAbstract(Object));

    def testAbstractClass(self):
        self.assertTrue(Tool.isAbstract(AbstractClass));

    def testAbstractMethod(self):
        self.assertTrue(Tool.isAbstract(AbstractMethod));
        self.assertRaises(TypeError, lambda:AbstractMethod().method());

    def testRegularClass(self):
        self.assertFalse(Tool.isAbstract(RegularClass));
        RegularClass().method();

    def testInstance(self):
        inst = RegularClass();
        self.assertTrue(isinstance(inst, RegularClass));
        self.assertTrue(isinstance(inst, AbstractClass));
        self.assertTrue(isinstance(inst, Object));
        self.assertTrue(isinstance(inst, object));

    def testInterface(self):
        expected = frozenset(['method']);
        self.assertEqual(CommonClass.__interfacemethods__, expected);
        self.assertRaises(TypeError, lambda:CommonClass().method());

    def testFinalClass(self):
        instance = FinalClass();
        self.assertTrue(isinstance(instance, FinalClass));
        def badCall():
            class ChildFinalClass(FinalClass):
                pass;
        self.assertRaises(TypeError, badCall);

    def testFinalMethod(self):
        instance = ChildFinalMethod();
        self.assertTrue(isinstance(instance, ChildFinalMethod));
        self.assertTrue(isinstance(instance, FinalMethod));
        def badCall():
            class BadChildFinalMethod(FinalMethod):
                def method(self):
                    pass;
        self.assertRaises(TypeError, badCall);

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
        self.assertFalse(self is CloneBuilder.build(self));

if __name__ == "__main__":
    unittest.main();
