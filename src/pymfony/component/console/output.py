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

import re;
import os;
import sys;

from pymfony.component.system import interface
from pymfony.component.system import Object
from pymfony.component.system import abstract
from pymfony.component.system import Tool
from pymfony.component.system.exception import RuntimeException
from pymfony.component.system.exception import InvalidArgumentException
from pymfony.component.console.formatter import OutputFormatterInterface
from pymfony.component.console.formatter import OutputFormatter

@interface
class OutputInterface(Object):
    """OutputInterface is the interface implemented by all Output classes.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """

    VERBOSITY_QUIET   = 0;
    VERBOSITY_NORMAL  = 1;
    VERBOSITY_VERBOSE = 2;

    OUTPUT_NORMAL = 0;
    OUTPUT_RAW = 1;
    OUTPUT_PLAIN = 2;

    def write(self, messages, newline = False, outputType = 0):
        """Writes a message to the output.
     *
     * @param string|array messages The message as an array of lines of a single string
     * @param Boolean      newline  Whether to add a newline or not
     * @param integer      type     The type of output (0: normal, 1: raw, 2: plain)
     *
     * @raise InvalidArgumentException When unknown output type is given
     *
     * @api

        """

    def writeln(self, messages, outputType = 0):
        """Writes a message to the output and adds a newline at the end.
     *
     * @param string|array messages The message as an array of lines of a single string
     * @param integer      type     The type of output (0: normal, 1: raw, 2: plain)
     *
     * @api

        """

    def setVerbosity(self, level):
        """Sets the verbosity of the output.
     *
     * @param integer level The level of verbosity
     *
     * @api

        """

    def getVerbosity(self):
        """Gets the current verbosity of the output.
     *
     * @return integer The current level of verbosity
     *
     * @api

        """

    def setDecorated(self, decorated):
        """Sets the decorated flag.
     *
     * @param Boolean decorated Whether to decorate the messages or not
     *
     * @api

        """

    def isDecorated(self):
        """Gets the decorated flag.
     *
     * @return Boolean True if the output will decorate messages, False otherwise:
     *
     * @api

        """

    def setFormatter(self, formatter):
        """Sets output formatter.
     *
     * @param OutputFormatterInterface formatter
     *
     * @api

        """
        assert isinstance(formatter, OutputFormatterInterface);

    def getFormatter(self):
        """Returns current output formatter instance.
     *
     * @return  OutputFormatterInterface
     *
     * @api

        """

@interface
class ConsoleOutputInterface(OutputInterface):
    """ConsoleOutputInterface is the interface implemented by ConsoleOutput class.
 * This adds information about stderr output stream.
 *
 * @author Dariusz G󲥣ki <darek.krk@gmail.com>

    """

    def getErrorOutput(self):
        """@return OutputInterface

        """

    def setErrorOutput(self, error):
        assert isinstance(error, OutputInterface);



