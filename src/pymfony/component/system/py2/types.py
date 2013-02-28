# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import sys;

from pymfony.component.system import Object;

if sys.version_info < (2, 7):
    from pymfony.component.system.py2.minor6.types import AbstractOrderedDict;
else:
    from collections import OrderedDict as AbstractOrderedDict;

"""
"""

__all__ = [
    'AbstractString',
    'AbstractOrderedDict',
];

class AbstractString(str, Object):
    @classmethod
    def __subclasshook__(cls, subclass):
        if issubclass(subclass, basestring):
            return True;
        return NotImplemented;
