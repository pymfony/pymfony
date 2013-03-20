# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import sys;
import os;
import inspect;
import re;

from pymfony.component.system.oop import abstract;
from pymfony.component.system.oop import interface;

if sys.version_info < (3,):
    from pymfony.component.system.py2 import *;
else:
    from pymfony.component.system.py3 import *;

if sys.version_info < (3, 3):
    import imp;
    def _load_source(modulename, filename):
        return imp.load_source(modulename, filename);
else:
    import importlib;
    def _load_source(modulename, filename):
        loader = importlib.machinery.SourceFileLoader(modulename, filename);
        return loader.load_module();

"""
"""

class Object(OOPObject):
    pass;

@interface
class SerializableInterface(Object):
    def serialize(self):
        pass;

    def unserialize(self, serialized):
        pass;

@interface
class ArrayAccessInterface(Object):
    """Interface to provide accessing objects as container.
    """
    def __getitem__(self, item):
        """Returns the value at specified item.

        `for` loops expect that an `IndexError` will be raised for illegal
        indexes to allow proper detection of the end of the sequence.

        @param item: mixed The item to retrieve.

        @raise IndexError: If of a value outside the set of indexes for the
                           sequence (after any special interpretation of
                           negative values).
        @raise TypeError: If key is of an inappropriate type.
        @raise KeyError: If key is missing (not in the container).
        """
        pass;

    def __setitem__(self, item, value):
        """Assigns a value to the specified item.

        @param item: mixed The item to assign the value to.
        @param value: mixed The value to set.
        """
        pass;

    def __delitem__(self, item):
        """Deletes an item.

        @param item: mixed The item to delete.
        """
        pass;

    def __contains__(self, item):
        """Whether a item exists

        This method is executed when using `in` and `not in`

        @param item: mixed An item to check for.

        @return: True on success or False on failure.
        """
        pass;

@interface
class TraversableInterface(Object):
    pass;

@interface
class IteratorInterface(TraversableInterface):
    def __iter__(self):
        """Return the iterator object itself.

        This is required to allow both containers and iterators to be used
        with the for and in statements.

        This method corresponds to the tp_iter slot of the type structure
        for Python objects in the Python/C API.

        @return: iterator

        @raise Exception: On failure.
        """
        pass;

    def next(self):
        """Return the next item from the container.

        This method corresponds to the tp_iternext slot of the type structure
        for Python objects in the Python/C API.

        @return: mixed The next item from the container.

        @raise StopIteration: If there are no further items.
        """
        pass;

@interface
class IteratorAggregateInterface(TraversableInterface):
    """Interface to create an external Iterator.
    """
    def __iter__(self):
        """Retrieve an external iterator.

        This method is called when an iterator is required for a container.

        @return: iterator|IteratorInterface|TraversableInterface

        @raise Exception: On failure.
        """
        pass;

@interface
class CountableInterface(Object):
    """Classes implementing CountableInterface can be used with the len()
    function.
    """
    def __len__(self):
        """This method is executed when using the len() function.

        @return: integer The length of the object (>= 0).
        """
        pass;


class CloneBuilder(AbstractCloneBuilder):
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
                            if inspect.ismethod(value):
                                cloneMethod = CloneBuilder.cloneMethod(value, self);
                                setattr(self, name, cloneMethod);
                            else:
                                setattr(self, name, value);
                        except Exception:
                            pass;

                for classType in instance.__class__.__mro__:
                    if classType not in self.__class__.__mro__:
                        self.__class__.register(classType);

        clone = CloneObject(instance);

        if isinstance(clone, ClonableInterface) or (
            hasattr(clone, '__clone__') and hasattr(clone.__clone__, '__call__')
        ):
            clone.__clone__();

        return clone;

    @classmethod
    def cloneMethod(cls, method, instance):
        MethodType = type(cls.cloneMethod);
        assert isinstance(method, MethodType);
        clone = MethodType(method.im_func, instance, method.im_class);
        return clone;

def clone(instance):
    """Creating a copy of an object with fully replicated properties is not
    always the wanted behavior.

    Object Cloning

    Creating a copy of an object with fully replicated properties is not
    always the wanted behavior. A good example of the need for copy
    constructors, is if you have an object which represents a GTK window
    and the object holds the resource of this GTK window, when you create
    a duplicate you might want to create a new window with the same
    properties and have the new object hold the resource of the new
    window. Another example is if your object holds a reference to another
    object which it uses and when you replicate the parent object you
    want to create a new instance of this other object so that the replica
    has its own separate copy.

    An object copy is created by using the clone keyword (which calls the
    object's __clone__() method if possible). An object's __clone__()
    method cannot be called directly.

        copy_of_object = clone(object);

    When an object is cloned, PYTHON will perform a shallow copy of all of
    the object's properties. Any properties that are references to other
    variables, will remain references.

        void __clone__( void )

    Once the cloning is complete, if a __clone__() method is defined, then
    the newly created object's __clone__() method will be called, to allow
    any necessary properties that need to be changed.

    @src: http://www.php.net/manual/en/language.oop5.cloning.php

    @param: The object instance to clone.

    @return: The clone instance passed as a parameter
    """

    return CloneBuilder.build(instance);


@interface
class ClonableInterface(Object):
    def __clone__(self):
        """Allow any necessary properties that need to be changed after the
        cloning is complete.

        @see: clone method
        """

