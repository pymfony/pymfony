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



class ServiceCircularReferenceException(RuntimeException):
    """This exception is thrown when a circular reference is detected.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self, serviceId, path):
        assert isinstance(path, list);

        RuntimeException.__init__(self,
            'Circular reference detected for service "{0}", path: "{1}".'
            ''.format(serviceId, ' -> '.join(path)
        ));

        self.__serviceId = None;
        self.__path = None;


        self.__serviceId = serviceId;
        self.__path = path;


    def getServiceId(self):

        return self.__serviceId;


    def getPath(self):

        return self.__path;


class ScopeWideningInjectionException(RuntimeException):
    """Thrown when a scope widening injection is detected.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """


    def __init__(self, sourceServiceId, sourceScope, destServiceId, destScope):

        RuntimeException.__init__(self,
            'Scope Widening Injection detected: The definition "{0}" references '
            'the service "{1}" which belongs to a narrower scope. Generally, it '
            'is safer to either move "{2}" to scope "{3}" or alternatively rely '
            'on the provider pattern by injecting the container itself, and '
            'requesting the service "{4}" each time it is needed. In rare, '
            'special cases however that might not be necessary, then you can '
            'set the reference to strict=False to get rid of this error.'
            ''.format(
           sourceServiceId,
           destServiceId,
           sourceServiceId,
           destScope,
           destServiceId
        ));

        self.__sourceServiceId = None;
        self.__sourceScope = None;
        self.__destServiceId = None;
        self.__destScope = None;

        self.__sourceServiceId = sourceServiceId;
        self.__sourceScope = sourceScope;
        self.__destServiceId = destServiceId;
        self.__destScope = destScope;


    def getSourceServiceId(self):

        return self.__sourceServiceId;


    def getSourceScope(self):

        return self.__sourceScope;


    def getDestServiceId(self):

        return self.__destServiceId;


    def getDestScope(self):

        return self.__destScope;




class ScopeCrossingInjectionException(RuntimeException):
    """This exception is thrown when the a scope crossing injection is detected.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """


    def __init__(self, sourceServiceId, sourceScope, destServiceId, destScope):

        RuntimeException.__init__(self,
            'Scope Crossing Injection detected: The definition "{0}" references '
            'the service "{1}" which belongs to another scope hierarchy. '
            'This service might not be available consistently. Generally, it '
            'is safer to either move the definition "{2}" to scope "{3}", or '
            'declare "{4}" as a child scope of "{5}". If you can be sure that '
            'the other scope is always active, you can set the reference to '
            'strict=False to get rid of this error.'.format(
           sourceServiceId,
           destServiceId,
           sourceServiceId,
           destScope,
           sourceScope,
           destScope
        ));

        self.__sourceServiceId = None;
        self.__sourceScope = None;
        self.__destServiceId = None;
        self.__destScope = None;
    
        self.__sourceServiceId = sourceServiceId;
        self.__sourceScope = sourceScope;
        self.__destServiceId = destServiceId;
        self.__destScope = destScope;


    def getSourceServiceId(self):

        return self.__sourceServiceId;


    def getSourceScope(self):

        return self.__sourceScope;


    def getDestServiceId(self):

        return self.__destServiceId;


    def getDestScope(self):

        return self.__destScope;
