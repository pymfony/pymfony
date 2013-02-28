# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import re;
import sys;

from pymfony.component.system.oop import abstract;
from pymfony.component.system import Object;
from pymfony.component.system import IteratorAggregateInterface;
from pymfony.component.system import CountableInterface;
from pymfony.component.system.exception import InvalidArgumentException;

if sys.version_info < (3,):
    from pymfony.component.system.py2.types import *;
else:
    from pymfony.component.system.py3.types import *;

"""
"""

class OrderedDict(AbstractOrderedDict):
    pass;

class String(AbstractString):
    """Base string to provide back compatibility"""
    pass;

class Array(OrderedDict):
    @classmethod
    def toDict(cls, l, strKeys=False):
        assert isinstance(l, list);
        d = dict();
        i = 0;
        for i in range(len(l)):
            if strKeys:
                d[str(i)] = l[i];
            else:
                d[i] = l[i];
            i = i + 1;
        return d;

    @classmethod
    def uniq(cls, iterable):
        assert isinstance(iterable, (list, dict));
        if isinstance(iterable, list):
            d = cls.toDict(iterable);
            result = [];
            def append(k, v):
                result.append(v);
        else:
            d = iterable;
            result = {};
            def append(k, v):
                result[k] = v;

        pairs = list();
        for k, v in d.items():
            pairs.append((k, v));
        seen = {};
        for k, v in pairs:
            marker = v;
            if marker not in seen.keys():
                seen[marker] = 1;
                append(k, v);

        return result;

    @classmethod
    def diff(cls, leftSide, rightSide):
        """Computes the difference of lists

        @param leftSide: list The list to compare from
        @param rightSide: list The list to compare against

        @return: list
        """
        leftSide = list(leftSide);
        rightSide = list(rightSide);
        return [item for item in leftSide if item not in rightSide];

    @classmethod
    def diffKey(cls, dict1, dict2, *args):
        """Compares dict1 against dict2 and returns the difference.

        @param: dict dict1 The dict to compare from
        @param: dict dict2 A dict to compare against
        @param: dict ...   More dicts to compare against

        @return: Returns a dict containing all the entries from dict1 that
                 are not present in any of the other dicts.
        """
        args = list(args);
        args = [dict2] + args;
        diff = {};
        while args:
            new = args.pop(0);
            for key, value in dict1.items():
                if key not in new.keys():
                    diff[key] = value;
        return diff;


class ParameterBag(IteratorAggregateInterface, CountableInterface):
    """ParameterBag is a container for key/value pairs.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """


    def __init__(self, parameters = dict()):
        """Constructor.
     *
     * @param dict parameters A dictionary of parameters
     *
     * @api

        """
        assert isinstance(parameters, dict);

        self._parameters = parameters;


    def all(self):
        """Returns the parameters.
     *
     * @return dict A dictionary of parameters
     *
     * @api

        """

        return self._parameters;


    def keys(self):
        """Returns the parameter keys.
     *
     * @return list A list of parameter keys
     *
     * @api

        """

        return list(self._parameters.keys());


    def replace(self, parameters = dict()):
        """Replaces the current parameters by a new set.
     *
     * @param dict parameters A dictionary of parameters
     *
     * @api

        """
        assert isinstance(parameters, dict);

        self._parameters = parameters;


    def add(self, parameters = dict()):
        """Adds parameters.
     *
     * @param dict parameters An dictionary of parameters
     *
     * @api

        """
        assert isinstance(parameters, dict);

        self._parameters.update(parameters);


    def get(self, path, default = None, deep = False):
        """Returns a parameter by name.
     *
     * @param string  path    The key
     * @param mixed   default The default value if the parameter key does not exist:
     * @param boolean deep    If True, a path like foo[bar] will find deeper items
     *
     * @return mixed
     *
     * @raise InvalidArgumentException
     *
     * @api

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
     *
     * @param string key   The key
     * @param mixed  value The value
     *
     * @api

        """

        self._parameters[key] = value;


    def has(self, key):
        """Returns True if the parameter is defined.:
     *
     * @param string key The key
     *
     * @return Boolean True if the parameter exists, False otherwise:
     *
     * @api

        """

        return key in self._parameters;


    def remove(self, key):
        """Removes a parameter.
     *
     * @param string key The key
     *
     * @api

        """

        try:
            del self._parameters[key];
        except KeyError:
            pass;

    def getAlpha(self, key, default = '', deep = False):
        """Returns the alphabetic characters of the parameter value.
     *
     * @param string  key     The parameter key
     * @param mixed   default The default value if the parameter key does not exist:
     * @param boolean deep    If True, a path like foo[bar] will find deeper items
     *
     * @return string The filtered value
     *
     * @api

        """

        return re.sub('[^A-Za-z]', '', str(self.get(key, default, deep)));


    def getAlnum(self, key, default = '', deep = False):
        """Returns the alphabetic characters and digits of the parameter value.
     *
     * @param string  key     The parameter key
     * @param mixed   default The default value if the parameter key does not exist:
     * @param boolean deep    If True, a path like foo[bar] will find deeper items
     *
     * @return string The filtered value
     *
     * @api

        """

        return re.sub('[\W]', '', str(self.get(key, default, deep)));


    def getDigits(self, key, default = '', deep = False):
        """Returns the digits of the parameter value.
     *
     * @param string  key     The parameter key
     * @param mixed   default The default value if the parameter key does not exist:
     * @param boolean deep    If True, a path like foo[bar] will find deeper items
     *
     * @return string The filtered value
     *
     * @api

        """

        return re.sub('[\D]', '', str(self.get(key, default, deep)));


    def getInt(self, key, default = 0, deep = False):
        """Returns the parameter value converted to integer.
     *
     * @param string  key     The parameter key
     * @param mixed   default The default value if the parameter key does not exist:
     * @param boolean deep    If True, a path like foo[bar] will find deeper items
     *
     * @return integer The filtered value
     *
     * @api

        """

        value = self.get(key, default, deep);
        if isinstance(value, int):
            return value;

        value = str(value);
        value = Convert.str2int(value);

        return int(value);


    def __iter__(self):
        """Returns an iterator for parameters.
     *
     * @return iterator An iterator instance

        """

        return iter(self._parameters);


    def __len__(self):
        """Returns the number of parameters.
     *
     * @return int The number of parameters

        """

        return len(self._parameters);