@abstract
class Output(OutputInterface):
    """Base class for output classes.
 *
 * There are three levels of verbosity:
 *
 *  * normal: no option passed (normal output - information)
 *  * verbose: -v (more output - debug)
 *  * quiet: -q (no output)
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """


    def __init__(self, verbosity = OutputInterface.VERBOSITY_NORMAL, decorated = None, formatter = None):
        """Constructor.
     *
     * @param integer                  verbosity The verbosity level (self.VERBOSITY_QUIET, self.VERBOSITY_NORMAL, self.VERBOSITY_VERBOSE)
     * @param Boolean                  decorated Whether to decorate messages or not (None for auto-guessing)
     * @param OutputFormatterInterface formatter Output formatter instance
     *
     * @api

        """
        if formatter:
            assert isinstance(formatter, OutputFormatterInterface);

        self.__verbosity = None;
        self.__formatter = None;
    
        if None is verbosity:
            self.__verbosity = self.VERBOSITY_NORMAL;
        else:
            self.__verbosity = verbosity;
        if None is formatter:
            self.__formatter = OutputFormatter();
        else:
            self.__formatter = formatter;
        self.__formatter.setDecorated(bool(decorated));


    def setFormatter(self, formatter):
        """Sets output formatter.
     *
     * @param OutputFormatterInterface formatter
     *
     * @api

        """
        assert isinstance(formatter, OutputFormatterInterface);

        self.__formatter = formatter;


    def getFormatter(self):
        """Returns current output formatter instance.
     *
     * @return  OutputFormatterInterface
     *
     * @api

        """

        return self.__formatter;


    def setDecorated(self, decorated):
        """Sets the decorated flag.
     *
     * @param Boolean decorated Whether to decorate the messages or not
     *
     * @api

        """

        self.__formatter.setDecorated(bool(decorated));


    def isDecorated(self):
        """Gets the decorated flag.
     *
     * @return Boolean True if the output will decorate messages, False otherwise:
     *
     * @api

        """

        return self.__formatter.isDecorated();


    def setVerbosity(self, level):
        """Sets the verbosity of the output.
     *
     * @param integer level The level of verbosity
     *
     * @api

        """

        self.__verbosity = int(level);


    def getVerbosity(self):
        """Gets the current verbosity of the output.
     *
     * @return integer The current level of verbosity
     *
     * @api

        """

        return self.__verbosity;


    def writeln(self, messages, outputType = OutputInterface.OUTPUT_NORMAL):
        """Writes a message to the output and adds a newline at the end.
     *
     * @param string|list messages    The message as an array of lines of a
                                      single string
     * @param integer     outputType  The type of output
     *
     * @api

        """

        self.write(messages, True, outputType);


    def write(self, messages, newline = False, outputType = OutputInterface.OUTPUT_NORMAL):
        """Writes a message to the output.
     *
     * @param string|list messages The message as a list of lines of a single string
     * @param Boolean      newline  Whether to add a newline or not
     * @param integer      type     The type of output
     *
     * @raise InvalidArgumentException When unknown output type is given
     *
     * @api

        """

        if (self.VERBOSITY_QUIET == self.__verbosity) :
            return;

        if not isinstance(messages, list):
            messages = [str(messages)];

        for message in messages:
            if OutputInterface.OUTPUT_NORMAL == outputType:
                message = self.__formatter.format(message);
            elif OutputInterface.OUTPUT_RAW == outputType:
                pass;
            elif OutputInterface.OUTPUT_PLAIN == outputType:
                message = self.__formatter.format(message);
                message = re.sub(r'<[^>]*?>', '', message);
            else:
                raise InvalidArgumentException(
                    'Unknown output type given ({0})'.format(outputType)
                );


            self._doWrite(message, newline);



    @abstract
    def _doWrite(self, message, newline):
        """Writes a message to the output.
     *
     * @param string  message A message to write to the output
     * @param Boolean newline Whether to add a newline or not

        """

class NullOutput(Output):
    """NullOutput suppresses all output.
 *
 *     output = NullOutput();
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """

    def _doWrite(self, message, newline):
        """Writes a message to the output.
     *
     * @param string  message A message to write to the output
     * @param Boolean newline Whether to add a newline or not

        """


