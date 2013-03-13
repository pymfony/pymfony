# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.system import Object;
from pymfony.component.system.serialiser import serialize;
from pymfony.component.system.serialiser import unserialize;

"""
"""

class SerialiserTest(unittest.TestCase):
    def test(self):
        value = B();
        ret = unserialize(serialize(value));

        self.assertTrue(isinstance(ret, value.__class__));
        self.assertTrue(isinstance(ret, Object));
        self.assertEqual(ret.__dict__, value.__dict__);


class B(Object):

    def __init__(self):
        self.b = 'foo';
        self.text = """
osuboqsosy soyo ve yo s yoo rfvq
sqvdo vyo yoyotyod ydonbo yon dvyo
""";
        self.list = [1, '', (1,1), {}, []];
        self.dict = {1:1, 2:'', 3:(1,1), 4:{}, 5:[]};

if __name__ == '__main__':
    unittest.main()
