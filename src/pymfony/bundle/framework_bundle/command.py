# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

from pymfony.component.console import Response
from pymfony.component.dependency import ContainerAware
from pymfony.component.console_kernel.routing import Router
from pymfony.component.console_kernel.routing import Route

"""
"""

class ListCommand(ContainerAware):
    def showAction(self):
        router = self._container.get('console.router');
        assert isinstance(router, Router);
        commandList = list();
        for name, route in router.getRouteCollection().all().items():
            assert isinstance(route, Route);

            if name == '_default':
                continue;

            commandList.append(
                "<info>{0}</info>: <comment>{1}</comment>".format(
                route.getPath(),
                route.getDescription(),
            ));

        return Response("Command List:\n- "+"\n- ".join(commandList));
