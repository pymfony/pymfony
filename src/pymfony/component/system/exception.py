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

import sys;
import linecache;

from pymfony.component.system import Object;
from pymfony.component.system.oop import final;

class StandardException(Exception, Object):
    STACK_PATTERN = 'File "{filename}", line {lineno}, in {name}';


    def __init__(self, message="", code=None, previous=None):
        """Construct the exception

        @param message:  string         The Exception message to raise.
        @param code:     int            The Exception code.
        @param previous: BaseException  The previous exception used for
                                        the exception chaining.
        """
        if previous: assert isinstance(previous, BaseException);
        else: previous = None;

        if code: assert isinstance(code, int);
        else: code = 0;

        self._message = None;
        self._code = None;
        self._previous = None;
        self._file = None;
        self._line = None;
        self._lineno = None;
        self._lines = None;
        self.__string = None;
        self.__traceAsString = None;
        self.__trace = None;

        self.__trace = self.__createTrace();
        self._message = str(message);
        self._code = int(code);
        self._previous = previous;


    def __createTrace(self):
        trace = [];
        try:
            raise Exception;
        except Exception:
            tb = sys.exc_info()[2];

        f = tb.tb_frame.f_back.f_back;

        while f is not None:
            localVars = {};
            for name, value in f.f_locals.items():
                localVars[name] = repr(value);

            filename = f.f_code.co_filename;
            lineno = f.f_lineno;
            name = f.f_code.co_name;
            argcount = f.f_code.co_argcount;
            allLines = linecache.getlines(filename, f.f_globals);
            line = allLines[lineno - 1].strip();

            upAndDown = 5;

            startLineno = lineno + 1;
            while startLineno > 1 and lineno - startLineno < upAndDown:
                startLineno -= 1;

            nbLines = len(allLines);
            endLineno = lineno;
            while endLineno < nbLines and endLineno - lineno < upAndDown:
                endLineno += 1;

            lines = dict();
            i = startLineno;
            while i <= endLineno:
                lines[i] = allLines[i-1];
                i += 1;

            stack = {
                'filename'  : filename,
                'lineno'    : lineno,
                'name'      : name,
                'line'      : line,
                'lines'     : lines, # {int: string, ...}
                'locals'    : localVars,
                'argcount'  : argcount,
            };
            trace.append(stack);
            f = f.f_back;

        return trace;


    def __formatTrace(self, trace):
        string = "";
        i = -1;
        for stack in reversed(trace):
            i += 1;
            string += "#" + str(i) + " " + self._formatStack(stack) + "\n";
        return string;

    def _formatStack(self, stack):
        argList = [];
        args = "";
        if not stack['name'].startswith('<'):
            for name, value in stack['locals'].items():
                argList.append(name + '=' + repr(value));
            if argList:
                args = "(" + ", ".join(argList) + ")";

        formater = self.STACK_PATTERN + ", with {0}"

        return formater.format(args, **stack);

    @final
    def getMessage(self):
        """Return the exception message

        @return: string The exception message
        """
        return self._message;

    @final
    def getPrevious(self):
        """Return the previous exception

        @return: BaseException The previous exception
        """
        return self._previous;

    @final
    def getCode(self):
        """Return the Exception code.

        @return: int The Exception code.
        """
        return self._code;

    @final
    def getFile(self):
        """Return the name of the file where the exception was raise.

        @return: string the name of the file where the exception was raise.
        """
        if self._file:
            return self._file;
        self._file = self.getTrace()[0]['filename'];
        return self._file;

    @final
    def getLineno(self):
        """Return the line number where the exception was raise.

        @return: int The line number where the exception was raise.
        """
        if self._lineno:
            return self._lineno;
        self._lineno = self.getTrace()[0]['lineno'];
        return self._lineno;

    @final
    def getLine(self):
        """Return the line content where the exception was raise.

        @return: string The line content where the exception was raise.
        """
        if self._line:
            return self._line;
        self._line = self.getTrace()[0]['line'];
        return self._line;

    @final
    def getLines(self):
        """Return lines content where the exception was raise.

        @return: dict lines content where the exception was raise.
                      {int: string, ...}
        """
        if self._lines:
            return self._lines;
        self._lines = self.getTrace()[0]['lines'];
        return self._lines;

    @final
    def getTrace(self):
        """Return the stack trace as list.

        @return: list of tuples like
                (filename, lineno, name, line, lines, locals, argcount)
        """
        return self.__trace;

    @final
    def getTraceAsString(self):
        """Return the stack trace as string.

        @return: string The stack trace as string.
        """
        if self.__traceAsString:
            return self.__traceAsString;
        self.__traceAsString = self.__formatTrace(self.getTrace());
        return self.__traceAsString;

    def __str__(self):
        """Return the string representation of exception.

        @return: string representation of exception.
        """
        if self.__string:
            return self.__string;

        self.__string = '';
        if self._previous:
            if not isinstance(self._previous, self.__class__):
                self.__string += "An exception '{0}' was previously raised with message '{1}'\n".format(
                    type(self._previous).__name__,
                    str(self._previous),
                );
            else:
                self.__string += str(self._previous);
            self.__string += '\nNext ';

        self.__string += \
        "exception '{0}' with message '{1}'\n".format(
            type(self).__name__,
            self._message,
            self._file,
            self._line,
        );
        self.__string += "Traceback (most recent call last):\n";
        self.__string += self.getTraceAsString();
        self.__string += \
        "{0}: {1}\n".format(
            type(self).__name__,
            self._message
        );
        return self.__string;

    @final
    def __copy__(self):
        """Prevent clone.
        """
        raise TypeError();

class LogicException(StandardException):
    pass;

class InvalidArgumentException(LogicException):
    pass;

class BadMethodCallException(LogicException):
    pass;

class OutOfBoundsException(LogicException, IndexError):
    """Exception thrown if a value is not a valid key.
    """

class RuntimeException(StandardException):
    pass;

class UnexpectedValueException(RuntimeException):
    """Exception raise if a value does not match with a set of values.

    Typically this happens when a function calls another function and expects
    the return value to be of a certain type or value not including arithmetic
    or buffer related errors.
    """
