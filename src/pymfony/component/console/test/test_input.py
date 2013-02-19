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
import os
import sys

from pymfony.component.system.exception import RuntimeException
from pymfony.component.system.exception import InvalidArgumentException
from pymfony.component.system.exception import LogicException
from pymfony.component.console.input import ArrayInput
from pymfony.component.console.input import InputDefinition
from pymfony.component.console.input import InputArgument
from pymfony.component.console.input import InputOption
from pymfony.component.console.input import StringInput
from pymfony.component.console.input import ArgvInput

class StringInputTest(unittest.TestCase):

    def testTokenize(self):
        """@dataProvider: getTokenizeData

        """

        for inputString, tokens, message in self.getTokenizeData():
            inputString = StringInput(inputString);
            self.assertEqual(tokens, inputString._ArgvInput__tokens, message);


    def getTokenizeData(self):

        return [
            ('', [], '->tokenize() parses an empty string'),
            ('foo', ['foo'], '->tokenize() parses arguments'),
            ('  foo  bar  ', ['foo', 'bar'], '->tokenize() ignores whitespaces between arguments'),
            ('"quoted"', ['quoted'], '->tokenize() parses quoted arguments'),
            ("'quoted'", ['quoted'], '->tokenize() parses quoted arguments'),
            (r'\"quoted\"', ['"quoted"'], '->tokenize() parses escaped-quoted arguments'),
            (r"\'quoted\'", ['\'quoted\''], '->tokenize() parses escaped-quoted arguments'),
            ('-a', ['-a'], '->tokenize() parses short options'),
            ('-azc', ['-azc'], '->tokenize() parses aggregated short options'),
            ('-awithavalue', ['-awithavalue'], '->tokenize() parses short options with a value'),
            ('-a"foo bar"', ['-afoo bar'], '->tokenize() parses short options with a value'),
            ('-a"foo bar""foo bar"', ['-afoo barfoo bar'], '->tokenize() parses short options with a value'),
            ('-a\'foo bar\'', ['-afoo bar'], '->tokenize() parses short options with a value'),
            ('-a\'foo bar\'\'foo bar\'', ['-afoo barfoo bar'], '->tokenize() parses short options with a value'),
            ('-a\'foo bar\'"foo bar"', ['-afoo barfoo bar'], '->tokenize() parses short options with a value'),
            ('--long-option', ['--long-option'], '->tokenize() parses long options'),
            ('--long-option=foo', ['--long-option=foo'], '->tokenize() parses long options with a value'),
            ('--long-option="foo bar"', ['--long-option=foo bar'], '->tokenize() parses long options with a value'),
            ('--long-option="foo bar""another"', ['--long-option=foo baranother'], '->tokenize() parses long options with a value'),
            ('--long-option=\'foo bar\'', ['--long-option=foo bar'], '->tokenize() parses long options with a value'),
            ("--long-option='foo bar''another'", ["--long-option=foo baranother"], '->tokenize() parses long options with a value'),
            ("--long-option='foo bar'\"another\"", ["--long-option=foo baranother"], '->tokenize() parses long options with a value'),
            ('foo -a -ffoo --long bar', ['foo', '-a', '-ffoo', '--long', 'bar'], '->tokenize() parses when several arguments and options'),
        ];



class InputTest(unittest.TestCase):

    def testConstructor(self):

        inputv = ArrayInput({'name': 'foo'}, InputDefinition([InputArgument('name')]));
        self.assertEqual('foo', inputv.getArgument('name'), '->__init__() takes a InputDefinition as an argument');


    def testOptions(self):

        inputv = ArrayInput({'--name': 'foo'}, InputDefinition([InputOption('name')]));
        self.assertEqual('foo', inputv.getOption('name'), '->getOption() returns the value for the given option');

        inputv.setOption('name', 'bar');
        self.assertEqual('bar', inputv.getOption('name'), '->setOption() sets the value for a given option');
        self.assertEqual({'name': 'bar'}, inputv.getOptions(), '->getOptions() returns all option values');

        inputv = ArrayInput({'--name': 'foo'}, InputDefinition([InputOption('name'), InputOption('bar', '', InputOption.VALUE_OPTIONAL, '', 'default')]));
        self.assertEqual('default', inputv.getOption('bar'), '->getOption() returns the default value for optional options');
        self.assertEqual({'name': 'foo', 'bar': 'default'}, inputv.getOptions(), '->getOptions() returns all option values, even optional ones');

        try:
            inputv.setOption('foo', 'bar');
            self.fail('->setOption() raise a InvalidArgumentException if the option does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->setOption() raise a InvalidArgumentException if the option does not exist');
            self.assertEqual('The "foo" option does not exist.', e.getMessage());


        try:
            inputv.getOption('foo');
            self.fail('->getOption() raise a InvalidArgumentException if the option does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->setOption() raise a InvalidArgumentException if the option does not exist');
            self.assertEqual('The "foo" option does not exist.', e.getMessage());



    def testArguments(self):

        inputv = ArrayInput({'name': 'foo'}, InputDefinition([InputArgument('name')]));
        self.assertEqual('foo', inputv.getArgument('name'), '->getArgument() returns the value for the given argument');

        inputv.setArgument('name', 'bar');
        self.assertEqual('bar', inputv.getArgument('name'), '->setArgument() sets the value for a given argument');
        self.assertEqual({'name': 'bar'}, inputv.getArguments(), '->getArguments() returns all argument values');

        inputv = ArrayInput({'name': 'foo'}, InputDefinition([InputArgument('name'), InputArgument('bar', InputArgument.OPTIONAL, '', 'default')]));
        self.assertEqual('default', inputv.getArgument('bar'), '->getArgument() returns the default value for optional arguments');
        self.assertEqual({'name': 'foo', 'bar': 'default'}, inputv.getArguments(), '->getArguments() returns all argument values, even optional ones');

        try:
            inputv.setArgument('foo', 'bar');
            self.fail('->setArgument() raise a InvalidArgumentException if the argument does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->setOption() raise a InvalidArgumentException if the option does not exist');
            self.assertEqual('The "foo" argument does not exist.', e.getMessage());


        try:
            inputv.getArgument('foo');
            self.fail('->getArgument() raise a InvalidArgumentException if the argument does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->setOption() raise a InvalidArgumentException if the option does not exist');
            self.assertEqual('The "foo" argument does not exist.', e.getMessage());



    def testValidate(self):

        inputv = ArrayInput(dict());
        inputv.bind(InputDefinition([InputArgument('name', InputArgument.REQUIRED)]));

        try:
            inputv.validate();
            self.fail('->validate() raise a RuntimeException if not enough arguments are given');
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException), '->validate() raise a RuntimeException if not enough arguments are given');
            self.assertEqual('Not enough arguments.', e.getMessage());


        inputv = ArrayInput({'name': 'foo'});
        inputv.bind(InputDefinition([InputArgument('name', InputArgument.REQUIRED)]));

        try:
            inputv.validate();
        except RuntimeException as e:
            self.fail('->validate() does not raise a RuntimeException if enough arguments are given');



    def testSetGetInteractive(self):

        inputv = ArrayInput(dict());
        self.assertTrue(inputv.isInteractive(), '->isInteractive() returns whether the input should be interactive or not');
        inputv.setInteractive(False);
        self.assertFalse(inputv.isInteractive(), '->setInteractive() changes the interactive flag');



