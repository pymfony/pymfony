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
    def uniq(cls, iterable, value_formater = None):
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
            if value_formater :
                marker = value_formater(v);
            else:
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
                else:
                    diff.pop(key, None);
        return diff;


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

        m = re.search("^"+EXPONENT_DNUM+"$", testValue);
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
