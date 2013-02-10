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

from pymfony.component.dispatcher import Event;
from pymfony.component.console import Request
from pymfony.component.clikernel.interface import CliKernelInterface
from pymfony.component.system.exception import LogicException
from pymfony.component.system import Tool
from pymfony.component.console import Response

class CliKernelEvent(Event):
    """Base class for events thrown in the CliKernel component):
 *
 * @author Bernhard Schussek <bschussek@gmail.com>
 *
 * @api

    """


    def __init__(self, kernel, request, requestType):
        assert isinstance(request, Request);
        assert isinstance(kernel, CliKernelInterface);

        Event.__init__(self);

        # The kernel in which this event was thrown
        # @var CliKernelInterface
        self.__kernel = None;

        # The request the kernel is currently processing
        # @var Request
        self.__request = None;

        # The request type the kernel is currently processing.  One of
        # HttpKernelInterface.MASTER_REQUEST and HttpKernelInterface.SUB_REQUEST
        # @var integer
        self.__requestType = None;

        self.__kernel = kernel;
        self.__request = request;
        self.__requestType = requestType;


    def getKernel(self):
        """Returns the kernel in which this event was thrown
     *
     * @return CliKernelInterface
     *
     * @api

        """

        return self.__kernel;


    def getRequest(self):
        """Returns the request the kernel is currently processing
     *
     * @return Request
     *
     * @api

        """

        return self.__request;


    def getRequestType(self):
        """Returns the request type the kernel is currently processing
     *
     * @return integer  One of CliKernelInterface.MASTER_REQUEST and
     *                  CliKernelInterface.SUB_REQUEST
     *
     * @api

        """

        return self.__requestType;


class FilterControllerEvent(CliKernelEvent):
    """Allows filtering of a controller callable
 *
 * You can call getController() to retrieve the current controller. With
 * setController() you can set a new controller that is used in the processing
 * of the request.
 *
 * Controllers should be callables.
 *
 * @author Bernhard Schussek <bschussek@gmail.com>
 *
 * @api

    """



    def __init__(self, kernel, controller, request, requestType):
        assert isinstance(request, Request);
        assert isinstance(kernel, CliKernelInterface);

        CliKernelEvent.__init__(self, kernel, request, requestType);

        # The current controller
        # @var callable
        self.__controller = None;
    
        self.setController(controller);


    def getController(self):
        """Returns the current controller
     *
     * @return callable
     *
     * @api

        """

        return self.__controller;


    def setController(self, controller):
        """Sets a new controller
     *
     * @param callable controller
     *
     * @raise LogicException
     *
     * @api

        """

        # controller must be a callable
        if ( not Tool.isCallable(controller)) :
            raise LogicException(
                'The controller must be a callable ({0} given).'.format(
                    repr(controller)
            ));


        self.__controller = controller;





class FilterResponseEvent(CliKernelEvent):
    """Allows to filter a Response object
 *
 * You can call getResponse() to retrieve the current response. With
 * setResponse() you can set a new response that will be returned to the
 * browser.
 *
 * @author Bernhard Schussek <bschussek@gmail.com>
 *
 * @api

    """

    def __init__(self, kernel, request, requestType, response):
        assert isinstance(response, Response);
        assert isinstance(request, Request);
        assert isinstance(kernel, CliKernelInterface);

        CliKernelEvent.__init__(self, kernel, request, requestType);

        # he current response object
        # @var Response
        self.__response = None;


        self.setResponse(response);


    def getResponse(self):
        """Returns the current response object
     *
     * @return Response
     *
     * @api

        """

        return self.__response;


    def setResponse(self, response):
        """Sets a new response object
     *
     * @param Response response
     *
     * @api

        """
        assert isinstance(response, Response);

        self.__response = response;



