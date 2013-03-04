# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from collections import OrderedDict as AbstractOrderedDict;

from pymfony.component.system import Object;

"""
"""

__all__ = [
    'AbstractString',
    'AbstractOrderedDict',
];

class AbstractString(str, Object):
    @classmethod
    def __subclasshook__(cls, subclass):
        if issubclass(subclass, str):
            return True;
        return NotImplemented;
