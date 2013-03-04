# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.system import Object;
from pymfony.component.system.oop import interface;

from pymfony.component.console import Request;

from pymfony.component.config.loader import LoaderInterface as BaseLoaderInterface;

"""
"""

@interface
class RequestMatcherInterface(Object):
    """RequestMatcherInterface is the interface that all request matcher classes must implement.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    def matchRequest(self, request):
        """Tries to match a request with a set of routes.

        If the matcher can not find information, it must raise one of the exceptions documented
        below.

        @param: Request request The request to match

        @return dict An array of parameters

        @raise ResourceNotFoundException If no matching resource could be found
        """
        assert isinstance(request, Request);

@interface
class RouterInterface(RequestMatcherInterface):
    """RouterInterface is the interface that all Router classes must implement.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    def getRouteCollection(self):
        """Gets the RouteCollection instance associated with this Router.

        @return: RouteCollection A RouteCollection instance

        """

@interface
class ExceptionInterface(Object):
    """ExceptionInterface

    @author: Alexandre Salom� <alexandre.salome@gmail.com>

    @api:
    """
    pass;

@interface
class LoaderInterface(BaseLoaderInterface):
    def load(self, resource, resourceType=None):
        """Loads a resource.

        @param resource: mixed
        @param resourceType: string The resource type

        @return: RouteCollection
        """
        pass
