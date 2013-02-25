# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;


from pymfony.component.console_kernel import ConsoleKernelEvents
from pymfony.component.event_dispatcher import EventSubscriberInterface
from pymfony.component.dependency import ContainerInterface
from pymfony.component.console_kernel.event import GetResponseEvent
from pymfony.component.console import Response
from pymfony.component.console.output import OutputInterface
from pymfony.component.console import Request
from pymfony.component.console_kernel.event import FilterResponseEvent
from pymfony.component.console_kernel.routing import RequestMatcherInterface
from pymfony.component.console_kernel.exception import NotFoundConsoleException
from pymfony.component.console_kernel.event import GetResponseForExceptionEvent
from pymfony.component.console_kernel.interface import ConsoleKernelInterface
from pymfony.component.system import clone

"""
"""

class RouterListener(EventSubscriberInterface):
    """Initializes the context from the request and sets request attributes based on a matching route.
 *
 * @author Fabien Potencier <fabien@symfony.com>

    """

    def __init__(self, container, matcher):
        """Constructor.
     *
     * @param ContainerInterface

        """
        assert isinstance(container, ContainerInterface);
        assert isinstance(matcher, RequestMatcherInterface);

        self.__container = container;
        self.__matcher = matcher;

    def onKernelRequest(self, event):
        assert isinstance(event, GetResponseEvent);

        request = event.getRequest();
        assert isinstance(request, Request);

        if (request.attributes.has('_controller')) :
            # routing is already done
            return;

        cmdName = request.getFirstArgument();

        if request.hasParameterOption(['--help', '-h']):
            if not cmdName:
                cmdName = 'help';
            else:
                request.attributes.set('_want_help', True);

        if request.hasParameterOption(['--no-interaction', '-n']):
            request.attributes.set('_interaction', False);

        if request.hasParameterOption(['--version', '-V']):
            event.setResponse(Response(self.__container.get('console_kernel').getLongVersion()));
            return;

        if not cmdName:
            cmdName = self.__container.get('console.router')\
                .getRouteCollection()\
                .get(self.__container.getParameter('console.router.default_route'))\
                .getPath()\
            ;

        request.setCommandName(cmdName);

        # add attributes based on the request (routing)
        try:
            parameters = self.__matcher.matchRequest(request);

            request.attributes.add(parameters);
            parameters.pop('_route', None);
            parameters.pop('_controller', None);
            request.attributes.set('_route_params', parameters);
        except NotFoundConsoleException as e:
            message = 'No route found for "{0}"'.format(
                " ".join(request.getArgv()[1:])
            );

            raise NotFoundConsoleException(message, e);

    @classmethod
    def getSubscribedEvents(self):

        return {
            ConsoleKernelEvents.REQUEST: [['onKernelRequest', 32]],
        };


class ResponseListener(EventSubscriberInterface):
    """ResponseListener fixes the Response headers based on the Request.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    def onKernelResponse(self, event):
        """Filters the Response.

        @param: FilterResponseEvent event A FilterResponseEvent instance

        """
        assert isinstance(event, FilterResponseEvent);

        response = event.getResponse();
        request = event.getRequest();

        if request.hasParameterOption(['--ansi']):
            response.setDecorated(True);
        elif request.hasParameterOption(['--no-ansi']):
            response.setDecorated(False);

        if request.hasParameterOption(['--quiet', '-q']):
            response.setVerbosity(OutputInterface.VERBOSITY_QUIET);
        elif request.hasParameterOption(['--verbose', '-v']):
            response.setVerbosity(OutputInterface.VERBOSITY_VERBOSE);


    @classmethod
    def getSubscribedEvents(cls):
        return {
            ConsoleKernelEvents.RESPONSE: 'onKernelResponse',
        };


class ExceptionListener(EventSubscriberInterface):
    def __init__(self, controller):
        self.__controller = controller;


    def onKernelException(self, event):
        assert isinstance(event, GetResponseForExceptionEvent);

        exception = event.getException();
        request = event.getRequest();

        attributes = {
            '_controller': self.__controller,
            'exception': exception,
        };

        request = clone(request);
        request.attributes.replace(attributes);

        try:
            response = event.getKernel().handle(request, ConsoleKernelInterface.SUB_REQUEST, True);
        except Exception:
            return;

        event.setResponse(response);


    @classmethod
    def getSubscribedEvents(cls):
        return {
            ConsoleKernelEvents.EXCEPTION: ['onKernelException', -128],
        };