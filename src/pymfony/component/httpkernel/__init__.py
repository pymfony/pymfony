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
from pymfony.component.system import final;

@final
class HttpKernelEvents(Object):
    # The REQUEST event occurs at the very beginning of request dispatching
    #
    # This event allows you to create a response for a request before any
    # other code in the framework is executed. The event listener method
    # receives a pymfony.component.httpkernel.event.GetResponseEvent instance.
    REQUEST = 'http_kernel.request';

    # The EXCEPTION event occurs when an uncaught exception appears
    #
    # This event allows you to create a response for a thrown exception or
    # to modify the thrown exception. The event listener method receives
    # a pymfony.component.httpkernel.event.GetResponseForExceptionEvent instance.
    EXCEPTION = 'http_kernel.exception';

    # The VIEW event occurs when the return value of a controller
    # is not a Response instance.
    #
    # This event allows you to create a response for the return value of the
    # controller. The event listener method receives a
    # pymfony.component.httpkernel.event.GetResponseForControllerResultEvent
    # instance.
    VIEW = 'http_kernel.view';

    # The CONTROLLER event occurs once a controller was found for
    # handling a request
    #
    # This event allows you to change the controller that will handle the
    # request. The event listener method receives a
    # pymfony.component.httpkernel.event.FilterControllerEvent instance.
    CONTROLLER = 'http_kernel.controller';

    # The RESPONSE event occurs once a response was created for
    # replying to a request
    #
    # This event allows you to modify or replace the response that will be
    # replied. The event listener method receives a
    # pymfony.component.httpkernel.event.FilterResponseEvent instance.
    RESPONSE = 'http_kernel.response';

    # The TERMINATE event occurs once a response was sent
    #
    # This event allows you to run expensive post-response jobs.
    # The event listener method receives a
    # pymfony.component.httpkernel.event.PostResponseEvent instance.
    TERMINATE = 'http_kernel.terminate';