class InputOptionTest(unittest.TestCase):

    def testConstructor(self):

        option = InputOption('foo');
        self.assertEqual('foo', option.getName(), '__init__() takes a name as its first argument');
        option = InputOption('--foo');
        self.assertEqual('foo', option.getName(), '__init__() removes the leading -- of the option name');

        try:
            option = InputOption('foo', 'f', InputOption.VALUE_IS_ARRAY);
            self.fail('__init__() raise an InvalidArgumentException if VALUE_IS_ARRAY option is used when an option does not accept a value');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '__init__() raise an InvalidArgumentException if VALUE_IS_ARRAY option is used when an option does not accept a value');
            self.assertEqual('Impossible to have an option mode VALUE_IS_ARRAY if the option does not accept a value.', e.getMessage());


        # shortcut argument
        option = InputOption('foo', 'f');
        self.assertEqual('f', option.getShortcut(), '__init__() can take a shortcut as its second argument');
        option = InputOption('foo', '-f');
        self.assertEqual('f', option.getShortcut(), '__init__() removes the leading - of the shortcut');
        option = InputOption('foo');
        self.assertTrue(option.getShortcut() is None, '__init__() makes the shortcut None by default');

        # mode argument
        option = InputOption('foo', 'f');
        self.assertFalse(option.acceptValue(), '__init__() gives a "InputOption.VALUE_NONE" mode by default');
        self.assertFalse(option.isValueRequired(), '__init__() gives a "InputOption.VALUE_NONE" mode by default');
        self.assertFalse(option.isValueOptional(), '__init__() gives a "InputOption.VALUE_NONE" mode by default');

        option = InputOption('foo', 'f', None);
        self.assertFalse(option.acceptValue(), '__init__() can take "InputOption.VALUE_NONE" as its mode');
        self.assertFalse(option.isValueRequired(), '__init__() can take "InputOption.VALUE_NONE" as its mode');
        self.assertFalse(option.isValueOptional(), '__init__() can take "InputOption.VALUE_NONE" as its mode');

        option = InputOption('foo', 'f', InputOption.VALUE_NONE);
        self.assertFalse(option.acceptValue(), '__init__() can take "InputOption.VALUE_NONE" as its mode');
        self.assertFalse(option.isValueRequired(), '__init__() can take "InputOption.VALUE_NONE" as its mode');
        self.assertFalse(option.isValueOptional(), '__init__() can take "InputOption.VALUE_NONE" as its mode');

        option = InputOption('foo', 'f', InputOption.VALUE_REQUIRED);
        self.assertTrue(option.acceptValue(), '__init__() can take "InputOption.VALUE_REQUIRED" as its mode');
        self.assertTrue(option.isValueRequired(), '__init__() can take "InputOption.VALUE_REQUIRED" as its mode');
        self.assertFalse(option.isValueOptional(), '__init__() can take "InputOption.VALUE_REQUIRED" as its mode');

        option = InputOption('foo', 'f', InputOption.VALUE_OPTIONAL);
        self.assertTrue(option.acceptValue(), '__init__() can take "InputOption.VALUE_OPTIONAL" as its mode');
        self.assertFalse(option.isValueRequired(), '__init__() can take "InputOption.VALUE_OPTIONAL" as its mode');
        self.assertTrue(option.isValueOptional(), '__init__() can take "InputOption.VALUE_OPTIONAL" as its mode');

        try:
            option = InputOption('foo', 'f', 'ANOTHER_ONE');
            self.fail('__init__() raise an InvalidArgumentException if the mode is not valid');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '__init__() raise an InvalidArgumentException if the mode is not valid');
            self.assertEqual('Option mode "ANOTHER_ONE" is not valid.', e.getMessage());

        try:
            option = InputOption('foo', 'f', -1);
            self.fail('__init__() raise an InvalidArgumentException if the mode is not valid');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '__init__() raise an InvalidArgumentException if the mode is not valid');
            self.assertEqual('Option mode "-1" is not valid.', e.getMessage());



    def testEmptyNameIsInvalid(self):
        """@expectedException InvalidArgumentException

        """

        self.assertRaises(InvalidArgumentException, InputOption, '');


    def testDoubleDashNameIsInvalid(self):
        """@expectedException InvalidArgumentException

        """

        self.assertRaises(InvalidArgumentException, InputOption, '--');


    def testSingleDashOptionIsInvalid(self):
        """@expectedException InvalidArgumentException

        """

        self.assertRaises(InvalidArgumentException, InputOption, 'foo', '-');


    def testIsArray(self):

        option = InputOption('foo', None, InputOption.VALUE_OPTIONAL | InputOption.VALUE_IS_ARRAY);
        self.assertTrue(option.isArray(), '->isArray() returns True if the option can be an array');
        option = InputOption('foo', None, InputOption.VALUE_NONE);
        self.assertFalse(option.isArray(), '->isArray() returns False if the option can not be an array');


    def testGetDescription(self):

        option = InputOption('foo', 'f', None, 'Some description');
        self.assertEqual('Some description', option.getDescription(), '->getDescription() returns the description message');


    def testGetDefault(self):

        option = InputOption('foo', None, InputOption.VALUE_OPTIONAL, '', 'default');
        self.assertEqual('default', option.getDefault(), '->getDefault() returns the default value');

        option = InputOption('foo', None, InputOption.VALUE_REQUIRED, '', 'default');
        self.assertEqual('default', option.getDefault(), '->getDefault() returns the default value');

        option = InputOption('foo', None, InputOption.VALUE_REQUIRED);
        self.assertTrue(option.getDefault() is None, '->getDefault() returns None if no default value is configured');

        option = InputOption('foo', None, InputOption.VALUE_OPTIONAL | InputOption.VALUE_IS_ARRAY);
        self.assertEqual(list(), option.getDefault(), '->getDefault() returns an empty array if option is an array');

        option = InputOption('foo', None, InputOption.VALUE_NONE);
        self.assertFalse(option.getDefault(), '->getDefault() returns False if the option does not take a value');


    def testSetDefault(self):

        option = InputOption('foo', None, InputOption.VALUE_REQUIRED, '', 'default');
        option.setDefault(None);
        self.assertTrue(option.getDefault() is None, '->setDefault() can reset the default value by passing None');
        option.setDefault('another');
        self.assertEqual('another', option.getDefault(), '->setDefault() changes the default value');

        option = InputOption('foo', None, InputOption.VALUE_REQUIRED | InputOption.VALUE_IS_ARRAY);
        option.setDefault([1, 2]);
        self.assertEqual([1, 2], option.getDefault(), '->setDefault() changes the default value');

        option = InputOption('foo', 'f', InputOption.VALUE_NONE);
        try:
            option.setDefault('default');
            self.fail('->setDefault() raise a LogicException if you give a default value for a VALUE_NONE option');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->setDefault() raise a LogicException if you give a default value for a VALUE_NONE option');
            self.assertEqual('Cannot set a default value when using InputOption.VALUE_NONE mode.', e.getMessage());


        option = InputOption('foo', 'f', InputOption.VALUE_OPTIONAL | InputOption.VALUE_IS_ARRAY);
        try:
            option.setDefault('default');
            self.fail('->setDefault() raise a LogicException if you give a default value which is not an array for a VALUE_IS_ARRAY option');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->setDefault() raise a LogicException if you give a default value which is not an array for a VALUE_IS_ARRAY option');
            self.assertEqual('A default value for an array option must be a list or dict.', e.getMessage());



    def testEquals(self):

        option = InputOption('foo', 'f', None, 'Some description');
        option2 = InputOption('foo', 'f', None, 'Alternative description');
        self.assertTrue(option.equals(option2));

        option = InputOption('foo', 'f', InputOption.VALUE_OPTIONAL, 'Some description');
        option2 = InputOption('foo', 'f', InputOption.VALUE_OPTIONAL, 'Some description', True);
        self.assertFalse(option.equals(option2));

        option = InputOption('foo', 'f', None, 'Some description');
        option2 = InputOption('bar', 'f', None, 'Some description');
        self.assertFalse(option.equals(option2));

        option = InputOption('foo', 'f', None, 'Some description');
        option2 = InputOption('foo', '', None, 'Some description');
        self.assertFalse(option.equals(option2));

        option = InputOption('foo', 'f', None, 'Some description');
        option2 = InputOption('foo', 'f', InputOption.VALUE_OPTIONAL, 'Some description');
        self.assertFalse(option.equals(option2));

