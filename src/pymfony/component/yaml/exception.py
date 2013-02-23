# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.system import Object
from pymfony.component.system.oop import interface
from pymfony.component.system.exception import RuntimeException

"""
"""

@interface
class ExceptionInterface(Object):
    """Exception interface for all exceptions thrown by the component.

    @author: Fabien Potencier <fabien@symfony.com>

    @api

    """



class RuntimeException(RuntimeException, ExceptionInterface):
    """Exception class thrown(, when an error occurs during parsing.):

    @author: Romain Neutron <imprec@gmail.com>

    @api

    """




class ParseException(RuntimeException):
    """Exception class thrown(, when an error occurs during parsing.):

    @author: Fabien Potencier <fabien@symfony.com>

    @api

    """

    def __init__(self, message, parsedLine = -1, snippet = None, parsedFile = None, previous = None):
        """Constructor.

        @param: string    message    The error message
        @param integer   parsedLine The line where the error occurred
        @param integer   snippet    The snippet of code near the problem
        @param string    parsedFile The file name where the error occurred
        @param Exception previous   The previous exception

        """
        if previous:
            assert isinstance(previous, Exception);

        self.__parsedFile = None;
        self.__parsedLine = None;
        self.__snippet = None;
        self.__rawMessage = None;


        self.__parsedFile = parsedFile;
        self.__parsedLine = parsedLine;
        self.__snippet = snippet;
        self.__rawMessage = message;

        self.__updateRepr();

        RuntimeException.__init__(self, self._message, 0, previous);


    def getSnippet(self):
        """Gets the snippet of code near the error.

        @return: string The snippet of code

        """

        return self.__snippet;


    def setSnippet(self, snippet):
        """Sets the snippet of code near the error.

        @param: string snippet The code snippet

        """

        self.__snippet = snippet;

        self.__updateRepr();


    def getParsedFile(self):
        """Gets the filename where the error occurred.

        This method returns None if a string is parsed.:

        @return: string The filename

        """

        return self.__parsedFile;


    def setParsedFile(self, parsedFile):
        """Sets the filename where the error occurred.

        @param: string parsedFile The filename

        """

        self.__parsedFile = parsedFile;

        self.__updateRepr();


    def getParsedLine(self):
        """Gets the line where the error occurred.

        @return: integer The file line

        """

        return self.__parsedLine;


    def setParsedLine(self, parsedLine):
        """Sets the line where the error occurred.

        @param: integer parsedLine The file line

        """

        self.__parsedLine = parsedLine;

        self.__updateRepr();


    def __updateRepr(self):

        self._message = self.__rawMessage;

        dot = False;
        if self._message.endswith('.'):
            self._message = self._message[:-1];
            dot = True;


        if (None is not self.__parsedFile) :
            self._message += ' in {0}'.format(repr(self.__parsedFile));


        if (self.__parsedLine >= 0) :
            self._message += ' at line {0}'.format(self.__parsedLine);


        if (self.__snippet) :
            self._message += ' (near "{0}")'.format(self.__snippet);


        if (dot) :
            self._message += '.';





class DumpException(RuntimeException):
    """Exception class thrown(, when an error occurs during dumping.):

    @author: Fabien Potencier <fabien@symfony.com>

    @api

    """

