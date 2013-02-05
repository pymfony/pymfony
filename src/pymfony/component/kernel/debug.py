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

import sys;

from pymfony.component.system import Object;

class ExceptionHandler(Object):
    def __init__(self, debug=True):
        self.__debug = debug;
        self._original_hook = sys.excepthook

    @classmethod
    def register(cls, debug=True):
        """Register the exception handler.

        @param debug: Boolean

        @return: ExceptionHandler The registered exception handler
        """
        handler = cls(debug);
        if sys.excepthook == sys.__excepthook__:
            # if someone already patched excepthook, let them win
            sys.excepthook = handler.handle;
        return handler;

    def handle(self, excType, excInstance, trace):
        # log this exception
        # Sends a Response for the given Exception.
        if self.__debug:
            self._original_hook(excType, excInstance, trace);