class InputArgumentTest(unittest.TestCase):

    def testConstructor(self):

        argument = InputArgument('foo');
        self.assertEqual('foo', argument.getName(), '__init__() takes a name as its first argument');

        # mode argument
        argument = InputArgument('foo');
        self.assertFalse(argument.isRequired(), '__init__() gives a "InputArgument.OPTIONAL" mode by default');

        argument = InputArgument('foo', None);
        self.assertFalse(argument.isRequired(), '__init__() can take "InputArgument.OPTIONAL" as its mode');

        argument = InputArgument('foo', InputArgument.OPTIONAL);
        self.assertFalse(argument.isRequired(), '__init__() can take "InputArgument.OPTIONAL" as its mode');

        argument = InputArgument('foo', InputArgument.REQUIRED);
        self.assertTrue(argument.isRequired(), '__init__() can take "InputArgument.REQUIRED" as its mode');

        try:
            argument = InputArgument('foo', 'ANOTHER_ONE');
            self.fail('__init__() raise an InvalidArgumentException if the mode is not valid');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '__init__() raise an InvalidArgumentException if the mode is not valid');
            self.assertEqual('Argument mode "ANOTHER_ONE" is not valid.', e.getMessage());

        try:
            argument = InputArgument('foo', -1);
            self.fail('__init__() raise an InvalidArgumentException if the mode is not valid');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '__init__() raise an InvalidArgumentException if the mode is not valid');
            self.assertEqual('Argument mode "-1" is not valid.', e.getMessage());



    def testIsArray(self):

        argument = InputArgument('foo', InputArgument.IS_ARRAY);
        self.assertTrue(argument.isArray(), '->isArray() returns True if the argument can be an array');
        argument = InputArgument('foo', InputArgument.OPTIONAL | InputArgument.IS_ARRAY);
        self.assertTrue(argument.isArray(), '->isArray() returns True if the argument can be an array');
        argument = InputArgument('foo', InputArgument.OPTIONAL);
        self.assertFalse(argument.isArray(), '->isArray() returns False if the argument can not be an array');


    def testGetDescription(self):

        argument = InputArgument('foo', None, 'Some description');
        self.assertEqual('Some description', argument.getDescription(), '->getDescription() return the message description');


    def testGetDefault(self):

        argument = InputArgument('foo', InputArgument.OPTIONAL, '', 'default');
        self.assertEqual('default', argument.getDefault(), '->getDefault() return the default value');


    def testSetDefault(self):

        argument = InputArgument('foo', InputArgument.OPTIONAL, '', 'default');
        argument.setDefault(None);
        self.assertTrue(argument.getDefault() is None, '->setDefault() can reset the default value by passing None');
        argument.setDefault('another');
        self.assertEqual('another', argument.getDefault(), '->setDefault() changes the default value');

        argument = InputArgument('foo', InputArgument.OPTIONAL | InputArgument.IS_ARRAY);
        argument.setDefault([1, 2]);
        self.assertEqual([1, 2], argument.getDefault(), '->setDefault() changes the default value');

        try:
            argument = InputArgument('foo', InputArgument.REQUIRED);
            argument.setDefault('default');
            self.fail('->setDefault() raise a LogicException if you give a default value for a required argument');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->setDefault() raise a LogicException exception if an invalid option is passed');
            self.assertEqual('Cannot set a default value except for InputArgument.OPTIONAL mode.', e.getMessage());


        try:
            argument = InputArgument('foo', InputArgument.IS_ARRAY);
            argument.setDefault('default');
            self.fail('->setDefault() raise a LogicException if you give a default value which is not an array for a IS_ARRAY option');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->setDefault() raise a LogicException if you give a default value which is not an array for a IS_ARRAY option');
            self.assertEqual('A default value for an array argument must be a list.', e.getMessage());


