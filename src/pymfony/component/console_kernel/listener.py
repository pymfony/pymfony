# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;


from pymfony.component.system import clone
from pymfony.component.event_dispatcher import EventSubscriberInterface
from pymfony.component.console import Request
from pymfony.component.console.output import OutputInterface
from pymfony.component.console_kernel import ConsoleKernelEvents
from pymfony.component.console_kernel.event import GetResponseEvent
from pymfony.component.console_kernel.event import FilterResponseEvent
from pymfony.component.console_kernel.exception import NotFoundConsoleException
from pymfony.component.console_kernel.event import GetResponseForExceptionEvent
from pymfony.component.console_kernel.interface import ConsoleKernelInterface
from pymfony.component.console_routing.matcher import RequestMatcherInterface
from pymfony.component.console_routing.exception import ResourceNotFoundException

"""
"""

class RouterListener(EventSubscriberInterface):
    """Initializes the context from the request and sets request attributes based on a matching route.
 *
 * @author Fabien Potencier <fabien@symfony.com>

    """

    def __init__(self, matcher):
        """Constructor.
     *
     * @param ContainerInterface

        """
        assert isinstance(matcher, RequestMatcherInterface);

        self.__matcher = matcher;

    def onKernelRequest(self, event):
        assert isinstance(event, GetResponseEvent);

        request = event.getRequest();
        assert isinstance(request, Request);

        if (request.attributes.has('_controller')) :
            # routing is already done
            return;

        # add attributes based on the request (routing)
        try:
            parameters = self.__matcher.matchRequest(request);

            request.attributes.add(parameters);
            parameters.pop('_route', None);
            parameters.pop('_controller', None);
            request.attributes.set('_route_params', parameters);
        except ResourceNotFoundException as e:
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
    __handling = False;

    def __init__(self, controller):
        self.__controller = controller;


    def onKernelException(self, event):
        assert isinstance(event, GetResponseForExceptionEvent);

        if self.__handling is True:
            return False;

        self.__handling = True;

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
            # set handling to false otherwise it wont be able to handle further more
            self.__handling = False;

            # re-throw the exception from within ConsoleKernel as this is a catch-all
            return;

        event.setResponse(response);

        self.__handling = False;

    @classmethod
    def getSubscribedEvents(cls):
        return {
            ConsoleKernelEvents.EXCEPTION: ['onKernelException', -128],
        };
