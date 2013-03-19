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
import shutil;
from time import time;
from random import randint as rand;

from pymfony.component.config.resource import DirectoryResource;

"""
"""


class DirectoryResourceTest(unittest.TestCase):

    def setUp(self):

        self._directory = tempfile.gettempdir()+'/symfonyDirectoryIterator';
        if not os.path.exists(self._directory) :
            os.mkdir(self._directory);

        self._touch(self._directory+'/tmp.xml');

    def tearDown(self):

        if not os.path.isdir(self._directory) :
            return;

        self._removeDirectory(self._directory);


    def _removeDirectory(self, directory):

        shutil.rmtree(directory, ignore_errors=True);

    def _touch(self, path, mtime = None, atime = None):
        currTime =  time();
        if mtime is None:
            mtime = currTime;
        if atime is None:
            atime = currTime;
        try:
            os.utime(path, (atime, mtime));
        except Exception:
            open(path, 'a').close();
            os.utime(path, (atime, mtime));


    def testGetResource(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.getResource

        """

        resource = DirectoryResource(self._directory);
        self.assertEqual(self._directory, resource.getResource(), '->getResource() returns the path to the resource');


    def testGetPattern(self):

        resource = DirectoryResource('foo', 'bar');
        self.assertEqual('bar', resource.getPattern());


    def testIsFresh(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.isFresh

        """

        resource = DirectoryResource(self._directory);
        self.assertTrue(resource.isFresh(time() + 10), '->isFresh() returns True if the resource has not changed');
        self.assertFalse(resource.isFresh(time() - 86400), '->isFresh() returns False if the resource has been updated');

        resource = DirectoryResource('/____foo/foobar'+str(rand(1, 999999)));
        self.assertFalse(resource.isFresh(time()), '->isFresh() returns False if the resource does not exist');


    def testIsFreshUpdateFile(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.isFresh

        """

        resource = DirectoryResource(self._directory);
        self._touch(self._directory+'/tmp.xml', time() + 20);
        self.assertFalse(resource.isFresh(time() + 10), '->isFresh() returns False if an existing file is modified');


    def testIsFreshNewFile(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.isFresh

        """

        resource = DirectoryResource(self._directory);
        self._touch(self._directory+'/new.xml', time() + 20);
        self.assertFalse(resource.isFresh(time() + 10), '->isFresh() returns False if a new file is added');


    def testIsFreshDeleteFile(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.isFresh

        """

        resource = DirectoryResource(self._directory);
        os.unlink(self._directory+'/tmp.xml');
        # Update the modification time it don't on Unix system.
        self._touch(self._directory, time() + 20);
        self.assertFalse(resource.isFresh(time() + 10), '->isFresh() returns False if an existing file is removed');


    def testIsFreshDeleteDirectory(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.isFresh

        """

        resource = DirectoryResource(self._directory);
        self._removeDirectory(self._directory);
        self.assertFalse(resource.isFresh(time()), '->isFresh() returns False if the whole resource is removed');


    def testIsFreshCreateFileInSubdirectory(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.isFresh

        """

        subdirectory = self._directory+'/subdirectory';
        os.mkdir(subdirectory);

        resource = DirectoryResource(self._directory);
        self.assertTrue(resource.isFresh(time() + 10), '->isFresh() returns True if an unmodified subdirectory exists');

        self._touch(subdirectory+'/newfile.xml', time() + 20);
        self.assertFalse(resource.isFresh(time() + 10), '->isFresh() returns False if a new file in a subdirectory is added');


    def testIsFreshModifySubdirectory(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.isFresh

        """

        resource = DirectoryResource(self._directory);

        subdirectory = self._directory+'/subdirectory';
        os.mkdir(subdirectory);
        self._touch(subdirectory, time() + 20);

        self.assertFalse(resource.isFresh(time() + 10), '->isFresh() returns False if a subdirectory is modified (e.g. a file gets deleted)');


    def testFilterRegexListNoMatch(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.isFresh

        """

        resource = DirectoryResource(self._directory, '\.(foo|xml)$');

        self._touch(self._directory+'/new.bar', time() + 20);
        self.assertTrue(resource.isFresh(time() + 10), '->isFresh() returns True if a new file not matching the filter regex is created');


    def testFilterRegexListMatch(self):
        """
        @covers Symfony\Component\Config\Resource\DirectoryResource.isFresh

        """

        resource = DirectoryResource(self._directory, '\.(foo|xml)$');

        self._touch(self._directory+'/new.xml', time() + 20);
        self.assertFalse(resource.isFresh(time() + 10), '->isFresh() returns False if an new file matching the filter regex is created ');

if __name__ == '__main__':
    unittest.main();