class InputDefinitionTest(unittest.TestCase):

    def setUp(self):
        self.foo = None;
        self.bar = None;
        self.foo1 = None;
        self.foo2 = None;
        self.fixtures = os.path.dirname(__file__)+'/Fixtures/';


    def testConstructor(self):

        self.initializeArguments();

        definition = InputDefinition();
        self.assertEqual(list(), definition.getArguments(), '__init__() creates a new InputDefinition object');

        definition = InputDefinition([self.foo, self.bar]);
        self.assertEqual([self.foo, self.bar], definition.getArguments(), '__init__() takes an array of InputArgument objects as its first argument');

        self.initializeOptions();

        definition = InputDefinition();
        self.assertEqual(list(), definition.getOptions(), '__init__() creates a new InputDefinition object');

        definition = InputDefinition([self.foo, self.bar]);
        self.assertTrue([self.foo, self.bar] == definition.getOptions() or [self.bar, self.foo] == definition.getOptions(), '__init__() takes an array of InputOption objects as its first argument');


    def testSetArguments(self):

        self.initializeArguments();

        definition = InputDefinition();
        definition.setArguments([self.foo]);
        self.assertEqual([self.foo], definition.getArguments(), '->setArguments() sets the array of InputArgument objects');
        definition.setArguments([self.bar]);

        self.assertEqual([self.bar], definition.getArguments(), '->setArguments() clears all InputArgument objects');


    def testAddArguments(self):

        self.initializeArguments();

        definition = InputDefinition();
        definition.addArguments([self.foo]);
        self.assertEqual([self.foo], definition.getArguments(), '->addArguments() adds an array of InputArgument objects');
        definition.addArguments([self.bar]);
        self.assertEqual([self.foo, self.bar], definition.getArguments(), '->addArguments() does not clear existing InputArgument objects');


    def testAddArgument(self):

        self.initializeArguments();

        definition = InputDefinition();
        definition.addArgument(self.foo);
        self.assertEqual([self.foo], definition.getArguments(), '->addArgument() adds a InputArgument object');
        definition.addArgument(self.bar);
        self.assertEqual([self.foo, self.bar], definition.getArguments(), '->addArgument() adds a InputArgument object');

        # arguments must have different names:
        try:
            definition.addArgument(self.foo1);
            self.fail('->addArgument() raise a LogicException if another argument is already registered with the same name');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->addArgument() raise a LogicException if another argument is already registered with the same name');
            self.assertEqual('An argument with name "foo" already exists.', e.getMessage());


        # cannot add a parameter after an array parameter
        definition.addArgument(InputArgument('fooarray', InputArgument.IS_ARRAY));
        try:
            definition.addArgument(InputArgument('anotherbar'));
            self.fail('->addArgument() raise a LogicException if there is an array parameter already registered');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->addArgument() raise a LogicException if there is an array parameter already registered');
            self.assertEqual('Cannot add an argument after an array argument.', e.getMessage());


        # cannot add a required argument after an optional one
        definition = InputDefinition();
        definition.addArgument(self.foo);
        try:
            definition.addArgument(self.foo2);
            self.fail('->addArgument() raise a LogicException if you try to add a required argument after an optional one');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->addArgument() raise a LogicException if you try to add a required argument after an optional one');
            self.assertEqual('Cannot add a required argument after an optional one.', e.getMessage());



    def testGetArgument(self):

        self.initializeArguments();

        definition = InputDefinition();
        definition.addArguments([self.foo]);
        self.assertEqual(self.foo, definition.getArgument('foo'), '->getArgument() returns a InputArgument by its name');
        try:
            definition.getArgument('bar');
            self.fail('->getArgument() raise an InvalidArgumentException if the InputArgument name does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->getArgument() raise an InvalidArgumentException if the InputArgument name does not exist');
            self.assertEqual('The "bar" argument does not exist.', e.getMessage());



    def testHasArgument(self):

        self.initializeArguments();

        definition = InputDefinition();
        definition.addArguments([self.foo]);
        self.assertTrue(definition.hasArgument('foo'), '->hasArgument() returns True if a InputArgument exists for the given name');
        self.assertFalse(definition.hasArgument('bar'), '->hasArgument() returns False if a InputArgument exists for the given name');


    def testGetArgumentRequiredCount(self):

        self.initializeArguments();

        definition = InputDefinition();
        definition.addArgument(self.foo2);
        self.assertEqual(1, definition.getArgumentRequiredCount(), '->getArgumentRequiredCount() returns the number of required arguments');
        definition.addArgument(self.foo);
        self.assertEqual(1, definition.getArgumentRequiredCount(), '->getArgumentRequiredCount() returns the number of required arguments');


    def testGetArgumentCount(self):

        self.initializeArguments();

        definition = InputDefinition();
        definition.addArgument(self.foo2);
        self.assertEqual(1, definition.getArgumentCount(), '->getArgumentCount() returns the number of arguments');
        definition.addArgument(self.foo);
        self.assertEqual(2, definition.getArgumentCount(), '->getArgumentCount() returns the number of arguments');


    def testGetArgumentDefaults(self):

        definition = InputDefinition([
            InputArgument('foo1', InputArgument.OPTIONAL),
            InputArgument('foo2', InputArgument.OPTIONAL, '', 'default'),
            InputArgument('foo3', InputArgument.OPTIONAL | InputArgument.IS_ARRAY),
        #   InputArgument('foo4', InputArgument.OPTIONAL | InputArgument.IS_ARRAY, '', [1, 2]),
        ]);
        self.assertEqual({'foo1': None, 'foo2': 'default', 'foo3': []}, definition.getArgumentDefaults(), '->getArgumentDefaults() return the default values for each argument');

        definition = InputDefinition([
            InputArgument('foo4', InputArgument.OPTIONAL | InputArgument.IS_ARRAY, '', [1, 2]),
        ]);
        self.assertEqual({'foo4': [1, 2]}, definition.getArgumentDefaults(), '->getArgumentDefaults() return the default values for each argument');


    def testSetOptions(self):

        self.initializeOptions();

        definition = InputDefinition([self.foo]);
        self.assertEqual([self.foo], definition.getOptions(), '->setOptions() sets the array of InputOption objects');
        definition.setOptions([self.bar]);
        self.assertEqual([self.bar], definition.getOptions(), '->setOptions() clears all InputOption objects');
        try:
            definition.getOptionForShortcut('f');
            self.fail('->setOptions() clears all InputOption objects');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->setOptions() clears all InputOption objects');
            self.assertEqual('The "-f" option does not exist.', e.getMessage());



    def testAddOptions(self):

        self.initializeOptions();

        definition = InputDefinition([self.foo]);
        self.assertEqual([self.foo], definition.getOptions(), '->addOptions() adds an array of InputOption objects');
        definition.addOptions([self.bar]);
        self.assertTrue([self.foo, self.bar] == definition.getOptions() or [self.bar, self.foo] == definition.getOptions(), '->addOptions() does not clear existing InputOption objects');


    def testAddOption(self):

        self.initializeOptions();

        definition = InputDefinition();
        definition.addOption(self.foo);
        self.assertEqual([self.foo], definition.getOptions(), '->addOption() adds a InputOption object');
        definition.addOption(self.bar);
        self.assertTrue([self.foo, self.bar] == definition.getOptions() or [self.bar, self.foo] == definition.getOptions(), '->addOption() adds a InputOption object');
        try:
            definition.addOption(self.foo2);
            self.fail('->addOption() raise a LogicException if the another option is already registered with the same name');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->addOption() raise a LogicException if the another option is already registered with the same name');
            self.assertEqual('An option named "foo" already exists.', e.getMessage());

        try:
            definition.addOption(self.foo1);
            self.fail('->addOption() raise a LogicException if the another option is already registered with the same shortcut');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->addOption() raise a LogicException if the another option is already registered with the same shortcut');
            self.assertEqual('An option with shortcut "f" already exists.', e.getMessage());



    def testGetOption(self):

        self.initializeOptions();

        definition = InputDefinition([self.foo]);
        self.assertEqual(self.foo, definition.getOption('foo'), '->getOption() returns a InputOption by its name');
        try:
            definition.getOption('bar');
            self.fail('->getOption() raise an InvalidArgumentException if the option name does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->getOption() raise an InvalidArgumentException if the option name does not exist');
            self.assertEqual('The "--bar" option does not exist.', e.getMessage());



    def testHasOption(self):

        self.initializeOptions();

        definition = InputDefinition([self.foo]);
        self.assertTrue(definition.hasOption('foo'), '->hasOption() returns True if a InputOption exists for the given name');
        self.assertFalse(definition.hasOption('bar'), '->hasOption() returns False if a InputOption exists for the given name');


    def testHasShortcut(self):

        self.initializeOptions();

        definition = InputDefinition([self.foo]);
        self.assertTrue(definition.hasShortcut('f'), '->hasShortcut() returns True if a InputOption exists for the given shortcut');
        self.assertFalse(definition.hasShortcut('b'), '->hasShortcut() returns False if a InputOption exists for the given shortcut');


    def testGetOptionForShortcut(self):

        self.initializeOptions();

        definition = InputDefinition([self.foo]);
        self.assertEqual(self.foo, definition.getOptionForShortcut('f'), '->getOptionForShortcut() returns a InputOption by its shortcut');
        try:
            definition.getOptionForShortcut('l');
            self.fail('->getOption() raise an InvalidArgumentException if the shortcut does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->getOption() raise an InvalidArgumentException if the shortcut does not exist');
            self.assertEqual('The "-l" option does not exist.', e.getMessage());



    def testGetOptionDefaults(self):

        definition = InputDefinition([
            InputOption('foo1', None, InputOption.VALUE_NONE),
            InputOption('foo2', None, InputOption.VALUE_REQUIRED),
            InputOption('foo3', None, InputOption.VALUE_REQUIRED, '', 'default'),
            InputOption('foo4', None, InputOption.VALUE_OPTIONAL),
            InputOption('foo5', None, InputOption.VALUE_OPTIONAL, '', 'default'),
            InputOption('foo6', None, InputOption.VALUE_OPTIONAL | InputOption.VALUE_IS_ARRAY),
            InputOption('foo7', None, InputOption.VALUE_OPTIONAL | InputOption.VALUE_IS_ARRAY, '', [1, 2]),
        ]);
        defaults = {
            'foo1': False, # FIX: None => False
            'foo2': None,
            'foo3': 'default',
            'foo4': None,
            'foo5': 'default',
            'foo6': [],
            'foo7': [1, 2],
        };
        self.assertEqual(defaults, definition.getOptionDefaults(), '->getOptionDefaults() returns the default values for all options');


    def testGetSynopsis(self):

        definition = InputDefinition([InputOption('foo')]);
        self.assertEqual('[--foo]', definition.getSynopsis(), '->getSynopsis() returns a synopsis of arguments and options');
        definition = InputDefinition([InputOption('foo', 'f')]);
        self.assertEqual('[-f|--foo]', definition.getSynopsis(), '->getSynopsis() returns a synopsis of arguments and options');
        definition = InputDefinition([InputOption('foo', 'f', InputOption.VALUE_REQUIRED)]);
        self.assertEqual('[-f|--foo="..."]', definition.getSynopsis(), '->getSynopsis() returns a synopsis of arguments and options');
        definition = InputDefinition([InputOption('foo', 'f', InputOption.VALUE_OPTIONAL)]);
        self.assertEqual('[-f|--foo[="..."]]', definition.getSynopsis(), '->getSynopsis() returns a synopsis of arguments and options');

        definition = InputDefinition([InputArgument('foo')]);
        self.assertEqual('[foo]', definition.getSynopsis(), '->getSynopsis() returns a synopsis of arguments and options');
        definition = InputDefinition([InputArgument('foo', InputArgument.REQUIRED)]);
        self.assertEqual('foo', definition.getSynopsis(), '->getSynopsis() returns a synopsis of arguments and options');
        definition = InputDefinition([InputArgument('foo', InputArgument.IS_ARRAY)]);
        self.assertEqual('[foo1] ... [fooN]', definition.getSynopsis(), '->getSynopsis() returns a synopsis of arguments and options');
        definition = InputDefinition([InputArgument('foo', InputArgument.REQUIRED | InputArgument.IS_ARRAY)]);
        self.assertEqual('foo1 ... [fooN]', definition.getSynopsis(), '->getSynopsis() returns a synopsis of arguments and options');


    def testAsText(self):

        definition = InputDefinition([
            InputArgument('foo', InputArgument.OPTIONAL, 'The foo argument'),
            InputArgument('baz', InputArgument.OPTIONAL, 'The baz argument', True),
            InputArgument('bar', InputArgument.OPTIONAL | InputArgument.IS_ARRAY, 'The bar argument', ['http://foo.com/']),
            InputOption('foo', 'f', InputOption.VALUE_REQUIRED, 'The foo option'),
            InputOption('baz', None, InputOption.VALUE_OPTIONAL, 'The baz option', False),
            InputOption('bar', 'b', InputOption.VALUE_OPTIONAL, 'The bar option', 'bar'),
            InputOption('qux', '', InputOption.VALUE_OPTIONAL | InputOption.VALUE_IS_ARRAY, 'The qux option', ['http://foo.com/', 'bar']),
            InputOption('qux2', '', InputOption.VALUE_OPTIONAL | InputOption.VALUE_IS_ARRAY, 'The qux2 option', {'foo': 'bar'}),
        ]);
        f = open(self.fixtures+'/definition_astext.txt');
        astext = f.readlines().sort();
        f.close();
        actual = definition.asText().split("\n").sort();
        self.assertEqual(astext, actual, '->asText() returns a textual representation of the InputDefinition');


    def testAsXml(self):

        definition = InputDefinition([
            InputArgument('foo', InputArgument.OPTIONAL, 'The foo argument'),
            InputArgument('baz', InputArgument.OPTIONAL, 'The baz argument', True),
            InputArgument('bar', InputArgument.OPTIONAL | InputArgument.IS_ARRAY, 'The bar argument', ['bar']),
            InputOption('foo', 'f', InputOption.VALUE_REQUIRED, 'The foo option'),
            InputOption('baz', None, InputOption.VALUE_OPTIONAL, 'The baz option', False),
            InputOption('bar', 'b', InputOption.VALUE_OPTIONAL, 'The bar option', 'bar'),
        ]);
        f = open(self.fixtures+'/definition_asxml.txt');
        expected = f.readlines().sort();
        f.close();
        actual = definition.asXml().split(InputDefinition.XML_NL).sort();

