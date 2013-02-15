# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import abc;
import inspect;
import pickle;

from pymfony.component.system.oop import OOPMeta;
from pymfony.component.system.oop import abstract;

"""
"""

__all__ = [
    'OOPObject',
    'AbstractString',
    'AbstractCloneBuilder',
];

class Abstract():
    __abstractclass__ = False;
    __isfinalclass__ = False;
    __finalmethods__ = frozenset();
    @classmethod
    def __subclasshook__(cls, subclass):
        if issubclass(cls, OOPObject):
            if cls is cls.__abstractclass__:
                return False;
        return NotImplemented;
@abstract
class OOPObject(object, Abstract):
    __metaclass__ = OOPMeta;

class AbstractString(str, OOPObject):
    @classmethod
    def __subclasshook__(cls, subclass):
        if issubclass(subclass, basestring):
            return True;
        return NotImplemented;

class AbstractCloneBuilder(OOPObject):
    TYPES_MAP = {
        'int': int,
        'float': float,
        'complex': complex,
        'str': str,
        'list': list,
        'tuple': tuple,
        'bytes': bytes,
        'bytearray': bytearray,
        'range': lambda o: range(len(o)),
        'set': lambda o: o.copy(),
        'frozenset': lambda o: o.copy(),
        'dict': dict,
        'bool': bool,

        'unicode': unicode,
        'long': long,
        'xrange': lambda o: xrange(len(o)),
        'buffer': buffer,
    };
