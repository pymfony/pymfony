# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from json import JSONDecoder;

from pymfony.component.system.types import OrderedDict;

"""
"""

__all__ = [
    'AbstractJSONDecoderOrderedDict',
];

class AbstractJSONDecoderOrderedDict(JSONDecoder):
    def __init__(self, parse_float=None, parse_int=None, parse_constant=None,
                       strict=True):
        JSONDecoder.__init__(self, object_hook=None, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, strict=strict, object_pairs_hook=self.__object_pairs_hook);

    def __object_pairs_hook(self, seq):
        return OrderedDict(seq);
