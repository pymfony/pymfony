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

from pymfony.component.system import Object;
from pymfony.component.system.oop import interface;

from pymfony.component.console import Response;
from pymfony.component.console import Request;

@interface
class ConsoleTerminableInterface(Object):
    """Terminable extends the Kernel request/response cycle with dispatching a post
 * response event after sending the response and before shutting down the kernel.
 *
 * @author Jordi Boggiano <j.boggiano@seld.be>
 * @author Pierre Minnieur <pierre.minnieur@sensiolabs.de>
 *
 * @api

    """

    def terminate(self, request, response):
        """Terminates a request/response cycle.
     *
     * Should be called after sending the response and before shutting down the kernel.
     *
     * @param Request   request     A Request instance
     * @param Response  response    A Response instance
     *
     * @api

        """
        assert isinstance(response, Response);
        assert isinstance(request, Request);

@interface
class ConsoleKernelInterface(Object):
    """ConsoleKernelInterface handles a Request to convert it to a Response.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """

    MASTER_REQUEST = 1;
    SUB_REQUEST = 2;

    def handle(self, request, requestType = MASTER_REQUEST, catch = True):
        """Handles a Request to convert it to a Response.
     *
     * When catch is True, the implementation must catch all exceptions
     * and do its best to convert them to a Response instance.
     *
     * @param Request   request   A Request instance
     * @param integer   type      The type of the request
     *                            (one of ConsoleKernelInterface.MASTER_REQUEST
                                  or ConsoleKernelInterface.SUB_REQUEST)
     * @param Boolean   catch     Whether to catch exceptions or not
     *
     * @return Response A Response instance
     *
     * @raise Exception When an Exception occurs during processing
     *
     * @api

        """
        assert isinstance(request, Request);
