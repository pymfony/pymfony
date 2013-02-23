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
from pymfony.bundle.framework_bundle.dependency.compiler import RegisterKernelListenersPass;
from pymfony.component.dependency.compiler import PassConfig;
from pymfony.component.dependency import Scope
from pymfony.bundle.framework_bundle.dependency.compiler import ConsoleRoutingResolverPass
from pymfony.component.console_kernel.routing import Route
from pymfony.component.console_kernel.routing import RouteCollection

"""
"""

class FrameworkBundle(Bundle):
    """Bundle.

    @author: Fabien Potencier <fabien@symfony.com>

    """
    def build(self, container):
        assert isinstance(container, ContainerBuilder);

        Bundle.build(self, container);

        container.addScope(Scope('request'));

        container.addCompilerPass(ConsoleRoutingResolverPass());
        container.addCompilerPass(RegisterKernelListenersPass(), PassConfig.TYPE_AFTER_REMOVING);

    def boot(self):

        routeCollection = self._container.get('console.router').getRouteCollection();
        assert isinstance(routeCollection, RouteCollection);

        routeCollection.add('_list', Route("list", "Lists commands", {
            '_controller': "FrameworkBundle:List:show",
        }));
        routeCollection.add('_default', Route("list", "Lists commands", {
            '_controller': "FrameworkBundle:List:show",
        }));