class GetResponseEvent(CliKernelEvent):
    """Allows to create a response for a request
 *
 * Call setResponse() to set the response that will be returned for the
 * current request. The propagation of this event is stopped as soon as a
 * response is set.
 *
 * @author Bernhard Schussek <bschussek@gmail.com>
 *
 * @api

    """

    def __init__(self, kernel, request, requestType):
        CliKernelEvent.__init__(self, kernel, request, requestType);

        # he response object
        # @var Response
        self.__response = None;

    def getResponse(self):
        """Returns the response object
     *
     * @return Response
     *
     * @api

        """

        return self.__response;


    def setResponse(self, response):
        """Sets a response and stops event propagation
     *
     * @param Response response
     *
     * @api

        """
        assert isinstance(response, Response);

        self.__response = response;

        self.stopPropagation();


    def hasResponse(self):
        """Returns whether a response was set
     *
     * @return Boolean Whether a response was set
     *
     * @api

        """

        return None is not self.__response;


class GetResponseForControllerResultEvent(GetResponseEvent):
    """Allows to create a response for the return value of a controller
 *
 * Call setResponse() to set the response that will be returned for the
 * current request. The propagation of this event is stopped as soon as a
 * response is set.
 *
 * @author Bernhard Schussek <bschussek@gmail.com>
 *
 * @api

    """


    def __init__(self, kernel, request, requestType, controllerResult):
        assert isinstance(request, Request);
        assert isinstance(kernel, CliKernelInterface);

        GetResponseEvent.__init__(self, kernel, request, requestType);

        # The return value of the controller
        # @var mixed
        self.__controllerResult = None;

        self.__controllerResult = controllerResult;


    def getControllerResult(self):
        """Returns the return value of the controller.
     *
     * @return mixed The controller return value
     *
     * @api

        """

        return self.__controllerResult;


    def setControllerResult(self, controllerResult):
        """Assigns the return value of the controller.
     *
     * @param mixed The controller return value
     *
     * @api

        """
        assert isinstance(controllerResult, dict);

        self.__controllerResult = controllerResult;



class GetResponseForExceptionEvent(GetResponseEvent):
    """Allows to create a response for a thrown exception
 *
 * Call setResponse() to set the response that will be returned for the
 * current request. The propagation of this event is stopped as soon as a
 * response is set.
 *
 * You can also call setException() to replace the thrown exception. This
 * exception will be thrown if no response is set during processing of this:
 * event.
 *
 * @author Bernhard Schussek <bschussek@gmail.com>
 *
 * @api

    """



    def __init__(self, kernel, request, requestType, e):
        assert isinstance(e, Exception);
        assert isinstance(request, Request);
        assert isinstance(kernel, CliKernelInterface);

        GetResponseEvent.__init__(self, kernel, request, requestType);

        # The exception object
        # @var Exception
        self.__exception = None;

        self.setException(e);


    def getException(self):
        """Returns the thrown exception
     *
     * @return Exception  The thrown exception
     *
     * @api

        """

        return self.__exception;


    def setException(self, exception):
        """Replaces the thrown exception
     *
     * This exception will be thrown if no response is set in the event.:
     *
     * @param Exception exception The thrown exception
     *
     * @api

        """
        assert isinstance(exception, Exception);

        self.__exception = exception;



class PostResponseEvent(Event):
    """Allows to execute logic after a response was sent
 *
 * @author Jordi Boggiano <j.boggiano@seld.be>

    """


    def __init__(self, kernel, request, response):
        assert isinstance(response, Response);
        assert isinstance(request, Request);
        assert isinstance(kernel, CliKernelInterface);

        #The kernel in which this event was thrown
        # @var CliKernelInterface
        self.__kernel = None;


        self.__request = None;

        self.__response = None;

        self.__kernel = kernel;
        self.__request = request;
        self.__response = response;


    def getKernel(self):
        """Returns the kernel in which this event was thrown.
     *
     * @return HttpKernelInterface

        """

        return self.__kernel;


    def getRequest(self):
        """Returns the request for which this event was thrown.
     *
     * @return Request

        """

        return self.__request;


    def getResponse(self):
        """Returns the response for which this event was thrown.
     *
     * @return Response

        """

        return self.__response;


