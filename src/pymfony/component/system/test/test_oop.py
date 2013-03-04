# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.system.oop import interface;
from pymfony.component.system.oop import abstract;
from pymfony.component.system.oop import final;
from pymfony.component.system import Object;
from pymfony.component.system import Tool;
from pymfony.component.system import OOPObject;

"""
"""

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
        self.assertTrue(Tool.isAbstract(OOPObject));

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

if __name__ == '__main__':
    unittest.main();

