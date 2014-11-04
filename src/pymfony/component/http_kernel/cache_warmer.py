# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import os;

from pymfony.component.system import Object;
from pymfony.component.system.oop import interface;
from pymfony.component.system.oop import abstract;
from pymfony.component.system.exception import RuntimeException;

"""
"""


@interface
class WarmableInterface(Object):
    """Interface for classes that support warming their cache.

    @author Fabien Potencier <fabien@symfony.com>

    """

    def warmUp(self, cacheDir):
        """Warms up the cache.

        @param string cacheDir The cache directory

        """


@interface
class CacheWarmerInterface(WarmableInterface):
    """Interface for classes able to warm up the cache.

    @author Fabien Potencier <fabien@symfony.com>

    """

    def isOptional(self):
        """Checks whether this warmer is optional or not.

        Optional warmers can be ignored on certain conditions.

        A warmer should return True if the cache can be:
        generated incrementally and on-demand.

        @return Boolean True if the warmer is optional, False otherwise:

        """



@abstract
class CacheWarmer(CacheWarmerInterface):
    """Abstract cache warmer that knows how to write a file to the cache.

    @author Fabien Potencier <fabien@symfony.com>

    """

    def _writeCacheFile(self, filename, content):

        try:
            suffix = 0;
            while os.path.exists(filename+str(suffix)):
                suffix += 1;
            tmpFile = filename+str(suffix);
            f = open(tmpFile, 'w');
            f.write(content);
            f.close();
            if os.path.exists(filename):
                os.remove(filename);
            os.rename(tmpFile, filename);
            if hasattr(os, 'chmod'):
                umask = os.umask(0o220);
                os.umask(umask);
                os.chmod(filename, 0o666 & ~umask);
        except Exception:
            raise RuntimeException('Failed to write cache file "{0}".'.format(filename));
        else:
            try:
                if hasattr(os, 'chmod'):
                    umask = os.umask(0o220);
                    os.umask(umask);
                    os.chmod(filename, 0o666 & ~umask);
            except Exception:
                pass;
        finally:
            try:
                f.close();
            except Exception:
                pass;
            if os.path.exists(tmpFile):
                os.remove(tmpFile);


class CacheWarmerAggregate(CacheWarmerInterface):
    """Aggregates several cache warmers into a single one.

    @author Fabien Potencier <fabien@symfony.com>

    """


    def __init__(self, warmers = None):
        if warmers is None:
            warmers = list();
        assert isinstance(warmers, list);

        self._warmers = None;
        self._optionalsEnabled = None;

        self.setWarmers(warmers);
        self._optionalsEnabled = False;


    def enableOptionalWarmers(self):

        self._optionalsEnabled = True;


    def warmUp(self, cacheDir):
        """Warms up the cache.

        @param string cacheDir The cache directory

        """

        for  warmer in self._warmers :
            if not self._optionalsEnabled and warmer.isOptional() :
                continue;


            warmer.warmUp(cacheDir);



    def isOptional(self):
        """Checks whether this warmer is optional or not.

        @return Boolean always True

        """

        return False;


    def setWarmers(self, warmers):
        assert isinstance(warmers, list);

        self._warmers = list();
        for warmer in warmers :
            self.add(warmer);



    def add(self, warmer):
        assert isinstance(warmer, CacheWarmerInterface);

        self._warmers.append(warmer);
