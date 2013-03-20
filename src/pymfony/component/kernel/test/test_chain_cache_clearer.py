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

from pymfony.component.kernel.cache_clearer import ChainCacheClearer;
from pymfony.component.kernel.cache_clearer import CacheClearerInterface;

"""
"""


class ChainCacheClearerTest(unittest.TestCase):


    def setUp(self):

        self._cacheDir = tempfile.gettempdir() + '/sf2_cache_clearer_dir';
        suffix = 0;
        while os.path.exists(self._cacheDir+str(suffix)):
            suffix += 1;
        self._cacheDir = self._cacheDir+str(suffix);


    def tearDown(self):

        try:
            shutil.rmtree(self._cacheDir);
        except Exception:
            pass;


    def testInjectClearersInConstructor(self):

        clearer = self._getMockClearer();

        chainClearer = ChainCacheClearer([clearer]);
        chainClearer.clear(self._cacheDir);


    def testInjectClearerUsingAdd(self):

        clearer = self._getMockClearer();

        chainClearer = ChainCacheClearer();
        chainClearer.add(clearer);
        chainClearer.clear(self._cacheDir);


    def _getMockClearer(self):

        return CacheClearerInterfaceMock();


class CacheClearerInterfaceMock(CacheClearerInterface):
    def clear(self, cacheDir):
        pass;

if __name__ == '__main__':
    unittest.main()
