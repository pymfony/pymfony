# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import sys

from pymfony.component.console.input import StringInput
from pymfony.component.system import Object;
from pymfony.component.system import Tool;
from pymfony.component.system.exception import UnexpectedValueException;
from pymfony.component.console.output import OutputInterface;
from pymfony.component.console.output import ConsoleOutput;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.console.input import ArgvInput;
from pymfony.component.system.types import ParameterBag;
from pymfony.component.console.input import InputInterface
from pymfony.component.system import clone
"""
"""


class Request(ArgvInput):
    def __init__(self, argv = None, attributes = dict()):
        self.__argv = list(argv);
        self.initialize(argv, attributes);

    def __clone__(self):
        self.attributes = clone(self.attributes);

    def initialize(self, argv = None, attributes = dict()):
        self.attributes = ParameterBag(attributes);
        ArgvInput.__init__(self, argv);

    @classmethod
    def create(cls, argv):
        """Creates a Request based on a given argv and configuration.

        @param list argv A list of parameters from the CLI (in the argv format)

        @return: Request

        @api:
        """
        request = cls(argv, dict());
        return request;

    @classmethod
    def createFromGlobals(cls):
        """Creates a new request with values from PYTHON's sys.argv.

        @return: Request
        """
        request = cls(sys.argv, dict());
        return request;

    @classmethod
    def createFromString(cls, string):
        """Creates a new request with values from PYTHON's sys.argv.

        @param: string inputString  A string of parameters from the CLI

        @return: Request
        """
        request = cls(StringInput(string), dict());
        return request;

    def getArgv(self):
        """

        @return list
        """
        return list(self.__argv);

    def setCommandName(self, command):
        self.attributes.set('_command', command);

    def getCommandName(self):
        if self.attributes.has('_command'):
            return self.attributes.get('_command');
        return self.getFirstArgument();


class Response(ConsoleOutput):
    statusTexts = {
        # Status codes translation table.
        #
        # @see: http://www.faqs.org/docs/abs/HTML/exitcodes.html
        # @see: /usr/include/sysexits.h

        0   : "OK",
        1   : "Error",
        2   : "Misuse of shell builtins",

        64  : "Command line usage error",
        65  : "Data format error",
        66  : "Cannot open input",
        67  : "Addressee unknown",
        68  : "Host name unknown",
        69  : "Service unavailable",
        70  : "Internal software error",
        71  : "System error (e.g., can't fork)",
        72  : "Critical OS file missing",
        73  : "Can't create (user) output file",
        74  : "IO error",
        75  : "Temp failure; user is invited to retry",
        76  : "Remote error in protocol",
        77  : "Permission denied",
        78  : "Configuration error",

        126 : "Command invoked cannot execute",
        127 : "Command not found",
        128 : "Invalid argument to exit",
        129 : 'Fatal error signal "1"',
        130 : 'Control-C',
        131 : 'Fatal error signal "3"',
        132 : 'Fatal error signal "4"',
        133 : 'Fatal error signal "5"',
        134 : 'Fatal error signal "6"',
        135 : 'Fatal error signal "7"',
        136 : 'Fatal error signal "8"',
        137 : 'Fatal error signal "9"',

        255 : "Exit status out of range",
    };

    def __init__(self, content = '', status = 0):
        """
     * Constructor.
     *
     * @param string  content The response content

     * @api
        """

        self._content = None;
        self._outputType = None;
        self._statusCode = None;

        ConsoleOutput.__init__(self);

        self.setContent(content);
        self.setStatusCode(status);
        self.setOutputType(OutputInterface.OUTPUT_NORMAL);



    def send(self):
        """Sends content.
     *
     * @param integer type The type of output
     *
     * @return Response
     *
     * @api

        """

        if 0 != self._statusCode:
            self.getErrorOutput().writeln(self._content, self._outputType);
        else:
            self.writeln(self._content, self._outputType);

        return self;



    def setContent(self, content):
        """Sets the response content.
     *
     * Valid types are strings, numbers, and objects that implement a __str__() method.
     *
     * @param mixed content
     *
     * @return Response
     *
     * @raise UnexpectedValueException
     *
     * @api

        """

        if (not Tool.isCallable(getattr(content, '__str__', None))) :
            raise UnexpectedValueException(
                'The Response content must be a string or object implementing '
                '__str__(), "'+type(content)+'" given.'
            );

        self._content = str(content);

        return self;


    def getContent(self):
        """Gets the current response content.
     *
     * @return string Content
     *
     * @api

        """

        return self._content;

    def setOutputType(self, outputType):
        """Sets the output type.
     *
     * @param integer The type of output
     *
     * @return Response
     *
     * @api

        """

        self._outputType = outputType;

        return self;

    def getOutputType(self):
        """Gets the output type.
     *
     * @return integer The output type
     *
     * @api

        """

        return self._outputType;

    def setStatusCode(self, code, text = None):
        """Sets the response status code.
     *
     * @param integer code CLI status code
     * @param mixed   text CLI status text
     *
     * If the status text is None it will be automatically populated for the known
     * status codes and left empty otherwise.
     *
     * @return Response
     *
     * @raise InvalidArgumentException When the CLI status code is not valid
     *
     * @api

        """
        code = int(code);
        self._statusCode = code;
        if self.isInvalid() :
            self._statusCode = 255;
            raise InvalidArgumentException(
                'The CLI status code "{0}" is not valid.'.format(code)
            );


        if (None is text) :
            if code in self.statusTexts:
                self.statusText = self.statusTexts[code];
            else:
                self.statusText = '';

            return self;


        if (False is text) :
            self.statusText = '';

            return self;


        self.statusText = text;

        return self;


    def getStatusCode(self):
        """Retrieves the status code for the current web response.
     *
     * @return integer Status code
     *
     * @api

        """

        return self._statusCode;

    def isInvalid(self):
        """Is response invalid?
     *
     * @return Boolean
     *
     * @api

        """

        return self._statusCode < 0 or self._statusCode > 255;

