# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import inspect

from pymfony.component.system import Object
from pymfony.component.system import ClassLoader
from pymfony.component.system import Tool
from pymfony.component.system.oop import final
from pymfony.component.system.types import String
from pymfony.component.system.exception import StandardException
from pymfony.component.system.oop import abstract

"""
"""

class ReflectionException(StandardException):
    pass;

class ReflectionParameter(Object):
    def __init__(self, function, parameter):
        """Constructor

        @param: The function to reflect parameters from.
        @param: The parameter.
        """
        self.__name = str(parameter);

        self.__defaultValue = None;
        self.__isDefaultValueAvailable = None;
        self.__isOptional = None;
        self.__position = None;

        args, varargs, varkw, defaults = inspect.getargspec(function);
        offset = -1 if inspect.ismethod(function) else 0;
        self.__position = list(args).index(self.__name) + offset;
        defaults = defaults if defaults else tuple();
        firstOptional = len(args) + offset - len(defaults);

        if self.__position >= firstOptional:
            self.__isOptional = True;
            self.__isDefaultValueAvailable = True;
            self.__defaultValue = defaults[self.__position - firstOptional];
        else:
            self.__isOptional = False;
            self.__isDefaultValueAvailable = False;


    def __str__(self):
        return self.__name;

    @final
    def __clone__(self):
        raise TypeError();

    def getName(self):
        """Gets the name of the parameter

        @return: string The name of the reflected parameter.
        """
        return self.__name;

    def getDefaultValue(self):
        """Gets the default value of the parameter for a user-defined function
        or method. If the parameter is not optional a ReflectionException will
        be raise.

        @return: mixed The parameters default value.
        """
        if not self.isOptional():
            raise ReflectionException("The parameter {0} is not optional".format(
                self.__name
            ));
        return self.__defaultValue;

    def isDefaultValueAvailable(self):
        """Checks if a default value for the parameter is available.

        @return: Boolean  TRUE if a default value is available, otherwise FALSE
        """
        return self.__isDefaultValueAvailable;

    def isOptional(self):
        """Checks if the parameter is optional.

        @return: Boolean TRUE if the parameter is optional, otherwise FALSE
        """
        return self.__isOptional;

    def getPosition(self):
        """Gets the position of the parameter.

        @return: int The position of the parameter, left to right, starting at position #0.
        """
        return self.__position;

@abstract
class AbstractReflectionFunction(Object):

    @final
    def __clone__(self):
        """The clone method prevents an object from being cloned.

        Reflection objects cannot be cloned.
        """
        raise TypeError("Reflection objects cannot be cloned.");

    @abstract
    def getParameters(self):
        """Get the parameters as a list of ReflectionParameter.

        @return: list A list of Parameters, as a ReflectionParameter object.
        """
        pass;

class ReflectionFunction(AbstractReflectionFunction):
    def __init__(self, function):
        """Constructs a ReflectionFunction object.

        @param: string|function The name of the function to reflect or a closure.

        @raise ReflectionException: When the name parameter does not contain a valid function.
        """
        if isinstance(function, String):
            try:
                function = ClassLoader.load(function);
            except ImportError:
                function = False;

        if not inspect.isfunction(function):
            raise ReflectionException(
                "The {0} parameter is not a valid function.".format(
                    function
            ))

        self._name = function.__name__;
        self._parameters = None;
        self._function = function;

    def __str__(self):
        return self._name;

    def getParameters(self):
        """Get the parameters as a list of ReflectionParameter.

        @return: list A list of Parameters, as a ReflectionParameter object.
        """
        if self._parameters is None:
            self._parameters = list();
            args = inspect.getargspec(self._function)[0];
            for arg in args:
                self._parameters.append(ReflectionParameter(self._function, arg));
        return self._parameters;


class ReflectionMethod(AbstractReflectionFunction):
    def __init__(self, method):
        """Constructs a ReflectionFunction object.

        @param: method The method to reflect.

        @raise ReflectionException: When the name parameter does not contain a valid method.
        """
        if not inspect.ismethod(method):
            raise ReflectionException(
                "The {0} parameter is not a valid method.".format(
                    method
            ))

        self._name = method.__name__;
        self._parameters = None;
        self._method = method;

    def __str__(self):
        return self._name;

    def getParameters(self):
        """Get the parameters as a list of ReflectionParameter.

        @return: list A list of Parameters, as a ReflectionParameter object.
        """
        if self._parameters is None:
            self._parameters = list();
            args = inspect.getargspec(self._method)[0];
            for arg in args[1:]:
                self._parameters.append(ReflectionParameter(self._method, arg));
        return self._parameters;


class ReflectionClass(Object):
    def __init__(self, argument):
        if isinstance(argument, String):
            qualClassName = argument;
            try:
                argument = ClassLoader.load(argument);
            except ImportError:
                argument = False;

        if argument is not False:
            assert issubclass(argument, object);
            self.__exists = True;
            self._class = argument;
            self._fileName = None;
            self._mro = None;
            self._namespaceName = None;
            self._parentClass = None;
            self._name = None;
        else:
            self.__exists = False;
            self._name = qualClassName;
            self._fileName = '';
            self._mro = tuple();
            self._namespaceName = Tool.split(qualClassName)[0];
            self._parentClass = False;
            self._class = None;


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

    def exists(self):
        return self.__exists;

    def newInstance(self, *args, **kargs):
        return self._class(*args, **kargs);


class ReflectionObject(ReflectionClass):
    def __init__(self, argument):
        assert isinstance(argument, object);

        ReflectionClass.__init__(self, argument.__class__);

        self.__object = argument;

    def getMethod(self, name):
        """Gets a ReflectionMethod for a class method.

        @param: string The method name to reflect.

        @return: ReflectionMethod A ReflectionMethod.

        @raise: ReflectionException When the method does not exist.
        """

        if hasattr(self.__object, name):
            return ReflectionMethod(getattr(self.__object, name));

        raise ReflectionException("The method {0} of class {1} does not exist.".format(
            name,
            self.getName(),
        ));