#        expected = Document();
#        expected.load(self.fixtures+'/definition_asxml.txt');
#        actual = Document();
#        actual.loadXML(definition.asXml());
        self.assertEqual(actual, expected, '->asText() returns a textual representation of the InputDefinition');


    def initializeArguments(self):

        self.foo = InputArgument('foo');
        self.bar = InputArgument('bar');
        self.foo1 = InputArgument('foo');
        self.foo2 = InputArgument('foo2', InputArgument.REQUIRED);


    def initializeOptions(self):

        self.foo = InputOption('foo', 'f');
        self.bar = InputOption('bar', 'b');
        self.foo1 = InputOption('fooBis', 'f');
        self.foo2 = InputOption('foo', 'p');


class ArgvInputTest(unittest.TestCase):

    def testConstructor(self):
        argv = sys.argv[:];

        sys.argv = ['console.php', 'foo'];
        inputv = ArgvInput();

        self.assertEqual(['foo'], inputv._ArgvInput__tokens, '__init__() automatically get its input from the argv server variable');

        sys.argv = argv[:];

    def testParser(self):

        inputv = ArgvInput(['console.php', 'foo']);
        inputv.bind(InputDefinition([InputArgument('name')]));
        self.assertEqual({'name': 'foo'}, inputv.getArguments(), '->parse() parses required arguments');

        inputv.bind(InputDefinition([InputArgument('name')]));
        self.assertEqual({'name': 'foo'}, inputv.getArguments(), '->parse() is stateless');

        inputv = ArgvInput(['console.php', '--foo']);
        inputv.bind(InputDefinition([InputOption('foo')]));
        self.assertEqual({'foo': True}, inputv.getOptions(), '->parse() parses long options without a value');

        inputv = ArgvInput(['console.php', '--foo=bar']);
        inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_REQUIRED)]));
        self.assertEqual({'foo': 'bar'}, inputv.getOptions(), '->parse() parses long options with a required value (with a = separator)');

        inputv = ArgvInput(['console.php', '--foo', 'bar']);
        inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_REQUIRED)]));
        self.assertEqual({'foo': 'bar'}, inputv.getOptions(), '->parse() parses long options with a required value (with a space separator)');

        try:
            inputv = ArgvInput(['console.php', '--foo']);
            inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_REQUIRED)]));
            self.fail('->parse() raise a RuntimeException if no value is passed to an option when it is required');
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException), '->parse() raise a RuntimeException if no value is passed to an option when it is required');
            self.assertEqual('The "--foo" option requires a value.', e.getMessage(), '->parse() raise a RuntimeException if no value is passed to an option when it is required');


        inputv = ArgvInput(['console.php', '-f']);
        inputv.bind(InputDefinition([InputOption('foo', 'f')]));
        self.assertEqual({'foo': True}, inputv.getOptions(), '->parse() parses short options without a value');

        inputv = ArgvInput(['console.php', '-fbar']);
        inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_REQUIRED)]));
        self.assertEqual({'foo': 'bar'}, inputv.getOptions(), '->parse() parses short options with a required value (with no separator)');

        inputv = ArgvInput(['console.php', '-f', 'bar']);
        inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_REQUIRED)]));
        self.assertEqual({'foo': 'bar'}, inputv.getOptions(), '->parse() parses short options with a required value (with a space separator)');

        inputv = ArgvInput(['console.php', '-f', '']);
        inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_OPTIONAL)]));
        self.assertEqual({'foo': ''}, inputv.getOptions(), '->parse() parses short options with an optional empty value');

        inputv = ArgvInput(['console.php', '-f', '', 'foo']);
        inputv.bind(InputDefinition([InputArgument('name'), InputOption('foo', 'f', InputOption.VALUE_OPTIONAL)]));
        self.assertEqual({'foo': ''}, inputv.getOptions(), '->parse() parses short options with an optional empty value followed by an argument');

        inputv = ArgvInput(['console.php', '-f', '', '-b']);
        inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_OPTIONAL), InputOption('bar', 'b')]));
        self.assertEqual({'foo': '', 'bar': True}, inputv.getOptions(), '->parse() parses short options with an optional empty value followed by an option');

        inputv = ArgvInput(['console.php', '-f', '-b', 'foo']);
        inputv.bind(InputDefinition([InputArgument('name'), InputOption('foo', 'f', InputOption.VALUE_OPTIONAL), InputOption('bar', 'b')]));
        self.assertEqual({'foo': None, 'bar': True}, inputv.getOptions(), '->parse() parses short options with an optional value which is not present');

        try:
            inputv = ArgvInput(['console.php', '-f']);
            inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_REQUIRED)]));
            self.fail('->parse() raise a RuntimeException if no value is passed to an option when it is required');
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException), '->parse() raise a RuntimeException if no value is passed to an option when it is required');
            self.assertEqual('The "--foo" option requires a value.', e.getMessage(), '->parse() raise a RuntimeException if no value is passed to an option when it is required');


        try:
            inputv = ArgvInput(['console.php', '-ffoo']);
            inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_NONE)]));
            self.fail('->parse() raise a RuntimeException if a value is passed to an option which does not take one');
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException), '->parse() raise a RuntimeException if a value is passed to an option which does not take one');
            self.assertEqual('The "-o" option does not exist.', e.getMessage(), '->parse() raise a RuntimeException if a value is passed to an option which does not take one');


        try:
            inputv = ArgvInput(['console.php', 'foo', 'bar']);
            inputv.bind(InputDefinition());
            self.fail('->parse() raise a RuntimeException if too many arguments are passed');
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException), '->parse() raise a RuntimeException if too many arguments are passed');
            self.assertEqual('Too many arguments.', e.getMessage(), '->parse() raise a RuntimeException if too many arguments are passed');


        try:
            inputv = ArgvInput(['console.php', '--foo']);
            inputv.bind(InputDefinition());
            self.fail('->parse() raise a RuntimeException if an unknown long option is passed');
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException), '->parse() raise a RuntimeException if an unknown long option is passed');
            self.assertEqual('The "--foo" option does not exist.', e.getMessage(), '->parse() raise a RuntimeException if an unknown long option is passed');


        try:
            inputv = ArgvInput(['console.php', '-f']);
            inputv.bind(InputDefinition());
            self.fail('->parse() raise a RuntimeException if an unknown short option is passed');
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException), '->parse() raise a RuntimeException if an unknown short option is passed');
            self.assertEqual('The "-f" option does not exist.', e.getMessage(), '->parse() raise a RuntimeException if an unknown short option is passed');


        inputv = ArgvInput(['console.php', '-fb']);
        inputv.bind(InputDefinition([InputOption('foo', 'f'), InputOption('bar', 'b')]));
        self.assertEqual({'foo': True, 'bar': True}, inputv.getOptions(), '->parse() parses short options when they are aggregated as a single one');

        inputv = ArgvInput(['console.php', '-fb', 'bar']);
        inputv.bind(InputDefinition([InputOption('foo', 'f'), InputOption('bar', 'b', InputOption.VALUE_REQUIRED)]));
        self.assertEqual({'foo': True, 'bar': 'bar'}, inputv.getOptions(), '->parse() parses short options when they are aggregated as a single one and the last one has a required value');

        inputv = ArgvInput(['console.php', '-fb', 'bar']);
        inputv.bind(InputDefinition([InputOption('foo', 'f'), InputOption('bar', 'b', InputOption.VALUE_OPTIONAL)]));
        self.assertEqual({'foo': True, 'bar': 'bar'}, inputv.getOptions(), '->parse() parses short options when they are aggregated as a single one and the last one has an optional value');

        inputv = ArgvInput(['console.php', '-fbbar']);
        inputv.bind(InputDefinition([InputOption('foo', 'f'), InputOption('bar', 'b', InputOption.VALUE_OPTIONAL)]));
        self.assertEqual({'foo': True, 'bar': 'bar'}, inputv.getOptions(), '->parse() parses short options when they are aggregated as a single one and the last one has an optional value with no separator');

        inputv = ArgvInput(['console.php', '-fbbar']);
        inputv.bind(InputDefinition([InputOption('foo', 'f', InputOption.VALUE_OPTIONAL), InputOption('bar', 'b', InputOption.VALUE_OPTIONAL)]));
        self.assertEqual({'foo': 'bbar', 'bar': None}, inputv.getOptions(), '->parse() parses short options when they are aggregated as a single one and one of them takes a value');

        try:
            inputv = ArgvInput(['console.php', 'foo', 'bar', 'baz', 'bat']);
            inputv.bind(InputDefinition([InputArgument('name', InputArgument.IS_ARRAY)]));
            self.assertEqual({'name': ['foo', 'bar', 'baz', 'bat']}, inputv.getArguments(), '->parse() parses array arguments');
        except RuntimeException as e:
            self.assertNotEqual('Too many arguments.', e.getMessage(), '->parse() parses array arguments');


        inputv = ArgvInput(['console.php', '--name=foo', '--name=bar', '--name=baz']);
        inputv.bind(InputDefinition([InputOption('name', None, InputOption.VALUE_OPTIONAL | InputOption.VALUE_IS_ARRAY)]));
        self.assertEqual({'name': ['foo', 'bar', 'baz']}, inputv.getOptions());

        try:
            inputv = ArgvInput(['console.php', '-1']);
            inputv.bind(InputDefinition([InputArgument('number')]));
            self.fail('->parse() raise a RuntimeException if an unknown option is passed');
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException), '->parse() parses arguments with leading dashes as options without having encountered a double-dash sequence');
            self.assertEqual('The "-1" option does not exist.', e.getMessage(), '->parse() parses arguments with leading dashes as options without having encountered a double-dash sequence');


        inputv = ArgvInput(['console.php', '--', '-1']);
        inputv.bind(InputDefinition([InputArgument('number')]));
        self.assertEqual({'number': '-1'}, inputv.getArguments(), '->parse() parses arguments with leading dashes as arguments after having encountered a double-dash sequence');

        inputv = ArgvInput(['console.php', '-f', 'bar', '--', '-1']);
        inputv.bind(InputDefinition([InputArgument('number'), InputOption('foo', 'f', InputOption.VALUE_OPTIONAL)]));
        self.assertEqual({'foo': 'bar'}, inputv.getOptions(), '->parse() parses arguments with leading dashes as options before having encountered a double-dash sequence');
        self.assertEqual({'number': '-1'}, inputv.getArguments(), '->parse() parses arguments with leading dashes as arguments after having encountered a double-dash sequence');

        inputv = ArgvInput(['console.php', '-f', 'bar', '']);
        inputv.bind(InputDefinition([InputArgument('empty'), InputOption('foo', 'f', InputOption.VALUE_OPTIONAL)]));
        self.assertEqual({'empty': ''}, inputv.getArguments(), '->parse() parses empty string arguments');


    def testGetFirstArgument(self):

        inputv = ArgvInput(['console.php', '-fbbar']);
        self.assertEqual(None, inputv.getFirstArgument(), '->getFirstArgument() returns the first argument from the raw input');

        inputv = ArgvInput(['console.php', '-fbbar', 'foo']);
        self.assertEqual('foo', inputv.getFirstArgument(), '->getFirstArgument() returns the first argument from the raw input');


    def testHasParameterOption(self):

        inputv = ArgvInput(['console.php', '-f', 'foo']);
        self.assertTrue(inputv.hasParameterOption('-f'), '->hasParameterOption() returns True if the given short option is in the raw input');

        inputv = ArgvInput(['console.php', '--foo', 'foo']);
        self.assertTrue(inputv.hasParameterOption('--foo'), '->hasParameterOption() returns True if the given short option is in the raw input');

        inputv = ArgvInput(['console.php', 'foo']);
        self.assertFalse(inputv.hasParameterOption('--foo'), '->hasParameterOption() returns False if the given short option is not in the raw input');


    def testGetParameterOptionEqualSign(self):
        """@dataProvider provideGetParameterOptionValues

        """

        for argv, key, expected in self.provideGetParameterOptionValues():
            inputv = ArgvInput(argv);
            self.assertEqual(expected, inputv.getParameterOption(key), '->getParameterOption() returns the expected value');


    def provideGetParameterOptionValues(self):

        return [
            (['app/console', 'foo:bar', '-e', 'dev'], '-e', 'dev'),
            (['app/console', 'foo:bar', '--env=dev'], '--env', 'dev'),
            (['app/console', 'foo:bar', '-e', 'dev'], ['-e', '--env'], 'dev'),
            (['app/console', 'foo:bar', '--env=dev'], ['-e', '--env'], 'dev'),
        ];

    def testGetParameterOptionMissingOption(self):
        """@dataProvider provideGetParameterOptionOptionMissingValues

        """

        for argv, key, default, expected in self.provideGetParameterOptionMissingOptionValues():
            inputv = ArgvInput(argv);
            self.assertEqual(expected, inputv.getParameterOption(key, default), '->getParameterOption() returns the expected value');


    def provideGetParameterOptionMissingOptionValues(self):

        return [
            (['app/console', 'foo:bar'], ['-e', '--env'], 'dev', 'dev'),
            (['app/console'], ['-e', '--env'], 'dev', 'dev'),
        ];

