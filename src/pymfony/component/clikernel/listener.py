# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""
"""

from __future__ import absolute_import;


from pymfony.component.clikernel import CliKernelEvents
from pymfony.component.dispatcher import EventSubscriberInterface
from pymfony.component.dependency import ContainerInterface
from pymfony.component.clikernel.event import GetResponseEvent
from pymfony.component.clikernel.exception import NotFoundCliException

class RouterListener(EventSubscriberInterface):
    """Initializes the context from the request and sets request attributes based on a matching route.
 *
 * @author Fabien Potencier <fabien@symfony.com>

    """

    def __init__(self, container):
        """Constructor.
     *
     * @param ContainerInterface

        """
        assert isinstance(container, ContainerInterface);

        self.__container = container;

    def onKernelRequest(self, event):
        assert isinstance(event, GetResponseEvent);

        request = event.getRequest();

        if (request.attributes.has('_controller')) :
            # routing is already done
            return;


        # add attributes based on the request (routing)
        commands = self.__container.getParameter('console.commands');
        if request.getCommand() not in commands:
            raise NotFoundCliException();

        controllerInfos = commands[request.getCommand()];
        controller = self.__stripController(controllerInfos['_controller']);
        request.attributes.set('_controller', controller);


    def __stripController(self, controller):
        """
        @param: dict controllerInfos
        """
        controller = str(controller);

        '@SomeBundle:controllerName:actionName'
        if not controller.startswith('@'):
            raise NotFoundCliException();

        bundleName, controllerName, actionName = controller[1:].split(':', 3);

        bundle = self.__container.get('kernel').getBundle(bundleName);
        bundleNamespace = bundle.getNamespace();
        className = ( bundleNamespace + '.controller.' +
            controllerName + 'Controller'
        );
        methodName = actionName + 'Action';

        return className + "::" + methodName;


    @classmethod
    def getSubscribedEvents(self):

        return {
            CliKernelEvents.REQUEST: [['onKernelRequest', 32]],
        };

