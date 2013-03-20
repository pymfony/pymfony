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

from pymfony.component.kernel.cache_warmer import CacheWarmer;
from pymfony.component.system.exception import RuntimeException

"""
"""


class CacheWarmerTest(unittest.TestCase):

    def setUp(self):

        self._cacheFile = tempfile.gettempdir() + '/sf2_cache_warmer_dir';
        suffix = 0;
        while os.path.exists(self._cacheFile+str(suffix)):
            suffix += 1;
        self._cacheFile = self._cacheFile+str(suffix);

    def tearDown(self):

        try:
            os.unlink(self._cacheFile);
        except Exception:
            pass;

    def testWriteCacheFileCreatesTheFile(self):

        warmer = TestCacheWarmer(self._cacheFile);
        warmer.warmUp(os.path.dirname(self._cacheFile));

        self.assertTrue(os.path.exists(self._cacheFile));


    def testWriteNonWritableCacheFileThrowsARuntimeException(self):
        """@expectedException RuntimeException

        """
        try:
            nonWritableFile = '/this/file/is/very/probably/not/writable';
            warmer = TestCacheWarmer(nonWritableFile);
            warmer.warmUp(os.path.dirname(nonWritableFile));

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));




class TestCacheWarmer(CacheWarmer):

    def __init__(self, filename):

        self._file = filename;


    def warmUp(self, cacheDir):

        self._writeCacheFile(self._file, 'content');


    def isOptional(self):

        return False;

if __name__ == '__main__':
    unittest.main();
