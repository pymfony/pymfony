# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.system import clone;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.reflection import ReflectionClass;

from pymfony.component.console.input import InputOption;

from pymfony.component.console_routing import Router as BaseRouter;
from pymfony.component.console_routing import RouteCollection;
from pymfony.component.console_routing.matcher import RequestMatcher as BaseRequestMatcher;
from pymfony.component.console_routing.exception import ResourceNotFoundException;

from pymfony.component.console_kernel.dependency import ContainerAwareConsoleKernel;
from pymfony.component.console_kernel.interface import ConsoleKernelInterface;

from pymfony.component.dependency.interface import ContainerInterface;

from pymfony.bundle.framework_bundle.controller import ControllerNameParser as BaseControllerNameParser;


"""
"""

class ConsoleKernel(ContainerAwareConsoleKernel):
    """This ConsoleKernel is used to manage scope changes of the DI container.

    @author: Fabien Potencier <fabien@symfony.com>
    @author: Johannes M. Schmitt <schmittjoh@gmail.com>
    """
    def forward(self, controller, attributes = None):
        """Forwards the request to another controller.

        @param: string controller The controller name (a string like BlogBundle:Post:index)
        @param: dict  attributes An array of request attributes

        @return: Response A Response instance

        @deprecated: in 2.2, will be removed in 2.3
        """
        if attributes is None:
            attributes = dict();
        assert isinstance(attributes, dict);

#        trigger_error('forward() is deprecated since version 2.2 and will be removed in 2.3.', E_USER_DEPRECATED);

        attributes['_controller'] = controller;

        subRequest = clone(self._container.get('request'));
        subRequest.attributes.replace(attributes);

        return self.handle(subRequest, ConsoleKernelInterface.SUB_REQUEST);


class ControllerNameParser(BaseControllerNameParser):
    """ControllerNameParser converts controller from the short notation a:b:c
    (BlogBundle:Post:index) to a fully-qualified class::method string
    (Bundle.BlogBundle.Command.PostCommand::indexAction).

    @author: Fabien Potencier <fabien@symfony.com>
    """

    def parse(self, controller):
        """Converts a short notation a:b:c to a class.method.

        @param: string controller A short notation controller (a:b:c)

        @return: string A string with class.method

        @raise InvalidArgumentException: when the specified bundle is not enabled
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
            test = b.getNamespace()+'.command.'+controller+'Command';
            if ReflectionClass(test).exists() :
                return test+'::'+action+'Action';


            bundles.append(b.getName());
            msg = (
                'Unable to find command "{0}:{1}" - class "{2}" does not '
                'exist.'.format(
                    bundle,
                    controller,
                    test,
            ));


        if (len(bundles) > 1) :
            msg = (
                'Unable to find command "{0}:{1}" in bundles {2}.'
                ''.format(
                    bundle,
                    controller,
                    ', '.join(bundles)
            ));


        raise InvalidArgumentException(msg);

class Router(BaseRouter):
    def __init__(self, container, resource, options = None):
        """Constructor.

        @param: ContainerInterface container  A ContainerInterface instance
        @param: mixed              resource   The main resource to load
        @param: dict               options    A dictionary of options
        """
        if options is None:
            options = dict();
        assert isinstance(container, ContainerInterface);

        loader  = container.get('console.routing.loader');
        BaseRouter.__init__(self, loader, resource, options=options);

        self.__container = container;
        self.__defaultRouteName = container.getParameter('console.router.default_route');
        environment = container.getParameter('kernel.environment');

        self.getDefinition().addOption(InputOption('--env', '-e', InputOption.VALUE_REQUIRED, 'The Environment name.', environment));
        self.getDefinition().addOption(InputOption('--no-debug', None, InputOption.VALUE_NONE, 'Switches off debug mode.'));

    def getRequestMatcher(self):
        if self._matcher is None:
            self._matcher = RequestMatcher(self.getRouteCollection(), self.__defaultRouteName);

        return self._matcher;

    def getRouteCollection(self):
        if self._collection is None:
            self._collection = BaseRouter.getRouteCollection(self);
            self.__resolveParameters(self._collection);

        return self._collection;

    def __resolveParameters(self, collection):
        """Replaces placeholders with service container parameter values in:
        - the route defaults,
        - the route requirements,
        - the route path.

        @param: RouteCollection collection
        """
        assert isinstance(collection, RouteCollection);

        for route in collection.all().values():
            for name, value in route.getDefaults().items():
                route.setDefault(name, self.__resolve(value));

            for name, value in route.getRequirements().items():
                route.setRequirement(name, self.__resolve(value));

            route.setPath(self.__resolve(route.getPath()));

    def __resolve(self, value):
        return self.__container.getParameterBag().resolveValue(value);


class RequestMatcher(BaseRequestMatcher):
    """This RequestMatcher apply default route if no route match

    @author: Alexandre Quercia <alquerci@email.com>
    """
    def __init__(self, routes, defaultRouteName = ''):
        BaseRequestMatcher.__init__(self, routes);

        self.__defaultRouteName = defaultRouteName;


    def matchRequest(self, request):
        try:
            return BaseRequestMatcher.matchRequest(self, request);
        except ResourceNotFoundException as e:
            if self.__defaultRouteName:
                route = self._routes.get(self.__defaultRouteName);
                self._handleRouteBinds(request, self.__defaultRouteName, route);
                return self._getAttributes(route, self.__defaultRouteName, request);
            else:
                raise e;
