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

import sys;
if sys.version_info[0] >= 3:
    basestring = str;
import re;

from pymfony.component.system import Object;
from pymfony.component.system import interface;

from pymfony.component.dependency.exception import ParameterNotFoundException;
from pymfony.component.dependency.exception import RuntimeException;
from pymfony.component.dependency.exception import ParameterCircularReferenceException;
from pymfony.component.dependency.exception import LogicException;

@interface
class ParameterBagInterface(Object):

    def clear(self):
        """Clears all parameters."""
        pass;

    def add(self, parameters):
        """Adds parameters to the service container parameters.

        @param parameters: dict An array of parameters
        """
        pass;

    def all(self):
        """Gets the service container parameters.
        
        @return: dict An array of parameters
        """
        pass;

    def get(self, name):
        """Gets a service container parameter.
        
        @param name: string The parameter name

        @return: mixed The parameter value

        @raise ParameterNotFoundException: if the parameter is not defined
        """

    def set(self, name, value):
        """Sets a service container parameter.

        @param name: string The parameter name
        @param value: mixed The parameter value
        """
        pass;

    def has(self, name):
        """Returns true if a parameter name is defined.
        
        @param name: string The parameter name
        @return: Boolean true if the parameter name is defined, false otherwise
        """
        pass;

    def resolve(self):
        """Replaces parameter placeholders (%name%)
        by their values for all parameters.
        """
        pass;

    def resolveValue(self, value):
        """Replaces parameter placeholders (%name%) by their values.

        @param value: mixed A value

        @raise ParameterNotFoundException: 
        if a placeholder references a parameter that does not exist 
        """
        pass;

    def escapeValue(self, value):
        """Escape parameter placeholders %

        @param mixed $value

        @return: mixed
        """
        pass;

    def unescapeValue(self, value):
        """Unescape parameter placeholders %

        @param value:  mixed

        @return: mixed
        """
        pass;

class ParameterBag(ParameterBagInterface):
    def __init__(self, parameters=None):
        if parameters is None:
            parameters = dict();
        else:
            assert isinstance(parameters, dict);

        self._parameters = dict();
        self._resolved = False;

        self.add(parameters);

    def _formatName(self, name):
        return str(name).lower();

    def clear(self):
        self._parameters = dict();

    def add(self, parameters):
        assert isinstance(parameters, dict);

        for name, value in parameters.items():
            name = self._formatName(name);
            self._parameters[name] = value;

    def all(self):
        return self._parameters;

    def get(self, name):
        name = self._formatName(name);

        if not self.has(name):
            raise ParameterNotFoundException(name);

        return self._parameters[name];

    def set(self, name, value):
        name = self._formatName(name);
        self._parameters[name] = value;

    def has(self, name):
        name = self._formatName(name);
        return name in self._parameters.keys();

    def remove(self, name):
        name = self._formatName(name);
        del self._parameters[name];

    def resolve(self):
        if self._resolved:
            return;

        params = dict();
        for name, value in self._parameters.items():
            try:
                value = self.resolveValue(value);
                params[name] = self.unescapeValue(value);
            except ParameterNotFoundException as e:
                e.setSourceKey(name);
                raise e;

        self._parameters = params;
        self._resolved = True;

    def resolveValue(self, value, resolving=None):
        if resolving is None:
            resolving = dict();
        assert isinstance(resolving, dict);

        if isinstance(value, dict):
            args = dict();
            for k, v in value.items():
                k = self.resolveValue(k, resolving);
                args[k] = self.resolveValue(v, resolving);
            return args;

        if not isinstance(value, basestring):
            return value;

        return self.resolveString(value, resolving);

    def resolveString(self, value, resolving=None):
        if resolving is None:
            resolving = dict();
        assert isinstance(resolving, dict);

        match = re.search(r"^%([^%\s]+)%$", value);
        if match:
            key = match.group(1).lower();
            if key in resolving.keys():
                raise ParameterCircularReferenceException(
                    list(resolving.keys())
                );
            resolving[key] = True;
            if self._resolved:
                return self.get(key);
            else:
                return self.resolveValue(self.get(key), resolving);

        def callback(match):
            key = match.group(1);
            if key is None:
                return "%%";
            key = key.lower();
            if key in resolving.keys():
                raise ParameterCircularReferenceException(
                    list(resolving.keys())
                );
            resolved = self.get(key);
            if not isinstance(resolved, (str, float, int)):
                raise RuntimeException(
                    'A string value must be composed of strings and/or '
                    'numbers, but found parameter "{0}" of type {1} inside '
                    'string value "{2}".'
                    "".format(key, type(resolved), value)
                );
            resolved = str(resolved);
            resolving[key] = True;
            if self.isResolved():
                return resolved;
            else:
                return self.resolveString(resolved, resolving);

        return re.sub(r"%%|%([^%\s]+)%", callback, value);

    def isResolved(self):
        return self._resolved;

    def escapeValue(self, value):
        if isinstance(value, basestring):
            return value.replace("%", "%%");

        if isinstance(value, dict):
            result = dict();
            for k, v in value.items():
                result[k] = self.escapeValue(v);
            return result;

        return value;

    def unescapeValue(self, value):
        if isinstance(value, basestring):
            return value.replace("%%", "%");

        if isinstance(value, dict):
            result = dict();
            for k, v in value.items():
                result[k] = self.unescapeValue(v);
            return result;

        return value;

class FrozenParameterBag(ParameterBag):
    def __init__(self, parameters=None):
        if parameters is None:
            parameters = dict();
        else:
            assert isinstance(parameters, dict);

        self._parameters = parameters;
        self._resolved = True;

    def clear(self):
        raise LogicException(
            'Impossible to call clear() on a frozen ParameterBag.'
        );

    def add(self, parameters):
        raise LogicException(
            'Impossible to call add() on a frozen ParameterBag.'
        );

    def set(self, name, value):
        raise LogicException(
            'Impossible to call set() on a frozen ParameterBag.'
        );



