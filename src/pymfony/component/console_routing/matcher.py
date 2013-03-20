# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import re;

from pymfony.component.console import Request;

from pymfony.component.console_routing import RouteCollection;
from pymfony.component.console_routing import Route;
from pymfony.component.console_routing import Router;
from pymfony.component.console_routing.exception import ResourceNotFoundException;
from pymfony.component.console_routing.interface import RequestMatcherInterface;

"""
"""

class RequestMatcher(RequestMatcherInterface):
    """RequestMatcher matches Request based on a set of routes.

    @author: Fabien Potencier <fabien@symfony.com>

    @api

    """

    REQUIREMENT_MATCH     = 0;
    REQUIREMENT_MISMATCH  = 1;
    ROUTE_MATCH           = 2;
    BIND_MISMATCH         = 3;
    BIND_MATCH            = 4;

    def __init__(self, routes):
        """Constructor.

        @param: RouteCollection routes  A RouteCollection instance

        @api

        """
        assert isinstance(routes, RouteCollection);

        self._routes = None;
        # @var: RouteCollection

        self._routes = routes;


    def matchRequest(self, request):
        assert isinstance(request, Request);

        ret = self._matchCollection(request, self._routes)
        if (ret) :
            return ret;

        raise ResourceNotFoundException();


    def _matchCollection(self, request, routes):
        """Tries to match a request with a set of routes.

        @param: Request          request The path info to be parsed
        @param RouteCollection routes   The set of routes

        @return dict An array of parameters
        """
        assert isinstance(routes, RouteCollection);
        assert isinstance(request, Request);

        for name, route in routes.all().items():
            assert isinstance(route, Route);

            # bind the input against the command specific arguments/options
            status = self._handleRouteBinds(request, name, route);

            if (self.BIND_MISMATCH == status[0]) :
                continue;

            if request.hasArgument(Router.COMMAND_KEY):
                if request.getArgument(Router.COMMAND_KEY) != route.getPath():
                    continue;

            status = self._handleRouteRequirements(request, name, route);

            if (self.REQUIREMENT_MISMATCH == status[0]) :
                continue;


            return self._getAttributes(route, name, request);



    def _getAttributes(self, route, name, request):
        """Returns an array of values to use as request attributes.

        As this method requires the Route object, it is not available
        in matchers that do not have access to the matched Route instance
        (like the PHP and Apache matcher dumpers).

        @param: Route  route      The route we are matching against
        @param string name       The name of the route
        @param: Request          request The path info to be parsed

        @return dict An array of parameters

        """
        assert isinstance(route, Route);
        assert isinstance(request, Request);

        attributes = dict();
        attributes['_route'] = name;
        attributes['_controller'] = route.getDefault('_controller');
        attributes.update(request.getArguments());

        return attributes;

    def _handleRouteBinds(self, request, name, route):
        """Handles specific route binding.:

        @param: Request request The path
        @param string name     The route name
        @param Route  route    The route

        @return list The first element represents the status, the second contains additional information

        """
        assert isinstance(route, Route);
        assert isinstance(request, Request);

        try:
            request.bind(route);
            request.validate();
        except Exception:
            return [self.BIND_MISMATCH, None];
        else:
            return [self.BIND_MATCH, None];


    def _handleRouteRequirements(self, request, name, route):
        """Handles specific route requirements.:

        @param: Request request The path
        @param string name     The route name
        @param Route  route    The route

        @return list The first element represents the status, the second contains additional information

        """
        assert isinstance(route, Route);
        assert isinstance(request, Request);

        for key, regexp in route.getRequirements().items():
            regexp = "^" + regexp + "$";
            if request.hasArgument(key):
                if not re.search(regexp, request.getArgument(key)):
                    return [self.REQUIREMENT_MISMATCH, None];
            elif request.hasOption(key):
                if not re.search(regexp, request.getOption(key)):
                    return [self.REQUIREMENT_MISMATCH, None];
            else:
                return [self.REQUIREMENT_MISMATCH, None];

        return [self.REQUIREMENT_MATCH, None];
