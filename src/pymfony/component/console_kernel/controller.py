# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import inspect

from pymfony.component.system import Object;
from pymfony.component.system import Tool;
from pymfony.component.system.oop import interface;
from pymfony.component.system.types import String;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import RuntimeException;
from pymfony.component.system.reflection import ReflectionClass;
from pymfony.component.system.reflection import ReflectionObject;
from pymfony.component.system.reflection import ReflectionMethod;
from pymfony.component.system.reflection import ReflectionFunction;
from pymfony.component.system.reflection import ReflectionParameter;

from pymfony.component.console import Request;

"""
"""

@interface
class ControllerResolverInterface(Object):
    """A ControllerResolverInterface implementation knows how to determine the
     controller to execute based on a Request object.

     It can also determine the arguments to pass to the Controller.

     A Controller can be any valid PYTHON callable.

     @author Fabien Potencier <fabien@symfony.com>

     @api

    """

    def getController(self, request):
        """Returns the Controller instance associated with a Request.

        As several resolvers can exist for a single application, a resolver must
        return False when it is not able to determine the controller.

        The resolver must only raise an exception when it should be able to load
        controller but cannot because of some errors made by the developer.

        @param Request request A Request instance

        @return mixed|Boolean A PYTHON callable representing the Controller,
                              or False if this resolver is not able to determine
                             the controller:

        @raise InvalidArgumentException|\LogicException If the controller can't be found

        @api

        """
        assert isinstance(request, Request);

    def getArguments(self, request, controller):
        """Returns the arguments to pass to the controller.

        @param Request request    A Request instance
        @param mixed   controller A PHP callable

        @return array An array of arguments to pass to the controller

        @raise RuntimeException When value for argument given is not provided

        @api

        """
        assert isinstance(request, Request);




class ControllerResolver(ControllerResolverInterface):
    """ControllerResolver.

    This implementation uses the '_controller' request attribute to determine
    the controller to execute and uses the request attributes to determine
    the controller method arguments.

    @author Fabien Potencier <fabien@symfony.com>

    @api

    """

    PREFIX_OPTION = "_o_";

    def __init__(self):
        """Constructor.
        """

    def getController(self, request):
        """Returns the Controller instance associated with a Request.

        As several resolvers can exist for a single application, a resolver must
        return False when it is not able to determine the controller.

        The resolver must only raise an exception when it should be able to load
        controller but cannot because of some errors made by the developer.

        @param Request request A ArgvInput instance

        @return mixed|Boolean A PYTHON callable representing the Controller,
                              or False if this resolver is not able to determine
                             the controller:

        @raise InvalidArgumentException|\LogicException If the controller can't be found

        @api

        """
        assert isinstance(request, Request);

        controller = request.attributes.get('_controller');
        if ( not controller) :
            return False;


        if Tool.isCallable(controller) :
            return controller;


        if not isinstance(controller, String):
            return False;

        if ':' not in controller:
            r = ReflectionClass(controller);
            if r.exists():
                instance = r.newInstance();
                if Tool.isCallable(instance):
                    return instance;

        controller, method = self._createController(controller);

        if not hasattr(controller, method) :
            raise InvalidArgumentException(
                'Method "{0}.{1}" does not exist.'.format(
                    ReflectionObject(controller).getName(), method)
                );


        return getattr(controller, method);


    def getArguments(self, request, controller):
        """Returns the arguments to pass to the controller.

        @param Request request    A Request instance
        @param mixed   controller A PYTHON callable

        @return list

        @raise RuntimeException When value for argument given is not provided

        @api

        """
        assert isinstance(request, Request);

        if inspect.ismethod(controller):
            r = ReflectionMethod(controller);
        elif inspect.isfunction(controller) or isinstance(controller, String):
            r = ReflectionFunction(controller);
        else:
            r = ReflectionObject(controller);
            r = r.getMethod('__call__');

        return self._doGetArguments(request, controller, r.getParameters());

    def _doGetArguments(self, request, controller, parameters):
        assert isinstance(request, Request);
        assert isinstance(parameters, list);

        attributes = request.attributes.all();
        arguments = list();

        for param in parameters:
            assert isinstance(param, ReflectionParameter);
            name = param.getName();
            attr = name;
            # strip option prefix
            if name.startswith(self.PREFIX_OPTION):
                attr = attr[len(self.PREFIX_OPTION):];

            attr = attr.replace('_', '-');

            if attr.startswith('-'):
                attr = '_' + attr[1:];

            arg = [name, attr];

            if arg[0] == 'request':
                arguments.append(request);
            elif arg[1] in attributes:
                arguments.append(attributes[arg[1]]);
            elif request.hasOption(arg[1]):
                arguments.append(request.getOption(arg[1]));
            elif param.isDefaultValueAvailable():
                arguments.append(param.getDefaultValue());
            else:
                raise RuntimeException(
                    'Controller "{0}" requires that you provide a value for '
                    'the "{1}" argument (because there is no default value or '
                    'because there is a non optional argument after this one).'
                    ''.format(repr(controller), name)
                );

        return arguments;


    def _createController(self, controller):
        """Returns a callable for the given controller.

        @param string controller A Controller string

        @return callable A PYTHON callable

        @raise InvalidArgumentException

        """

        if '::' not in controller :
            raise InvalidArgumentException(
                'Unable to find controller "{0}".'.format(controller)
            );


        className, method = controller.split('::', 2);

        r = ReflectionClass(className);

        if ( not r.exists()) :
            raise InvalidArgumentException(
                'Class "{0}" does not exist.'.format(className)
            );

        return (r.newInstance(), method);
