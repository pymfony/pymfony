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
import os;
import tempfile;

from pymfony.component.console.output import Output;
from pymfony.component.console.formatter import OutputFormatterStyle;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.console.output import OutputInterface;
from pymfony.component.console.output import NullOutput;
from pymfony.component.console.output import StreamOutput;
from pymfony.component.console.output import ConsoleOutput;

class OutputTest(unittest.TestCase):

    def testConstructor(self):

        output = TestOutput(Output.VERBOSITY_QUIET, True);
        self.assertEqual(Output.VERBOSITY_QUIET, output.getVerbosity(), '__init__() takes the verbosity as its first argument');
        self.assertTrue(output.isDecorated(), '__init__() takes the decorated flag as its second argument');


    def testSetIsDecorated(self):

        output = TestOutput();
        output.setDecorated(True);
        self.assertTrue(output.isDecorated(), 'setDecorated() sets the decorated flag');


    def testSetGetVerbosity(self):

        output = TestOutput();
        output.setVerbosity(Output.VERBOSITY_QUIET);
        self.assertEqual(Output.VERBOSITY_QUIET, output.getVerbosity(), '->setVerbosity() sets the verbosity');


    def testWrite(self):

        fooStyle = OutputFormatterStyle('yellow', 'red', ['blink']);
        output = TestOutput(Output.VERBOSITY_QUIET);
        output.writeln('foo');
        self.assertEqual('', output.output, '->writeln() outputs nothing if verbosity is set to VERBOSITY_QUIET');

        output = TestOutput();
        output.writeln(['foo', 'bar']);
        self.assertEqual("foo\nbar\n", output.output, '->writeln() can take an array of messages to output');

        output = TestOutput();
        output.writeln('<info>foo</info>', Output.OUTPUT_RAW);
        self.assertEqual("<info>foo</info>\n", output.output, '->writeln() outputs the raw message if OUTPUT_RAW is specified');

        output = TestOutput();
        output.writeln('<info>foo</info>', Output.OUTPUT_PLAIN);
        self.assertEqual("foo\n", output.output, '->writeln() strips decoration tags if OUTPUT_PLAIN is specified');

        output = TestOutput();
        output.setDecorated(False);
        output.writeln('<info>foo</info>');
        self.assertEqual("foo\n", output.output, '->writeln() strips decoration tags if decoration is set to False');

        output = TestOutput();
        output.getFormatter().setStyle('FOO', fooStyle);
        output.setDecorated(True);
        output.writeln('<foo>foo</foo>');
        self.assertEqual("\033[33;41;5mfoo\033[0m\n", output.output, '->writeln() decorates the output');

        try:
            output.writeln('<foo>foo</foo>', 24);
            self.fail('->writeln() raise an InvalidArgumentException when the type does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->writeln() raise an InvalidArgumentException when the type does not exist');
            self.assertEqual('Unknown output type given (24)', e.getMessage());


        output.clear();
        output.write('<bar>foo</bar>');
        self.assertEqual('<bar>foo</bar>', output.output, '->write() do nothing when a style does not exist');

        output.clear();
        output.writeln('<bar>foo</bar>');
        self.assertEqual("<bar>foo</bar>\n", output.output, '->writeln() do nothing when a style does not exist');



class TestOutput(Output):

    def __init__(self, verbosity=OutputInterface.VERBOSITY_NORMAL, decorated=None, formatter=None):
        Output.__init__(self, verbosity=verbosity, decorated=decorated, formatter=formatter)
        self.output = '';

    def clear(self):

        self.output = '';


    def _doWrite(self, message, newline):

        if newline:
            self.output += message+"\n";
        else:
            self.output += message;

class NullOutputTest(unittest.TestCase):

    def testConstructor(self):

        output = NullOutput();
        output.write('foo');
        self.assertTrue(True, '->write() does nothing'); # FIXME


class StreamOutputTest(unittest.TestCase):

    #  self._stream = None;

    def setUp(self):

        self.stream = tempfile.TemporaryFile();


    def tearDown(self):

        self.stream = None;


    def testConstructor(self):

        try:
            output = StreamOutput('foo');
            self.fail('__init__() raise an InvalidArgumentException if the first argument is not a stream');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '__init__() raise an InvalidArgumentException if the first argument is not a stream');
            self.assertEqual('The StreamOutput class needs a stream as its first argument.', e.getMessage());


        output = StreamOutput(self.stream, Output.VERBOSITY_QUIET, True);
        self.assertEqual(Output.VERBOSITY_QUIET, output.getVerbosity(), '__init__() takes the verbosity as its first argument');
        self.assertTrue(output.isDecorated(), '__init__() takes the decorated flag as its second argument');


    def testGetStream(self):

        output = StreamOutput(self.stream);
        self.assertEqual(self.stream, output.getStream(), '->getStream() returns the current stream');


    def testDoWrite(self):

        output = StreamOutput(self.stream);
        output.writeln('foo');
        output.getStream().seek(0);
        self.assertEqual('foo'+os.linesep, output.getStream().read().decode(), '->doWrite() writes to the stream');


class ConsoleOutputTest(unittest.TestCase):

    def testConstructor(self):

        output = ConsoleOutput(Output.VERBOSITY_QUIET, True);
        self.assertEqual(Output.VERBOSITY_QUIET, output.getVerbosity(), '__init__() takes the verbosity as its first argument');



if __name__ == '__main__':
    unittest.main();
