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

from pymfony.component.system import Object;
from pymfony.component.system import final;

class StandardException(Exception, Object):
    def __init__(self, message="", code=0, previous=None):
        """Construct the exception

        @param message: string The Exception message to raise.
        @param code: int The Exception code.
        @param previous: BaseException The previous exception used for
                         the exception chaining.
        """
        if previous:
            assert isinstance(previous, BaseException);

        self.__string = "".join(traceback.format_stack()[:-1]);
        self.__trace = traceback.extract_stack()[:-1];
        self._message = str(message);
        self._code = int(code);
        self._file = self.__trace[-1][0];
        self._line = self.__trace[-1][1];
        self._previous = previous;


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
        return self._trace;

    @final
    def getTraceAsString(self):
        """Return the stack trace as string.

        @return: string The stack trace as string.
        """
        return self._string;

    def __str__(self):
        """Return the string representation of exception.

        @return: string representation of exception.
        """
        return self._string;

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