class StreamOutput(Output):
    """StreamOutput writes the output to a given stream.
 *
 * Usage:
 *
 * output = StreamOutput(fopen('php://stdout', 'w'));
 *
 * As `StreamOutput` can use any stream, you can also use a file:
 *
 * output = StreamOutput(fopen('/path/to/output.log', 'a', False));
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """


    def __init__(self, stream, verbosity = Output.VERBOSITY_NORMAL, decorated = None, formatter = None):
        """Constructor.
     *
     * @param mixed                    stream    A stream resource
     * @param integer                  verbosity The verbosity level (self.VERBOSITY_QUIET, self.VERBOSITY_NORMAL,
     *                                                                 self.VERBOSITY_VERBOSE)
     * @param Boolean                  decorated Whether to decorate messages or not (None for auto-guessing)
     * @param OutputFormatterInterface formatter Output formatter instance
     *
     * @raise InvalidArgumentException When first argument is not a real stream
     *
     * @api

        """
        if formatter:
            assert isinstance(formatter, OutputFormatterInterface);

        self.__stream = None;

        for method in ['flush', 'write', 'isatty']:
            if not Tool.isCallable(getattr(stream, method, None)):
                raise InvalidArgumentException(
                    'The StreamOutput class needs a stream as its first '
                    'argument.'
                );


        self.__stream = stream;

        if (None is decorated) :
            decorated = self._hasColorSupport();


        Output.__init__(self, verbosity, decorated, formatter);


    def getStream(self):
        """Gets the stream attached to this StreamOutput instance.
     *
     * @return resource A stream resource

        """

        return self.__stream;


    def _doWrite(self, message, newline):
        """Writes a message to the output.
     *
     * @param string  message A message to write to the output
     * @param Boolean newline Whether to add a newline or not
     *
     * @raise RuntimeException When unable to write output (should never happen)

        """

        if newline:
            text = message + os.linesep;
        else:
            text = message;

        try:
            self.__stream.write(text.encode());
        except IOError:
            # @codeCoverageIgnoreStart
            # should never happen
            raise RuntimeException('Unable to write output.');
            # @codeCoverageIgnoreEnd


        self.__stream.flush();


    def _hasColorSupport(self):
        """Returns True if the stream supports colorization.:
     *
     * Colorization is disabled if not supported by the stream::
     *
     *  -  windows without ansicon and ConEmu
     *  -  non tty consoles
     *
     * @return Boolean True if the stream supports colorization, False otherwise:

        """

        # @codeCoverageIgnoreStart
        if (os.path.sep == '\\') :
            return 'ANSICON' in os.environ or (
                'ConEmuANSI' in os.environ and os.environ['ConEmuANSI'] == 'ON'
            );

        return self.__stream.isatty();
        # @codeCoverageIgnoreEnd


class ConsoleOutput(StreamOutput, ConsoleOutputInterface):
    """ConsoleOutput is the default class for(, all CLI output. It uses STDOUT.):
 *
 * This class is(, a convenient wrapper around `StreamOutput`.):
 *
 *     output = ConsoleOutput();
 *
 * This is equivalent to:
 *
 *     output = StreamOutput(fopen('php://stdout', 'w'));
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """


    def __init__(self, verbosity = StreamOutput.VERBOSITY_NORMAL, decorated = None, formatter = None):
        """Constructor.
     *
     * @param integer                  verbosity The verbosity level (self.VERBOSITY_QUIET, self.VERBOSITY_NORMAL,
     *                                                                 self.VERBOSITY_VERBOSE)
     * @param Boolean                  decorated Whether to decorate messages or not (None for auto-guessing)
     * @param OutputFormatterInterface formatter Output formatter instance
     *
     * @api

        """
        if formatter:
            assert isinstance(formatter, OutputFormatterInterface);

        self.__stderr = None;


        StreamOutput.__init__(self, sys.stdout, verbosity, decorated, formatter);

        self.__stderr = StreamOutput(sys.stderr, verbosity, decorated, formatter);


    def setDecorated(self, decorated):

        StreamOutput.setDecorated(self, decorated);
        self.__stderr.setDecorated(decorated);


    def setFormatter(self, formatter):
        assert isinstance(formatter, OutputFormatterInterface);

        StreamOutput.setFormatter(self, formatter);
        self.__stderr.setFormatter(formatter);


    def setVerbosity(self, level):

        StreamOutput.setVerbosity(self, level);
        self.__stderr.setVerbosity(level);


    def getErrorOutput(self):
        """@return OutputInterface

        """

        return self.__stderr;


    def setErrorOutput(self, error):
        assert isinstance(error, OutputInterface);

        self.__stderr = error;


    def _hasStdoutSupport(self):
        """Returns True if current environment supports writing console output to:
     * STDOUT.
     *
     * IBM iSeries (OS400) exhibits character-encoding issues when writing to
     * STDOUT and doesn't properly convert ASCII to EBCDIC, resulting in garbage
     * output.
     *
     * @return boolean

        """

        return hasattr(sys, 'stdout');

