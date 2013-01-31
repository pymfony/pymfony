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

import abc;
import inspect;

__all__ = [
    'abstract',
    'interface',
    'Object'
];

class MetaClass(abc.ABCMeta):
    pass;

def abstractclass(obj):
    obj.__abstractclass__ = obj;
    return obj;

def abstract(obj):
    if isinstance(obj, type(abstract)):
        return  abc.abstractmethod(obj);
    elif isinstance(obj, type(MetaClass)):
        return abstractclass(obj);
    return obj;

def interface(obj):
    return abstractclass(obj);

class Abstract():
    __abstractclass__ = None;
    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is Object:
            if cls is cls.__abstractclass__:
                return False;
        return NotImplemented;

@abstract
class Object(object, Abstract):
    __metaclass__ = MetaClass;
    def __copy__(self):
        return CloneObject(self);

class CloneObject(Object):
    def __init__(self, instanceOrig):
        typeOrig = type(instanceOrig);
        for subclass in typeOrig.mro():
            if subclass not in type(self).mro():
                type(self).register(subclass);
        for name in dir(instanceOrig):
            try:
                setattr(self, name, getattr(instanceOrig, name));
            except AttributeError:
                pass;

@abstract
class Tool(Object):
    @classmethod
    def isAbstract(cls, obj):
        abstractclass = getattr(obj, '__abstractclass__', None);
        return inspect.isabstract(obj) or obj is abstractclass;


    @classmethod
    def isCallable(cls, closure):
        try:
            if hasattr(closure, '__call__'):
                    return True;
            if repr(closure).startswith("<") and repr(closure).endswith(">"):
                if " at 0x" in repr(closure):
                    return True;
                if "'function'" in str(type(closure)):
                    return True;
                if "'builtin_function_or_method'" in str(type(closure)):
                    return True;
        except BaseException:
            pass;
        return False;

    @classmethod
    def split(cls, string, sep="."):
        """Split a string.

        Return tuple (head, tail) where tail is everything after
        the final <sep>. Either part may be empty."""
        # set i to index beyond p's last slash
        i = len(string);
        while i and string[i-1] not in sep:
            i = i - 1;
        head, tail = string[:i], string[i:]; # now tail has no "."
        head2 = head;
        while head2 and head2[-1] in sep:
            head2 = head2[:-1];
        head = head2 or head;
        return head, tail;

@abstract
class Array(Object):
    @classmethod
    def toDict(cls, l):
        assert isinstance(l, list);
        d = dict();
        i = 0;
        for i in range(len(l)):
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
        for (k, v) in d.iteritems():
            pairs.append((k, v));
        seen = {};
        for k, v in pairs:
            marker = v;
            if marker not in seen.keys():
                seen[marker] = 1;
                append(k, v);

        return result;


class ReflectionClass(Object):
    def __init__(self, argument):
        assert issubclass(argument, (object, Abstract));
        self._class = argument;

        self._filename = None;
        self._mro = None;

    def getFileName(self):
        if self._filename is not None:
            return self._filename;

        try:
            self._filename = inspect.getabsfile(self._class);
        except TypeError:
            self._filename = False;
        return self._filename;

    def getmro(self):
        if self._mro is not None:
            return self._mro;

        self._mro = inspect.getmro(self._class);
        return self._mro;

class ReflectionObject(ReflectionClass):
    def __init__(self, argument):
        assert isinstance(argument, (Object, type(Abstract)));
        ReflectionClass.__init__(self, argument.__class__);
