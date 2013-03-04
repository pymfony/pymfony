# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

from pymfony.component.system import Object;
from pymfony.component.system.oop import interface;

"""
"""

@interface
class TraceableEventDispatcherInterface(Object):
    def getCalledListeners(self):
        """Gets the called listeners.

        @return: dict An dict of called listeners
        """
        pass;

    def getNotCalledListeners(self):
        """Gets the not called listeners.

        @return: dict An dict of not called listeners
        """
        pass;
