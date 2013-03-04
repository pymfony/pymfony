# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.config.loader import DelegatingLoader as BaseDelegatingLoader;
from pymfony.component.config.loader import LoaderResolverInterface;

from pymfony.bundle.framework_bundle.controller import ControllerNameParser;

from pymfony.component.console_routing.interface import LoaderInterface;

"""
"""


class DelegatingLoader(BaseDelegatingLoader, LoaderInterface):
    """DelegatingLoader delegates route loading to other loaders using a loader resolver.

    This implementation resolves the _controller attribute from the short notation
    to the fully-qualified form (from a:b:c to class:method).:

    @author: Fabien Potencier <fabien@symfony.com>

    """


    def __init__(self, parser, resolver):
        """Constructor.

        @param: ControllerNameParser    parser   A ControllerNameParser instance
        @param LoggerInterface         logger   A LoggerInterface instance
        @param LoaderResolverInterface resolver A LoaderResolverInterface instance

        """
        assert isinstance(resolver, LoaderResolverInterface);
        assert isinstance(parser, ControllerNameParser);

        self._parser = parser;

        BaseDelegatingLoader.__init__(self, resolver);


    def load(self, resource, resourceType = None):
        """Loads a resource.

        @param: mixed  resource A resource
        @param string resourceType     The resource type

        @return RouteCollection A RouteCollection instance

        """

        collection = BaseDelegatingLoader.load(self, resource, resourceType);

        for route in collection.all().values():
            controller = route.getDefault('_controller');
            if (controller) :
                try:
                    controller = self._parser.parse(controller);
                except Exception:
                    # unable to optimize unknown notation
                    pass;

                route.setDefault('_controller', controller);

        return collection;

