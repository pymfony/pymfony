# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;
import os;
import shutil;
import tempfile;

from pymfony.component.kernel.cache_warmer import CacheWarmerInterface;
from pymfony.component.kernel.cache_warmer import CacheWarmerAggregate;

"""
"""


class CacheWarmerAggregateTest(unittest.TestCase):

    def setUp(self):

        self._cacheDir = tempfile.gettempdir() + 'sf2_cache_clearer_dir';
        suffix = 0;
        while os.path.exists(self._cacheDir+str(suffix)):
            suffix += 1;
        self._cacheDir = self._cacheDir+str(suffix);


    def tearDown(self):

        try:
            shutil.rmtree(self._cacheDir);
        except Exception:
            pass;


    def testInjectWarmersUsingConstructor(self):

        warmer = CacheWarmerInterfaceMock1();

        aggregate = CacheWarmerAggregate([warmer]);
        aggregate.warmUp(self._cacheDir);


    def testInjectWarmersUsingAdd(self):

        warmer = CacheWarmerInterfaceMock1();

        aggregate = CacheWarmerAggregate();
        aggregate.add(warmer);
        aggregate.warmUp(self._cacheDir);


    def testInjectWarmersUsingSetWarmers(self):

        warmer = CacheWarmerInterfaceMock1();

        aggregate = CacheWarmerAggregate();
        aggregate.setWarmers([warmer]);
        aggregate.warmUp(self._cacheDir);


    def testWarmupDoesCallWarmupOnOptionalWarmersWhenEnableOptionalWarmersIsEnabled(self):

        warmer = CacheWarmerInterfaceMock3();

        aggregate = CacheWarmerAggregate([warmer]);
        aggregate.enableOptionalWarmers();
        aggregate.warmUp(self._cacheDir);


    def testWarmupDoesNotCallWarmupOnOptionalWarmersWhenEnableOptionalWarmersIsNotEnabled(self):

        warmer = CacheWarmerInterfaceMock2();

        aggregate = CacheWarmerAggregate([warmer]);
        aggregate.warmUp(self._cacheDir);


class CacheWarmerInterfaceMock1(CacheWarmerInterface):
    def isOptional(self):
        pass;
    def warmUp(self, cacheDir):
        pass;

class CacheWarmerInterfaceMock2(CacheWarmerInterface):
    def isOptional(self):
        return True;
    def warmUp(self, cacheDir):
        raise Exception();

class CacheWarmerInterfaceMock3(CacheWarmerInterface):
    def isOptional(self):
        raise Exception();
    def warmUp(self, cacheDir):
        pass;


if __name__ == '__main__':
    unittest.main();
