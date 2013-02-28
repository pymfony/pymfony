# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from json import decoder;
from json import scanner;

from pymfony.component.system.py26.types import OrderedDict;

"""
"""

__all__ = [
    'AbstractJSONDecoderOrderedDict',
];

def JSONObject(match, context, _w=decoder.WHITESPACE.match):
    pairs = OrderedDict(); # Change to an ordered dict
    s = match.string
    end = _w(s, match.end()).end()
    nextchar = s[end:end + 1]
    # Trivial empty object
    if nextchar == '}':
        return pairs, end + 1
    if nextchar != '"':
        raise ValueError(decoder.errmsg("Expecting property name", s, end))
    end += 1
    encoding = getattr(context, 'encoding', None)
    strict = getattr(context, 'strict', True)
    iterscan = JSONScanner.iterscan
    while True:
        key, end = decoder.scanstring(s, end, encoding, strict)
        end = _w(s, end).end()
        if s[end:end + 1] != ':':
            raise ValueError(decoder.errmsg("Expecting : delimiter", s, end))
        end = _w(s, end + 1).end()
        try:
            value, end = iterscan(s, idx=end, context=context).next()
        except StopIteration:
            raise ValueError(decoder.errmsg("Expecting object", s, end))
        pairs[key] = value
        end = _w(s, end).end()
        nextchar = s[end:end + 1]
        end += 1
        if nextchar == '}':
            break
        if nextchar != ',':
            raise ValueError(decoder.errmsg("Expecting , delimiter", s, end - 1))
        end = _w(s, end).end()
        nextchar = s[end:end + 1]
        end += 1
        if nextchar != '"':
            raise ValueError(decoder.errmsg("Expecting property name", s, end - 1))
    object_hook = getattr(context, 'object_hook', None)
    if object_hook is not None:
        pairs = object_hook(pairs)
    return pairs, end
scanner.pattern(r'{')(JSONObject);

ANYTHING = list(decoder.ANYTHING);
ANYTHING[0] = JSONObject;
JSONScanner = scanner.Scanner(ANYTHING);

class AbstractJSONDecoderOrderedDict(decoder.JSONDecoder):
    _scanner = JSONScanner;
