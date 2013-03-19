# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;
import tempfile;
import os;
from time import time;
from random import randint as rand;

from pymfony.component.config.resource import FileResource;

"""
"""


class FileResourceTest(unittest.TestCase):

    def setUp(self):

        self._file = tempfile.gettempdir()+'/tmp.xml';
        if not os.path.exists(self._file):
            open(self._file, 'a').close();
        os.utime(self._file, None);
        self._resource = FileResource(self._file);


    def tearDown(self):

        os.unlink(self._file);


    def testGetResource(self):
        """
        @covers Symfony\Component\Config\Resource\FileResource.getResource

        """

        self.assertEqual(os.path.realpath(self._file), self._resource.getResource(), '->getResource() returns the path to the resource');


    def testIsFresh(self):
        """
        @covers Symfony\Component\Config\Resource\FileResource.isFresh

        """

        self.assertTrue(self._resource.isFresh(time() + 10), '->isFresh() returns True if the resource has not changed');
        self.assertFalse(self._resource.isFresh(time() - 86400), '->isFresh() returns False if the resource has been updated');

        resource = FileResource('/____foo/foobar'+str(rand(1, 999999)));
        self.assertFalse(resource.isFresh(time()), '->isFresh() returns False if the resource does not exist');

if __name__ == '__main__':
    unittest.main();
