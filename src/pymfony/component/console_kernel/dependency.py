# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.console import Request;
from pymfony.component.console import Response;
from pymfony.component.console_kernel import ConsoleKernel;
from pymfony.component.console_kernel.controller import ControllerResolverInterface;
from pymfony.component.console_kernel.interface import ConsoleKernelInterface;

from pymfony.component.dependency.interface import ContainerInterface;

from pymfony.component.event_dispatcher import EventDispatcherInterface;

"""
"""

class ContainerAwareConsoleKernel(ConsoleKernel):
    """This ConsoleKernel is used to manage scope changes of the DI container.

    @author: Fabien Potencier <fabien@symfony.com>
    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """


    def __init__(self, dispatcher, container, controllerResolver):
        """Constructor.

        @param: EventDispatcherInterface    dispatcher         An EventDispatcherInterface instance
        @param ContainerInterface          container          A ContainerInterface instance
        @param ControllerResolverInterface controllerResolver A ControllerResolverInterface instance

        """
        assert isinstance(controllerResolver, ControllerResolverInterface);
        assert isinstance(container, ContainerInterface);
        assert isinstance(dispatcher, EventDispatcherInterface);

        ConsoleKernel.__init__(self, dispatcher, controllerResolver);

        self._container = container;


    def handle(self, request, response = None, requestType = ConsoleKernelInterface.MASTER_REQUEST, catch = True):
        assert isinstance(request, Request);

        if None is response :
            response = Response();

        assert isinstance(response, Response);

        if not self._container.isScopeActive('request'):
            self._container.enterScope('request');
            self._container.set('request', request, 'request');
            self._container.set('response', response, 'request');

        try:
            response = ConsoleKernel.handle(self, request, response, requestType, catch);
        finally:
            if self._container.isScopeActive('request'):
                self._container.leaveScope('request');

        return response;
