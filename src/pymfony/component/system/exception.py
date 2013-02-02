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

class SystemException(Exception, Object):
    pass;

class LogicException(SystemException):
    pass;

class InvalidArgumentException(LogicException):
    pass;

class BadMethodCallException(LogicException):
    pass;

class OutOfBoundsException(LogicException):
    pass;

class RuntimeException(SystemException):
    pass;
