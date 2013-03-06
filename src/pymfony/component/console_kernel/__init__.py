# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.system import Object;
from pymfony.component.system.oop import final;
from pymfony.component.system.exception import LogicException;

from pymfony.component.event_dispatcher import EventDispatcherInterface;

from pymfony.component.console import Response;
from pymfony.component.console import Request;

from pymfony.component.console_kernel.exception import ConsoleExceptionInterface;
from pymfony.component.console_kernel.exception import NotFoundConsoleException;
from pymfony.component.console_kernel.controller import ControllerResolverInterface;
from pymfony.component.console_kernel.event import PostResponseEvent;
from pymfony.component.console_kernel.event import GetResponseEvent;
from pymfony.component.console_kernel.event import FilterControllerEvent;
from pymfony.component.console_kernel.event import GetResponseForControllerResultEvent;
from pymfony.component.console_kernel.event import FilterResponseEvent;
from pymfony.component.console_kernel.event import GetResponseForExceptionEvent;
from pymfony.component.console_kernel.interface import ConsoleTerminableInterface;
from pymfony.component.console_kernel.interface import ConsoleKernelInterface;

"""
"""

@final
class ConsoleKernelEvents(Object):
    # The REQUEST event occurs at the very beginning of request dispatching
    #
    # This event allows you to create a response for a request before any
    # other code in the framework is executed. The event listener method
    # receives a pymfony.component.console_kernel.event.GetResponseEvent instance.
    REQUEST = 'console_kernel.request';

    # The EXCEPTION event occurs when an uncaught exception appears
    #
    # This event allows you to create a response for a raise exception or
    # to modify the raise exception. The event listener method receives
    # a pymfony.component.console_kernel.event.GetResponseForExceptionEvent instance.
    EXCEPTION = 'console_kernel.exception';

    # The CONTROLLER event occurs once a controller was found for
    # handling a output
    #
    # This event allows you to change the controller that will handle the
    # response. The event listener method receives a
    # pymfony.component.console_kernel.event.FilterControllerEvent instance.
    CONTROLLER = 'console_kernel.controller';

    # The VIEW event occurs when the return value of a controller
    # is not a Response instance.
    #
    # This event allows you to create a response for the return value of the
    # controller. The event listener method receives a
    # pymfony.component.console_kernel.event.GetResponseForControllerResultEvent
    # instance.
    VIEW = 'console_kernel.view';

    # The RESPONSE event occurs once a response was created for
    # replying to a response
    #
    # This event allows you to modify or replace the response that will be
    # replied. The event listener method receives a
    # pymfony.component.console_kernel.event.FilterResponseEvent instance.
    RESPONSE = 'console_kernel.response';

    # The TERMINATE event occurs once a response was sent
    #
    # This event allows you to run expensive post-response jobs.
    # The event listener method receives a
    # pymfony.component.console_kernel.event.PostResponseEvent instance.
    TERMINATE = 'console_kernel.terminate';



