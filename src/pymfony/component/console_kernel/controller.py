# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import inspect

from pymfony.component.system.oop import interface;
from pymfony.component.system import Object;
from pymfony.component.console import Request
from pymfony.component.system import Tool
from pymfony.component.system.exception import InvalidArgumentException
from pymfony.component.system import ReflectionClass
from pymfony.component.system import ReflectionObject
from pymfony.component.system.exception import RuntimeException

"""
"""

@interface
class ControllerResolverInterface(Object):
    """A ControllerResolverInterface implementation knows how to determine the
 * controller to execute based on a Request object.
 *
 * It can also determine the arguments to pass to the Controller.
 *
 * A Controller can be any valid PYTHON callable.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """

    def getController(self, request):
        """Returns the Controller instance associated with a Request.
     *
     * As several resolvers can exist for a single application, a resolver must
     * return False when it is not able to determine the controller.
     *
     * The resolver must only raise an exception when it should be able to load
     * controller but cannot because of some errors made by the developer.
     *
     * @param Request request A Request instance
     *
     * @return mixed|Boolean A PYTHON callable representing the Controller,
     *                       or False if this resolver is not able to determine
                             the controller:
     *
     * @raise InvalidArgumentException|\LogicException If the controller can't be found
     *
     * @api

        """
        assert isinstance(request, Request);

    def getArguments(self, request, controller):
        """Returns the arguments to pass to the controller.
     *
     * @param Request request    A Request instance
     * @param mixed   controller A PHP callable
     *
     * @return array An array of arguments to pass to the controller
     *
     * @raise RuntimeException When value for argument given is not provided
     *
     * @api

        """
        assert isinstance(request, Request);




class ControllerResolver(ControllerResolverInterface):
    """ControllerResolver.
 *
 * This implementation uses the '_controller' request attribute to determine
 * the controller to execute and uses the request attributes to determine
 * the controller method arguments.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """

    def __init__(self):
        """Constructor.
        """

    def getController(self, request):
        """Returns the Controller instance associated with a Request.
     *
     * As several resolvers can exist for a single application, a resolver must
     * return False when it is not able to determine the controller.
     *
     * The resolver must only raise an exception when it should be able to load
     * controller but cannot because of some errors made by the developer.
     *
     * @param Request request A ArgvInput instance
     *
     * @return mixed|Boolean A PYTHON callable representing the Controller,
     *                       or False if this resolver is not able to determine
                             the controller:
     *
     * @raise InvalidArgumentException|\LogicException If the controller can't be found
     *
     * @api

        """
        assert isinstance(request, Request);

        controller = request.attributes.get('_controller');
        if ( not controller) :
            return False;


        if Tool.isCallable(controller) :
            return controller;


        if not isinstance(controller, str):
            return False;

        controller, method = self._createController(controller);

        if not hasattr(controller, method) :
            raise InvalidArgumentException(
                'Method "{0}.{1}" does not exist.'.format(
                    ReflectionObject(controller).getName(), method)
                );


        return getattr(controller, method);

    # TODO: add this in to a ReflectionFunction class
    def __getRequiredArgs(self, func):
        args, varargs, varkw, defaults = inspect.getargspec(func);
        if defaults:
            args = args[:-len(defaults)];
        return args;   # *args and **kwargs are not required, so ignore them.


    def getArguments(self, request, controller):
        """Returns the arguments to pass to the controller.
     *
     * @param Request request    A Request instance
     * @param mixed   controller A PHP callable
     *
     * @return list
     *
     * @raise RuntimeException When value for argument given is not provided
     *
     * @api

        """
        assert isinstance(request, Request);

        # TODO: make more efficient PYTHON arguments binding
        args = self.__getRequiredArgs(controller);

        arguments = list();

        for name in args:
            attr = name.replace('_', '-');
            if attr.startswith('-'):
                attr[0] = '_';
            arg = [name, attr];
            if arg[0] == 'self':
                continue;
            if arg[0] == 'request':
                arguments.append(request);
            elif request.attribute.has(arg[1]):
                arguments.append(request.attribute.get(arg[1]));
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
     *
     * @param string controller A Controller string
     *
     * @return callable A PYTHON callable
     *
     * @raise InvalidArgumentException

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
