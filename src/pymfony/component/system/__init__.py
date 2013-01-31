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
import pickle;
import sys;

__all__ = [
    'abstract',
    'interface',
    'Object'
];

class MetaClass(abc.ABCMeta):
    def __new__(cls, name, bases, namespace):
        cls = abc.ABCMeta.__new__(cls, name, bases, namespace);
        abstracts = set(cls.__abstractmethods__);
        # Compute set of abstract method names
        for name, value in namespace.items():
            if getattr(value, "__isabstractmethod__", False):
                abstracts.add(name);
        for base in bases:
            for name in getattr(base, "__interfacemethods__", set()):
                value = getattr(cls, name, None);
                if getattr(value, "__isabstractmethod__", False):
                    abstracts.add(name);
        cls.__abstractmethods__ = frozenset(abstracts);
        return cls

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
    if sys.version_info[0] >= 3:
        methods = inspect.getmembers(obj, inspect.isfunction);
    else:
        methods = inspect.getmembers(obj, inspect.ismethod);
    
    absMethods = set();

    def func(*a, **ka):
        pass;

    for name, method in methods:
        if not name.endswith('__'):
            absMethods.add(name);
            setattr(obj, name, abc.abstractmethod(func));

    obj.__interfacemethods__ = frozenset(absMethods);

    return abstractclass(obj);

class Abstract():
    __abstractclass__ = None;
    @classmethod
    def __subclasshook__(cls, subclass):
        if issubclass(cls, Object):
            if cls is cls.__abstractclass__:
                return False;
        return NotImplemented;


if sys.version_info[0] <= 2:
    @abstract
    class Object(object, Abstract):
        __metaclass__ = MetaClass;
        def __copy__(self):
            return CloneBuilder.build(self);
else:
    @abstract
    class Object(Abstract):
        __metaclass__ = MetaClass;
        def __copy__(self):
            return CloneBuilder.build(self);




class CloneBuilder(Object):
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
    };
    if sys.version_info[0] <= 2:
        TYPES_MAP.update({
            'unicode': unicode,
            'long': long,
            'xrange': lambda o: xrange(len(o)),
            'buffer': buffer,
        });
    @classmethod
    def build(cls, instance):
        """Build the clone

        @param instance: object The instance to clone
        """
        mro = type(instance).__mro__;

        class CloneObject(Object):
            __clone_mro__ = tuple(mro);
            def __init__(self, instanceOrig):
                properties = inspect.getmembers(instanceOrig);
                for name, value in properties:
                    typeName = type(value).__name__;
                    if typeName in CloneBuilder.TYPES_MAP.keys():
                        cloneValue = CloneBuilder.TYPES_MAP[typeName](value);
                        setattr(self, name, cloneValue);
                    else:
                        try:
                            setattr(self, name, value);
                        except AttributeError:
                            pass;

                for classType in instance.__class__.__mro__:
                    if classType not in self.__class__.__mro__:
                        self.__class__.register(classType);

        return CloneObject(instance);

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
        return [item for item in leftSide if item not in rightSide]


class ReflectionClass(Object):
    def __init__(self, argument):
        assert issubclass(argument, object);
        self._class = argument;

        self._fileName = None;
        self._mro = None;
        self._namespaceName = None;
        self._name = None;
        self._parentClass = None;

    def getFileName(self):
        if self._fileName is not None:
            return self._fileName;

        try:
            self._fileName = inspect.getabsfile(self._class);
        except TypeError:
            self._fileName = False;
        return self._fileName;

    def getParentClass(self):
        """
        @return: ReflexionClass|False
        """
        if self._parentClass is None:
            if len(self.getmro()) > 1:
                self._parentClass = ReflectionClass(self.getmro()[1]);
            else:
                self._parentClass = False;
        return self._parentClass;


    def getmro(self):
        if self._mro is None:
            self._mro = inspect.getmro(self._class);
        return self._mro;

    def getNamespaceName(self):
        if self._namespaceName is None:
            self._namespaceName = str(self._class.__module__);
        return self._namespaceName;

    def getName(self):
        if self._name is None:
            self._name = self.getNamespaceName()+'.'+str(self._class.__name__);
        return self._name;

class ReflectionObject(ReflectionClass):
    def __init__(self, argument):
        assert isinstance(argument, Object);
        ReflectionClass.__init__(self, argument.__class__);