class ConsoleKernel(ConsoleKernelInterface, ConsoleTerminableInterface):
    """ConsoleKernel notifies events to convert a Request object to a Response one.:

    @author Fabien Potencier <fabien@symfony.com>

    @api

    """

    def __init__(self, dispatcher, resolver, name = 'UNKNOWN', version = 'UNKNOWN'):
        """Constructor

        @param EventDispatcherInterface    dispatcher An EventDispatcherInterface instance
        @param ControllerResolverInterface resolver   A ControllerResolverInterface instance

        @api

        """
        assert isinstance(resolver, ControllerResolverInterface);
        assert isinstance(dispatcher, EventDispatcherInterface);

        self._dispatcher = None;
        self._resolver = None;
        self.__name = None;
        self.__version = None;
        self.__definition = None;

        self._dispatcher = dispatcher;
        self._resolver = resolver;
        self.__name = name;
        self.__version = version;

    def handle(self, request, requestType = ConsoleKernelInterface.MASTER_REQUEST, catch = True):
        """Handles a Request to convert it to a Response.

        When catch is True, the implementation must catch all exceptions
        and do its best to convert them to a Response instance.

        @param Request request   A Request instance
        @param integer   type      The type of the request
                                   (one of ConsoleKernelInterface.MASTER_REQUEST
                                  or ConsoleKernelInterface.SUB_REQUEST)
        @param Boolean   catch     Whether to catch exceptions or not

        @return Response A Response instance

        @raise Exception When an Exception occurs during processing

        @api

        """
        assert isinstance(request, Request);

        try:
            return self.__handleRaw(request, requestType);
        except Exception as e:
            if (False is catch) :
                raise e;


            return self.__handleException(e, request, requestType);



    def terminate(self, request, response):
        """@inheritdoc

        @api

        """
        assert isinstance(response, Response);
        assert isinstance(request, Request);

        self._dispatcher.dispatch(
            ConsoleKernelEvents.TERMINATE,
            PostResponseEvent(self, request, response)
        );

    def getName(self):
        """Gets the name of the application.

        @return: string The application name

        @api

        """

        return self.__name;


    def setName(self, name):
        """Sets the application name.

        @param: string name The application name

        @api

        """

        self.__name = name;


    def getVersion(self):
        """Gets the application version.

        @return: string The application version

        @api

        """

        return self.__version;


    def setVersion(self, version):
        """Sets the application version.

        @param: string version The application version

        @api

        """

        self.__version = version;


    def getLongVersion(self):
        """Returns the long version of the application.

        @return: string The long application version

        @api

        """

        if ('UNKNOWN' != self.getName() and 'UNKNOWN' != self.getVersion()) :
            return '<info>{0}</info> version <comment>{1}</comment>'.format(
                self.getName(), self.getVersion()
            );

        return '<info>Console Tool</info>';


    def __handleRaw(self, request, requestType = ConsoleKernelInterface.MASTER_REQUEST):
        """Handles a request to convert it to a response.

        Exceptions are not caught.

        @param Request request A Request instance
        @param integer type    The type of the request (one of ConsoleKernelInterface.MASTER_REQUEST or ConsoleKernelInterface.SUB_REQUEST)

        @return Response A Response instance

        @raise LogicException If one of the listener does not behave as expected
        @raise NotFoundConsoleException When controller cannot be found

        """
        assert isinstance(request, Request);

        # request
        event = GetResponseEvent(self, request, requestType);
        self._dispatcher.dispatch(ConsoleKernelEvents.REQUEST, event);

        if (event.hasResponse()) :
            return self.__filterResponse(event.getResponse(), request, requestType);


        # load controller
        controller = self._resolver.getController(request);
        if (False is controller) :
            raise NotFoundConsoleException(
                'Unable to find the controller for path "{0}". Maybe you '
                'forgot to add the matching route in your routing '
                'configuration?'.format(" ".join(request.getArgv()[1:]))
            );


        event = FilterControllerEvent(self, controller, request, requestType);
        self._dispatcher.dispatch(ConsoleKernelEvents.CONTROLLER, event);
        controller = event.getController();

        # controller arguments
        arguments = self._resolver.getArguments(request, controller);

        # call controller
        response = controller(*arguments);

        # view
        if ( not isinstance(response, Response)) :
            event = GetResponseForControllerResultEvent(self, request, requestType, response);
            self._dispatcher.dispatch(ConsoleKernelEvents.VIEW, event);

            if (event.hasResponse()) :
                response = event.getResponse();


            if ( not isinstance(response, Response)) :
                msg = 'The controller must return a response ({0} given).'
                ''.format(repr(response));

                # the user may have forgotten to return something
                if (None is response) :
                    msg += ' Did you forget to add a return statement '
                    'somewhere in your controller?';

                raise LogicException(msg);



        return self.__filterResponse(response, request, requestType);


    def __filterResponse(self, response, request, requestType):
        """Filters a response object.

        @param Response   response   A Response instance
        @param Request  request  A error message in case the response is
                                    not a Response object
        @param integer    requestType  The type of the input (one of
                                    ConsoleKernelInterface.MASTER_REQUEST or
                                    ConsoleKernelInterface.SUB_REQUEST)

        @return Response The filtered Response instance

        @raise RuntimeException if the passed object is not a Response instance:

        """
        assert isinstance(request, Request);
        assert isinstance(response, Response);

        event = FilterResponseEvent(self, request, requestType, response);

        self._dispatcher.dispatch(ConsoleKernelEvents.RESPONSE, event);

        return event.getResponse();


    def __handleException(self, e, request, requestType):
        """Handles an exception by trying to convert it to a Response.

        @param Exception  e          An Exception instance
        @param Request    request  A Request instance
        @param integer    requestType  The type of the request

        @return Response A Response instance

        @raise Exception

        """
        assert isinstance(e, Exception);

        event = GetResponseForExceptionEvent(self, request, requestType, e);
        self._dispatcher.dispatch(ConsoleKernelEvents.EXCEPTION, event);

        # a listener might have replaced the exception
        e = event.getException();

        if ( not event.hasResponse()) :
            raise e;

        response = event.getResponse();

        if (isinstance(e, ConsoleExceptionInterface)) :
            # keep the CLI status code
            response.setStatusCode(e.getStatusCode());
        else:
            response.setStatusCode(1);

        try:
            return self.__filterResponse(response, request, requestType);
        except Exception as e:
            return response;
