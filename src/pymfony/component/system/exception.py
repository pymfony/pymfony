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

import traceback;
import sys

from pymfony.component.system import Object;
from pymfony.component.system import final;

class StandardException(Exception, Object):
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
        self._file = None;
        self._previous = None;
        self._line = None;
        self.__string = None;
        self.__trace = None;
        self._function = None;
        self._locals = None;

        self._message = str(message);
        self._code = int(code);
        self._previous = previous;
        self.__trace = self.__createTrace();
        currentStack = self.__trace.pop(0);
        self._line = currentStack['line'];
        self._file = currentStack['file'];
        self._function = currentStack['function'];
        self._locals = currentStack['locals'];
        self.__string = self.__formatTrace(self.__trace);


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
            stack = {
                'file'     : f.f_code.co_filename,
                'line'     : f.f_lineno,
                'function' : f.f_code.co_name,
                'locals'   : localVars,
            };
            trace.append(stack);
            f = f.f_back;

        return trace;


    def __formatTrace(self, trace):
        string = "";
        i = -1;
        for stack in trace:
            i += 1;
            string += self._formatStack(i, stack);
        return string;

    def _formatStack(self, i, stack):
        return "#{0} {file}({line}): {function}()\n".format(i, **stack);

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
        return self._file;

    @final
    def getLine(self):
        """Return the line number where the exception was raise.

        @return: int The line number where the exception was raise.
        """
        return self._line;

    @final
    def getTrace(self):
        """Return the stack trace as list.

        @return: list of tuples like (file, line, method, message)
        """
        return self.__trace;

    @final
    def getTraceAsString(self):
        """Return the stack trace as string.

        @return: string The stack trace as string.
        """
        return self.__string;

    def __str__(self):
        """Return the string representation of exception.

        @return: string representation of exception.
        """
        string = '';
        if self._previous:
            string += str(self._previous);
            string += '\nNext ';
        string += \
        "exception '{0}' with message '{1}' in {2}:{3}\n".format(
            type(self).__name__,
            self._message,
            self._file,
            self._line,
        );
        string += "Stack trace:\n";
        string += self.__string;
        return string;

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
