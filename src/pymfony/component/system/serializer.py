# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pickle import dumps;
from pickle import loads;

try:
    from base64 import encodebytes;
    from base64 import decodebytes;
except Exception:
    from base64 import encodestring as encodebytes;
    from base64 import decodestring as decodebytes;

"""
"""

CHARSET = 'UTF-8';

def serialize(obj):
    return encodebytes(dumps(obj)).decode(CHARSET).replace('\n', '');

def unserialize(s):
    return loads(decodebytes(s.encode(CHARSET)));