@abstract
class Convert(Object):

    @classmethod
    def str2int(cls, value):
        """A PHP conversion
        """
        if isinstance(value, float):
            return int(value);
        if isinstance(value, int):
            return value;

        value = str(value);

        if not value:
            return 0;

        ALLOW_CHARS = "0123456789.eE+-";

        if value[0] not in ALLOW_CHARS:
            return 0;

        LNUM = "([0-9]+)";
        DNUM = "(?:([0-9]*)[\.]"+LNUM+")"+\
            "|(?:"+LNUM+"[\.]([0-9]*))";
        EXPONENT_DNUM = ""+\
            "([+-]?)(?:(?:"+LNUM+"|"+DNUM+")(?:[eE]([+-]?)"+LNUM+")?)";

        testValue = '';
        for char in value:
            if char in ALLOW_CHARS:
                testValue += char;
            else:
                break;

        m = re.match("^"+EXPONENT_DNUM+"$", testValue);
        if not m:
            return 0;

        # declare
        sign = "+"; #m[1];
        
        intPart = "0"; #a code: 2 3 5";
        intPartSize = 0;
        
        decPart = ""; #a code: 4 6";
        decPartSize = 0;
        
        signExp = "+"; #a code: 7";
        valueExp = 0; #a code: 8";


        # assignation
        if m.group(1):
            sign = m.group(1);

        if m.group(2):
            intPart = m.group(2);
            intPartSize = len(intPart);

        elif m.group(3):
            intPart = m.group(3);
            intPartSize = len(intPart);

        elif m.group(5):
            intPart = m.group(5);
            intPartSize = len(intPart);

        if m.group(4):
            decPart = m.group(4);
            decPartSize = len(decPart);

        elif m.group(6):
            decPart = m.group(6);
            decPartSize = len(decPart);

        if m.group(7):
            signExp = m.group(7);

        if m.group(8):
            valueExp = int(m.group(8));


        # populate the out var

        out = "";

        if (signExp == "-"):
            if (intPartSize <= valueExp):
                out += "0"; # remove the right part of colon;
            else:
                out += intPart[0:-valueExp];

        else: # exp is positif
            int_dec_part = intPart + decPart;
            addZeroNb = valueExp - decPartSize;
            if (addZeroNb < 0):
                out += int_dec_part[0:addZeroNb];

            else: # concatenate zero to right

                zeroStr = "0" * addZeroNb;
                out += int_dec_part + zeroStr;

        out = out.lstrip("0");

        out = sign + out;

        return int(out);
