# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;
from pymfony.component.system import Object
from pymfony.component.kernel import KernelInterface
from pymfony.component.system.exception import InvalidArgumentException
from pymfony.component.system import ReflectionClass
from pymfony.component.console_kernel.controller import ControllerResolver as BaseControllerResolver
from pymfony.component.dependency.interface import ContainerInterface
from pymfony.component.system.exception import LogicException
from pymfony.component.dependency.interface import ContainerAwareInterface

"""
"""

class ControllerNameParser(Object):
    """ControllerNameParser converts controller from the short notation a:b:c
    (BlogBundle:Post:index) to a fully-qualified class.method string:
    (Bundle.BlogBundle.Controller.PostController.indexAction).

    @author: Fabien Potencier <fabien@symfony.com>

    """


    def __init__(self, kernel):
        """Constructor.

        @param: KernelInterface kernel A KernelInterface instance

        """
        assert isinstance(kernel, KernelInterface);

        self._kernel = None;

        self._kernel = kernel;


    def parse(self, controller):
        """Converts a short notation a:b:c to a class.method.

        @param: string controller A short notation controller (a:b:c)

        @return string A string with class.method

        @raise InvalidArgumentException when the specified bundle is not enabled:
                                          or the controller cannot be found

        """
        parts = controller.split(':');
        if (3  != len(parts)) :
            raise InvalidArgumentException(
                'The "{0}" controller is not a valid a:b:c controller string.'
                ''.format(controller)
            );


        bundle, controller, action = parts;
        controller = controller.replace('/', '.');
        bundles = list();

        # this raise an exception if there is no such bundle:
        for b in self._kernel.getBundle(bundle, False):
            test = b.getNamespace()+'.controller.'+controller+'Controller';
            if ReflectionClass(test).exists() :
                return test+'::'+action+'Action';


            bundles.append(b.getName());
            msg = (
                'Unable to find controller "{0}:{1}" - class "{2}" does not '
                'exist.'.format(
                    bundle,
                    controller,
                    test,
            ));


        if (len(bundles) > 1) :
            msg = (
                'Unable to find controller "{0}:{1}" in bundles {2}.'
                ''.format(
                    bundle,
                    controller,
                    ', '.join(bundles)
            ));


        raise InvalidArgumentException(msg);


class ControllerResolver(BaseControllerResolver):
    """ControllerResolver.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    def __init__(self, container, parser):
        """Constructor.

        @param: ContainerInterface   container A ContainerInterface instance
        @param ControllerNameParser parser    A ControllerNameParser instance
        @param LoggerInterface      logger    A LoggerInterface instance

        """
        assert isinstance(parser, ControllerNameParser);
        assert isinstance(container, ContainerInterface);



        self._container = None;
        self._parser = None;


        self._container = container;
        self._parser = parser;


    def _createController(self, controller):
        """Returns a callable for the given controller.

        @param: string controller A Controller string

        @return mixed A PHP callable

        @raise LogicException When the name could not be parsed
        @raise InvalidArgumentException When the controller class does(, not exist):

        """

        if '::' not in controller :
            count = controller.count(':');
            if (2 == count) :
                # controller in the a:b:c notation then
                controller = self._parser.parse(controller);
            elif (1 == count) :
                # controller in the service:method notation
                (service, method) = controller.split(':', 2);

                return [self._container.get(service), method];
            else :
                raise LogicException(
                    'Unable to parse the controller name "{0}".'
                    ''.format(controller)
                );



        (className, method) = controller.split('::', 2);

        r = ReflectionClass(className);
        if not r.exists() :
            raise InvalidArgumentException(
                'Class "{0}" does not exist.'.format(className
            ));


        controller = r.newInstance();
        if (isinstance(controller, ContainerAwareInterface)) :
            controller.setContainer(self._container);


        return [controller, method];
