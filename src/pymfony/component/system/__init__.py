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
if sys.version_info[0] == 2:
    from pymfony.component.system.py2 import *;
else:
    from pymfony.component.system.py3 import *;

__all__ = [
    'abstract',
    'interface',
    'Object',
];


@interface
class SerializableInterface(Object):
    def serialize(self):
        pass;

    def unserialize(self, serialized):
        pass;
