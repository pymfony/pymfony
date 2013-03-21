# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.kernel.cache_warmer import CacheWarmerInterface;
from pymfony.component.console_routing.interface import RouterInterface;
from pymfony.component.kernel.cache_warmer import WarmableInterface

"""
"""

class ConsoleRouterCacheWarmer(CacheWarmerInterface):
    """Generates the router matcher and generator classes.

    @author Fabien Potencier <fabien@symfony.com>

    """

    def __init__(self, router):
        """Constructor.

        @param RouterInterface $router A Router instance

        """
        assert isinstance(router, RouterInterface);

        self.__router = router;


    def warmUp(self, cacheDir):
        """Warms up the cache.

        @param string cacheDir The cache directory

        """

        if isinstance(self.__router, WarmableInterface) :
            self.__router.warmUp(cacheDir);


    def isOptional(self):
        """Checks whether this warmer is optional or not.

        @return Boolean always true

        """
        return True;
