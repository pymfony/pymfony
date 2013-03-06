# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.kernel.bundle import Bundle;

from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency import Scope;
from pymfony.component.dependency.compiler import PassConfig;

from pymfony.bundle.framework_bundle.dependency.compiler import RegisterKernelListenersPass;
from pymfony.bundle.framework_bundle.dependency.compiler import ConsoleRoutingResolverPass;

from pymfony.component.console_routing import RouteCollection;
from pymfony.component.console_routing import Route;

"""
Pymfony FrameworkBundle
"""

class FrameworkBundle(Bundle):
    """Bundle.

    @author: Fabien Potencier <fabien@symfony.com>
    """
    def boot(self):
        if self._container.has('console.router'):
            routeCollection = self._container.get('console.router').getRouteCollection();
            assert isinstance(routeCollection, RouteCollection);

            routeCollection.add('framework_list', Route("list", "Lists commands", {
                '_controller': "FrameworkBundle:List:show",
            }));

    def build(self, container):
        assert isinstance(container, ContainerBuilder);

        Bundle.build(self, container);

        container.addScope(Scope('request'));

        container.addCompilerPass(ConsoleRoutingResolverPass());
        container.addCompilerPass(RegisterKernelListenersPass(), PassConfig.TYPE_AFTER_REMOVING);