class ArrayInputTest(unittest.TestCase):

    def testGetFirstArgument(self):

        inputv = ArrayInput([]);
        self.assertTrue(inputv.getFirstArgument() is None, '->getFirstArgument() returns None if no argument were passed');
        inputv = ArrayInput({'name': 'Fabien'});
        self.assertEqual('Fabien', inputv.getFirstArgument(), '->getFirstArgument() returns the first passed argument');
        inputv = ArrayInput({'--foo': 'bar', 'name': 'Fabien'});
        self.assertEqual('Fabien', inputv.getFirstArgument(), '->getFirstArgument() returns the first passed argument');


    def testHasParameterOption(self):

        inputv = ArrayInput({'name': 'Fabien', '--foo': 'bar'});
        self.assertTrue(inputv.hasParameterOption('--foo'), '->hasParameterOption() returns True if an option is present in the passed parameters');
        self.assertFalse(inputv.hasParameterOption('--bar'), '->hasParameterOption() returns False if an option is not present in the passed parameters');

        inputv = ArrayInput(['--foo']);
        self.assertTrue(inputv.hasParameterOption('--foo'), '->hasParameterOption() returns True if an option is present in the passed parameters');


    def testParse(self):

        inputv = ArrayInput({'name': 'foo'}, InputDefinition([InputArgument('name')]));
        self.assertEqual({'name': 'foo'}, inputv.getArguments(), '->parse() parses required arguments');

        try:
            inputv = ArrayInput({'foo': 'foo'}, InputDefinition([InputArgument('name')]));
            self.fail('->parse() raise an InvalidArgumentException exception if an invalid argument is passed');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->parse() raise an InvalidArgumentException exception if an invalid argument is passed');
            self.assertEqual('The "foo" argument does not exist.', e.getMessage(), '->parse() raise an InvalidArgumentException exception if an invalid argument is passed');


        inputv = ArrayInput({'--foo': 'bar'}, InputDefinition([InputOption('foo')]));
        self.assertEqual({'foo': 'bar'}, inputv.getOptions(), '->parse() parses long options');

        inputv = ArrayInput({'--foo': 'bar'}, InputDefinition([InputOption('foo', 'f', InputOption.VALUE_OPTIONAL, '', 'default')]));
        self.assertEqual({'foo': 'bar'}, inputv.getOptions(), '->parse() parses long options with a default value');

        inputv = ArrayInput({'--foo': None}, InputDefinition([InputOption('foo', 'f', InputOption.VALUE_OPTIONAL, '', 'default')]));
        self.assertEqual({'foo': 'default'}, inputv.getOptions(), '->parse() parses long options with a default value');

        try:
            inputv = ArrayInput({'--foo': None}, InputDefinition([InputOption('foo', 'f', InputOption.VALUE_REQUIRED)]));
            self.fail('->parse() raise an InvalidArgumentException exception if a required option is passed without a value');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->parse() raise an InvalidArgumentException exception if a required option is passed without a value');
            self.assertEqual('The "--foo" option requires a value.', e.getMessage(), '->parse() raise an InvalidArgumentException exception if a required option is passed without a value');


        try:
            inputv = ArrayInput({'--foo': 'foo'}, InputDefinition());
            self.fail('->parse() raise an InvalidArgumentException exception if an invalid option is passed');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->parse() raise an InvalidArgumentException exception if an invalid option is passed');
            self.assertEqual('The "--foo" option does not exist.', e.getMessage(), '->parse() raise an InvalidArgumentException exception if an invalid option is passed');


        inputv = ArrayInput({'-f': 'bar'}, InputDefinition([InputOption('foo', 'f')]));
        self.assertEqual({'foo': 'bar'}, inputv.getOptions(), '->parse() parses short options');

        try:
            inputv = ArrayInput({'-o': 'foo'}, InputDefinition());
            self.fail('->parse() raise an InvalidArgumentException exception if an invalid option is passed');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->parse() raise an InvalidArgumentException exception if an invalid option is passed');
            self.assertEqual('The "-o" option does not exist.', e.getMessage(), '->parse() raise an InvalidArgumentException exception if an invalid option is passed');


if __name__ == "__main__":
    unittest.main();
