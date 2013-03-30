# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import LogicException;

from pymfony.component.dependency.parameterbag import ParameterBag;
from pymfony.component.dependency.exception import ParameterNotFoundException;
from pymfony.component.dependency.exception import RuntimeException;
from pymfony.component.dependency.exception import ParameterCircularReferenceException;
from pymfony.component.dependency.parameterbag import FrozenParameterBag;

"""
"""

class ParameterBagTest(unittest.TestCase):

    def testConstructor(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.__construct

        """

        parameters = {
            'foo': 'foo',
            'bar': 'bar',
        };

        bag = ParameterBag(parameters);
        self.assertEqual(parameters, bag.all(), '__init__() takes an array of parameters as its first argument');


    def testClear(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.clear

        """

        parameters = {
            'foo': 'foo',
            'bar': 'bar',
        };

        bag = ParameterBag(parameters);
        bag.clear();
        self.assertEqual({}, bag.all(), '->clear() removes all parameters');


    def testRemove(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.remove

        """

        bag = ParameterBag({
            'foo': 'foo',
            'bar': 'bar',
        });
        bag.remove('foo');
        self.assertEqual({'bar': 'bar'}, bag.all(), '->remove() removes a parameter');
        bag.remove('BAR');
        self.assertEqual({}, bag.all(), '->remove() converts key to lowercase before removing');


    def testGetSet(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.get
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.set

        """

        bag = ParameterBag({'foo': 'bar'});
        bag.set('bar', 'foo');
        self.assertEqual('foo', bag.get('bar'), '->set() sets the value of a new parameter');

        bag.set('foo', 'baz');
        self.assertEqual('baz', bag.get('foo'), '->set() overrides previously set parameter');

        bag.set('Foo', 'baz1');
        self.assertEqual('baz1', bag.get('foo'), '->set() converts the key to lowercase');
        self.assertEqual('baz1', bag.get('FOO'), '->get() converts the key to lowercase');

        try:
            bag.get('baba');
            self.fail('->get() raise an InvalidArgumentException if the key does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->get() raise an InvalidArgumentException if the key does not exist');
            self.assertEqual('You have requested a non-existent parameter "baba".', e.getMessage(), '->get() raise an InvalidArgumentException if the key does not exist');



    def testHas(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.has

        """

        bag = ParameterBag({'foo': 'bar'});
        self.assertTrue(bag.has('foo'), '->has() returns True if a parameter is defined');
        self.assertTrue(bag.has('Foo'), '->has() converts the key to lowercase');
        self.assertFalse(bag.has('bar'), '->has() returns False if a parameter is not defined');


    def testResolveValue(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.resolveValue

        """

        bag = ParameterBag({});
        self.assertEqual('foo', bag.resolveValue('foo'), '->resolveValue() returns its argument unmodified if no placeholders are found');

        bag = ParameterBag({'foo': 'bar'});
        self.assertEqual('I\'m a bar', bag.resolveValue('I\'m a %foo%'), '->resolveValue() replaces placeholders by their values');
        self.assertEqual({'bar': 'bar'}, bag.resolveValue({'%foo%': '%foo%'}), '->resolveValue() replaces placeholders in keys and values of arrays');
        self.assertEqual({'bar': {'bar': {'bar': 'bar'}}}, bag.resolveValue({'%foo%': {'%foo%': {'%foo%': '%foo%'}}}), '->resolveValue() replaces placeholders in nested arrays');
        self.assertEqual('I\'m a %%foo%%', bag.resolveValue('I\'m a %%foo%%'), '->resolveValue() supports % escaping by doubling it');
        self.assertEqual('I\'m a bar %%foo bar', bag.resolveValue('I\'m a %foo% %%foo %foo%'), '->resolveValue() supports % escaping by doubling it');
        self.assertEqual({'foo': {'bar': {'ding': 'I\'m a bar %%foo %%bar'}}}, bag.resolveValue({'foo': {'bar': {'ding': 'I\'m a bar %%foo %%bar'}}}), '->resolveValue() supports % escaping by doubling it');

        bag = ParameterBag({'foo': True});
        self.assertTrue(bag.resolveValue('%foo%'), '->resolveValue() replaces arguments that are just a placeholder by their value without casting them to strings');
        bag = ParameterBag({'foo': None});
        self.assertTrue(None is bag.resolveValue('%foo%'), '->resolveValue() replaces arguments that are just a placeholder by their value without casting them to strings');

        bag = ParameterBag({'foo': 'bar', 'baz': '%%%foo% %foo%%% %%foo%% %%%foo%%%'});
        self.assertEqual('%%bar bar%% %%foo%% %%bar%%', bag.resolveValue('%baz%'), '->resolveValue() replaces params placed besides escaped %');

        bag = ParameterBag({'baz': '%%s?%%s'});
        self.assertEqual('%%s?%%s', bag.resolveValue('%baz%'), '->resolveValue() is not replacing greedily');

        bag = ParameterBag({});
        try:
            bag.resolveValue('%foobar%');
            self.fail('->resolveValue() raise an InvalidArgumentException if a placeholder references a non-existent parameter');
        except ParameterNotFoundException as e:
            self.assertEqual('You have requested a non-existent parameter "foobar".', e.getMessage(), '->resolveValue() raise a ParameterNotFoundException if a placeholder references a non-existent parameter');


        try:
            bag.resolveValue('foo %foobar% bar');
            self.fail('->resolveValue() raise a ParameterNotFoundException if a placeholder references a non-existent parameter');
        except ParameterNotFoundException as e:
            self.assertEqual('You have requested a non-existent parameter "foobar".', e.getMessage(), '->resolveValue() raise a ParameterNotFoundException if a placeholder references a non-existent parameter');


        bag = ParameterBag({'foo': 'a %bar%', 'bar': {}});
        try:
            bag.resolveValue('%foo%');
            self.fail('->resolveValue() raise a RuntimeException when a parameter embeds another non-string parameter');
        except RuntimeException as e:
            self.assertEqual('A string value must be composed of strings and/or numbers, but found parameter "bar" of type dict inside string value "a %bar%".', e.getMessage(), '->resolveValue() raise a RuntimeException when a parameter embeds another non-string parameter');


        bag = ParameterBag({'foo': '%bar%', 'bar': '%foobar%', 'foobar': '%foo%'});
        try:
            bag.resolveValue('%foo%');
            self.fail('->resolveValue() raise a ParameterCircularReferenceException when a parameter has a circular reference');
        except ParameterCircularReferenceException as e:
            self.assertEqual('Circular reference detected for parameter "foo" ("foo" > "bar" > "foobar" > "foo").', e.getMessage(), '->resolveValue() raise a ParameterCircularReferenceException when a parameter has a circular reference');


        bag = ParameterBag({'foo': 'a %bar%', 'bar': 'a %foobar%', 'foobar': 'a %foo%'});
        try:
            bag.resolveValue('%foo%');
            self.fail('->resolveValue() raise a ParameterCircularReferenceException when a parameter has a circular reference');
        except ParameterCircularReferenceException as e:
            self.assertEqual('Circular reference detected for parameter "foo" ("foo" > "bar" > "foobar" > "foo").', e.getMessage(), '->resolveValue() raise a ParameterCircularReferenceException when a parameter has a circular reference');


        bag = ParameterBag({'host': 'foo.bar', 'port': 1337});
        self.assertEqual('foo.bar:1337', bag.resolveValue('%host%:%port%'));


    def testResolveIndicatesWhyAParameterIsNeeded(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.resolve

        """

        bag = ParameterBag({'foo': '%bar%'});

        try:
            bag.resolve();
        except ParameterNotFoundException as e:
            self.assertEqual('The parameter "foo" has a dependency on a non-existent parameter "bar".', e.getMessage());


        bag = ParameterBag({'foo': '%bar%'});

        try:
            bag.resolve();
        except ParameterNotFoundException as e:
            self.assertEqual('The parameter "foo" has a dependency on a non-existent parameter "bar".', e.getMessage());



    def testResolveUnescapesValue(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.resolve

        """

        bag = ParameterBag({
            'foo': {'bar': {'ding': 'I\'m a bar %%foo %%bar'}},
            'bar': 'I\'m a %%foo%%',
        });

        bag.resolve();

        self.assertEqual('I\'m a %foo%', bag.get('bar'), '->resolveValue() supports % escaping by doubling it');
        self.assertEqual({'bar': {'ding': 'I\'m a bar %foo %bar'}}, bag.get('foo'), '->resolveValue() supports % escaping by doubling it');


    def testEscapeValue(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.escapeValue

        """

        bag = ParameterBag();

        bag.add({
            'foo': bag.escapeValue({'bar': {'ding': 'I\'m a bar %foo %bar', 'zero': None}}),
            'bar': bag.escapeValue('I\'m a %foo%'),
        });

        self.assertEqual('I\'m a %%foo%%', bag.get('bar'), '->escapeValue() escapes % by doubling it');
        self.assertEqual({'bar': {'ding': 'I\'m a bar %%foo %%bar', 'zero': None}}, bag.get('foo'), '->escapeValue() escapes % by doubling it');


    def testResolveStringWithSpacesReturnsString(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\ParameterBag.resolve
        @dataProvider stringsWithSpacesProvider

        """

        def test(expected, test, description):
            bag = ParameterBag({'foo': 'bar'});

            try:
                self.assertEqual(expected, bag.resolveString(test), description);
            except ParameterNotFoundException as e:
                self.fail('{0} - "{1}"'.format(description, expected));

        for data in self.stringsWithSpacesProvider():
            test(*data);


    def stringsWithSpacesProvider(self):

        return [
            ['bar', '%foo%', 'Parameters must be wrapped by %.'],
            ['% foo %', '% foo %', 'Parameters should not have spaces.'],
            ['{% set my_template = "foo" %}', '{% set my_template = "foo" %}', 'Twig-like strings are not parameters.'],
            ['50% is less than 100%', '50% is less than 100%', 'Text between % signs is allowed, if there are spaces.'],
        ];



class FrozenParameterBagTest(unittest.TestCase):

    def testConstructor(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\FrozenParameterBag.__construct

        """

        parameters = {
            'foo': 'foo',
            'bar': 'bar',
        };
        bag = FrozenParameterBag(parameters);
        self.assertEqual(parameters, bag.all(), '__init__() takes an array of parameters as its first argument');


    def testClear(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\FrozenParameterBag.clear
        @expectedException LogicException

        """

        try:
            bag = FrozenParameterBag({});
            bag.clear();

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException));


    def testSet(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\FrozenParameterBag.set
        @expectedException LogicException

        """

        try:
            bag = FrozenParameterBag({});
            bag.set('foo', 'bar');

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException));


    def testAdd(self):
        """
        @covers Symfony\Component\DependencyInjection\ParameterBag\FrozenParameterBag.add
        @expectedException LogicException

        """

        try:
            bag = FrozenParameterBag({});
            bag.add({});

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException));


if __name__ == '__main__':
    unittest.main();
