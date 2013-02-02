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

from pymfony.component.system import Object;
from pymfony.component.system import interface;
from pymfony.component.system.exception import BadMethodCallException;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import LogicException;
from pymfony.component.system.exception import OutOfBoundsException;
from pymfony.component.system.exception import RuntimeException;

@interface
class ExceptionInterface(Object):
    pass;

class RuntimeException(RuntimeException, ExceptionInterface):
    pass;


class LogicException(LogicException, ExceptionInterface):
    pass;

class OutOfBoundsException(OutOfBoundsException, ExceptionInterface):
    pass;

class BadMethodCallException(BadMethodCallException, ExceptionInterface):
    pass;

class InvalidArgumentException(InvalidArgumentException, ExceptionInterface):
    pass;


class ServiceNotFoundException(InvalidArgumentException):
    def __init__(self, identifier, sourceId=None):
        self.__id = identifier;
        self.__sourceId = sourceId;

        self.updateRepr();

    def updateRepr(self):
        if self.__sourceId is None:
            self.message = (
                'You have requested a non-existent parameter "{0}".'
                "".format(self.__id)
            );
        else:
            self.message = (
                'The service "{1}" has a dependency '
                'on a non-existent service "{0}".'
                "".format(self.__id, self.__sourceId)
            );

    def getKey(self):
        return self.__key;

    def setSourceId(self, key):
        self.__sourceId = key;

    def getSourceId(self):
        return self.__sourceId;


class ParameterNotFoundException(InvalidArgumentException):
    def __init__(self, key, sourceId=None, sourceKey=None):
        self.__key = key;
        self.__sourceKey = sourceKey;
        self.__sourceId = sourceId;

        self.updateRepr();

    def updateRepr(self):
        if not self.__sourceId is None:
            self.message = (
                'The service "{1}" has a dependency '
                'on a non-existent parameter "{0}".'
                "".format(self.__key, self.__sourceId)
            );
        elif not self.__sourceKey is None:
            self.message = (
                'The parameter "{1}" has a dependency '
                'on a non-existent parameter "{0}".'
                "".format(self.__key, self.__sourceKey)
            );
        else:
            self.message = (
                'You have requested a non-existent parameter "{0}".'
                "".format(self.__key)
            );

    def getKey(self):
        return self.__key;

    def setSourceKey(self, key):
        self.__sourceKey = key;

    def getSourceKey(self):
        return self.__sourceKey;

    def setSourceId(self, key):
        self.__sourceId = key;

    def getSourceId(self):
        return self.__sourceId;

class ParameterCircularReferenceException(RuntimeException):
    pass;
