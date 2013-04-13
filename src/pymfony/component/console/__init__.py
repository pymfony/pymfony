# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import sys;
import re;

from pymfony.component.system import clone;
from pymfony.component.system import Tool;
from pymfony.component.system import IteratorAggregateInterface;
from pymfony.component.system import CountableInterface;
from pymfony.component.system.exception import UnexpectedValueException;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.types import Array;
from pymfony.component.system.types import Convert;

from pymfony.component.console.output import OutputInterface;
from pymfony.component.console.output import ConsoleOutput;
from pymfony.component.console.input import StringInput
from pymfony.component.console.input import ArgvInput;

"""
"""


class ParameterBag(IteratorAggregateInterface, CountableInterface):
    """ParameterBag is a container for key/value pairs.

    @author Fabien Potencier <fabien@symfony.com>

    @api

    """


    def __init__(self, parameters = None):
        """Constructor.

        @param dict parameters A dictionary of parameters

        @api

        """
        if parameters is None:
            parameters = dict();
        assert isinstance(parameters, dict);

        self._parameters = parameters;


    def all(self):
        """Returns the parameters.

        @return dict A dictionary of parameters

        @api

        """

        return self._parameters;


    def keys(self):
        """Returns the parameter keys.

        @return list A list of parameter keys

        @api

        """

        return list(self._parameters.keys());


    def replace(self, parameters = None):
        """Replaces the current parameters by a new set.

        @param dict parameters A dictionary of parameters

        @api

        """
        if parameters is None:
            parameters = dict();
        assert isinstance(parameters, dict);

        self._parameters = parameters;


    def add(self, parameters = None):
        """Adds parameters.

        @param dict parameters An dictionary of parameters

        @api

        """
        if parameters is None:
            parameters = dict();
        assert isinstance(parameters, dict);

        self._parameters.update(parameters);


    def get(self, path, default = None, deep = False):
        """Returns a parameter by name.

        @param string  path    The key
        @param mixed   default The default value if the parameter key does not exist
        @param boolean deep    If True, a path like foo[bar] will find deeper items

        @return mixed

        @raise InvalidArgumentException

        @api

        """

        try:
            pos = str(path).index('[');
        except ValueError:
            pos = False;
        if ( not deep or False is pos) :
            if path in self._parameters:
                return self._parameters[path];
            else:
                return default;


        root = str(path)[0:pos];
        if not root in self._parameters :
            return default;


        value = self._parameters[root];
        currentKey = None;
        i = pos - 1;
        for char in range(len(path)):
            i += 1;
            if ('[' == char) :
                if (None is not currentKey) :
                    raise InvalidArgumentException(
                        'Malformed path. Unexpected "[" at position {0}.'
                        ''.format(str(i))
                    );


                currentKey = '';
            elif (']' == char) :
                if (None is currentKey) :
                    raise InvalidArgumentException(
                        'Malformed path. Unexpected "]" at position {0}.'
                        ''.format(str(i))
                    );

                if isinstance(value, list):
                    value = Array.toDict(value, True);
                if not isinstance(value, dict) or currentKey not in value :
                    return default;


                value = value[currentKey];
                currentKey = None;
            else :
                if (None is currentKey) :
                    raise InvalidArgumentException(
                        'Malformed path. Unexpected "{0}" at position {1}.'
                        ''.format(char, str(i))
                    );


                currentKey += char;



        if (None is not currentKey) :
            raise InvalidArgumentException(
                'Malformed path. Path must end with "]".'
            );


        return value;


    def set(self, key, value):
        """Sets a parameter by name.

        @param string key   The key
        @param mixed  value The value

        @api

        """

        self._parameters[key] = value;


    def has(self, key):
        """Returns True if the parameter is defined.

        @param string key The key

        @return Boolean True if the parameter exists, False otherwise

        @api

        """

        return key in self._parameters;


    def remove(self, key):
        """Removes a parameter.

        @param string key The key

        @api

        """

        try:
            del self._parameters[key];
        except KeyError:
            pass;

    def getAlpha(self, key, default = '', deep = False):
        """Returns the alphabetic characters of the parameter value.

        @param string  key     The parameter key
        @param mixed   default The default value if the parameter key does not exist
        @param boolean deep    If True, a path like foo[bar] will find deeper items

        @return string The filtered value

        @api

        """

        return re.sub('[^A-Za-z]', '', str(self.get(key, default, deep)));


    def getAlnum(self, key, default = '', deep = False):
        """Returns the alphabetic characters and digits of the parameter value.

        @param string  key     The parameter key
        @param mixed   default The default value if the parameter key does not exist
        @param boolean deep    If True, a path like foo[bar] will find deeper items

        @return string The filtered value

        @api

        """

        return re.sub('[\W]', '', str(self.get(key, default, deep)));


    def getDigits(self, key, default = '', deep = False):
        """Returns the digits of the parameter value.

        @param string  key     The parameter key
        @param mixed   default The default value if the parameter key does not exist
        @param boolean deep    If True, a path like foo[bar] will find deeper items

        @return string The filtered value

        @api

        """

        return re.sub('[\D]', '', str(self.get(key, default, deep)));


    def getInt(self, key, default = 0, deep = False):
        """Returns the parameter value converted to integer.

        @param string  key     The parameter key
        @param mixed   default The default value if the parameter key does not exist
        @param boolean deep    If True, a path like foo[bar] will find deeper items

        @return integer The filtered value

        @api

        """

        value = self.get(key, default, deep);
        if isinstance(value, int):
            return value;

        value = str(value);
        value = Convert.str2int(value);

        return int(value);


    def __iter__(self):
        """Returns an iterator for parameters.

        @return iterator An iterator instance

        """

        return iter(self._parameters);


    def __len__(self):
        """Returns the number of parameters.

        @return int The number of parameters

        """

        return len(self._parameters);


class Request(ArgvInput):
    def __init__(self, argv = None, attributes = None):
        if attributes is None:
            attributes = dict();
        self.__argv = list(argv);
        self.initialize(argv, attributes);

    def __clone__(self):
        self.attributes = clone(self.attributes);

    def initialize(self, argv = None, attributes = None):
        if attributes is None:
            attributes = dict();
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

    def getArgv(self):
        """

        @return list
        """
        return list(self.__argv);


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
        """Constructor.

        @param string  content The response content

        @api
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

        @return Response

        @api

        """

        if not self._content :
            return self;

        if 0 != self._statusCode:
            self.getErrorOutput().writeln(self._content, self._outputType);
        else:
            self.writeln(self._content, self._outputType);

        return self;



    def setContent(self, content):
        """Sets the response content.

        Valid types are strings, numbers, and objects that implement a __str__() method.

        @param mixed content

        @return Response

        @raise UnexpectedValueException

        @api

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

        @return string Content

        @api

        """

        return self._content;

    def setOutputType(self, outputType):
        """Sets the output type.

        @param integer The type of output

        @return Response

        @api

        """

        self._outputType = outputType;

        return self;

    def getOutputType(self):
        """Gets the output type.

        @return integer The output type

        @api

        """

        return self._outputType;

    def setStatusCode(self, code, text = None):
        """Sets the response status code.

        @param integer code CLI status code
        @param mixed   text CLI status text

        If the status text is None it will be automatically populated for the
        known status codes and left empty otherwise.

        @return Response

        @raise InvalidArgumentException When the CLI status code is not valid

        @api

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

        @return integer Status code

        @api

        """

        return self._statusCode;

    def isInvalid(self):
        """Is response invalid?

        @return Boolean

        @api

        """

        return self._statusCode < 0 or self._statusCode > 255;