@abstract
class Tool(Object):
    @classmethod
    def isAbstract(cls, obj):
        abstractclass = getattr(obj, '__abstractclass__', False);
        return inspect.isabstract(obj) or obj is abstractclass;

    @classmethod
    def isCallable(cls, closure):
        if hasattr(closure, '__call__'):
            return True;

        elif isinstance(closure, basestring):
            if '.' in closure:
                # Static class method call
                try:
                    closure = ClassLoader.load(closure);
                except Exception:
                    return False;
            else:
                # Simple callback
                try:
                    closure = eval(closure);
                except Exception:
                    return False;

        return False;

    @classmethod
    def isPhpCallable(cls, closure):
        if isinstance(closure, list):
            if len(closure) != 2:
                return False;

            if not isinstance(closure[1], basestring):
                return False;

            if not isinstance(closure[0], object):
                # Static class method call
                try:
                    closure[0] = ClassLoader.load(closure[0]);
                except Exception:
                    return False;
                closure = getattr(closure[0], closure[1], False);
                if closure is False:
                    return False;
            else:
                # Object method call
                closure = getattr(closure[0], closure[1], False);
                if closure is False:
                    return False;

        return cls.isCallable(closure);

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

    @classmethod
    def stripcslashes(cls, string):
        HEXA = '0123456789abcdefABCDEF';
        target = "";
        nlen = len(string);
        numtmp = dict();

        source = string[:];
        end = nlen;
        i = 0;
        while(i < end):
            if source[i] == '\\' and i+1 < end :
                i+=1;
                if source[i] == 'n': target+='\n'; nlen-=1; i+=1;continue;
                elif source[i] == 'r': target+='\r'; nlen-=1; i+=1;continue;
                elif source[i] == 'a': target+='\a'; nlen-=1; i+=1;continue;
                elif source[i] == 't': target+='\t'; nlen-=1; i+=1;continue;
                elif source[i] == 'v': target+='\v'; nlen-=1; i+=1;continue;
                elif source[i] == 'b': target+='\b'; nlen-=1; i+=1;continue;
                elif source[i] == 'f': target+='\f'; nlen-=1; i+=1;continue;
                elif source[i] == '\\': target+='\\'; nlen-=1; i+=1;continue;
                elif source[i] == 'x':
                    if i+1 < end and source[i+1] in HEXA:
                        i+=1;
                        numtmp = source[i];
                        if i+1 < end and source[i+1] in HEXA:
                            i+=1;
                            numtmp += source[i];
                            nlen-=3;
                        else:
                            nlen-=2;
                        target += numtmp.decode("hex");
                        i+=1;continue;
                    # break is left intentionally
                y = 0;
                while (i < end and source[i] in '01234567' and y<3):
                    numtmp[y] = source[i];
                    y+=1; i+=1;
                
                if y:
                    target += str(hex(int(numtmp, 8)))[2:].decode("hex");
                    nlen-=y;
                    i-=1;
                else:
                    target+=source[i];
                    nlen-=1;
                
            else:
                target+=source[i];
            i+=1;

        return target;



class ClassLoader(Object):
    __classes = {};
    __badClasses = {};
    __validVarNamePattern = re.compile('^[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*$');

    @classmethod
    def load(cls, qualClassName):
        """Load a fully qualify class name.

        @param qualClassName: string  A fully qualify class name to load.

        @return: type  A class

        @raise ImportError: When the class can not be load

        """

        if qualClassName in cls.__classes:
            return cls.__classes[qualClassName];

        if qualClassName in cls.__badClasses:
            raise ImportError('No class named "{0}".'.format(qualClassName));

        classType = None;

        if '.' in qualClassName:
            moduleName, className = Tool.split(qualClassName);

            try:
                module = __import__(moduleName, {}, {}, [className], 0);
            except TypeError:
                module = __import__(moduleName, {}, {}, ["__init__"], 0);
            except ImportError as e:
                cls.__badClasses[qualClassName] = True;
                raise e;

            classType = getattr(module, className, False);
        elif cls.__validVarNamePattern.search(qualClassName):
            try:
                classType = eval(qualClassName, {}, {});
            except Exception:
                classType = None;

        if classType:
            cls.__classes[qualClassName] = classType;
        else:
            cls.__badClasses[qualClassName] = True;
            raise ImportError('No class named "{0}".'.format(qualClassName));

        return classType;


class SourceFileLoader(Object):
    __badModules = {};
    __modules = {};

    @classmethod
    def load(cls, path):
        """Load a Python source file and return a representative module.

        @param path: string  The path to the file

        @return: module

        @raise ImportError: When the file can not be load

        """

        if not os.path.isfile(path):
            raise ImportError('Try to import a not exists file "{0}".'.format(path));

        if not os.access(path, os.R_OK):
            raise ImportError('Try to import a not readable file "{0}".'.format(path));

        normalizePath = cls.__normalizePath(path);

        if normalizePath in cls.__modules:
            return cls.__modules[normalizePath];

        if normalizePath in cls.__badModules:
            raise ImportError('The file "{0}" can not be imported.'.format(
                normalizePath
            ));

        try:
            module = _load_source(normalizePath, normalizePath);
            assert isinstance(module, type(sys));
        except Exception as e:
            cls.__badModules[normalizePath] = True;
            raise ImportError('The file "{0}" can not be imported; {1}'.format(
                normalizePath,
                str(e)
            ));
        else:
            cls.__modules[normalizePath] = module;

        return module;


    @classmethod
    def __normalizePath(cls, path):
        newPath = os.path.normpath(os.path.normcase(os.path.realpath(path)));
        return newPath.replace('\\', '/');
