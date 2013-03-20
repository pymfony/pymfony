# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.system import Object;
from pymfony.component.system.oop import interface;

"""
"""


@interface
class CacheClearerInterface(Object):
    """CacheClearerInterface.

    @author Dustin Dobervich <ddobervich@gmail.com>

    """

    def clear(self, cacheDir):
        """Clears any caches necessary.

        @param string cacheDir The cache directory.

        """



class ChainCacheClearer(CacheClearerInterface):
    """ChainCacheClearer.

    @author Dustin Dobervich <ddobervich@gmail.com>

    """


    def __init__(self, clearers = None):
        """Constructs a new instance of ChainCacheClearer.

        @param list clearers The initial clearers.

        """
        if clearers is None:
            clearers = list();

        self._clearers = None;
        """@var array clearers"""

        assert isinstance(clearers, list);


        self._clearers = clearers;


    def clear(self, cacheDir):
        """Clears any caches necessary.

        @param string cacheDir The cache directory.

        """

        for clearer in self._clearers :
            clearer.clear(cacheDir);



    def add(self, clearer):
        """Adds a cache clearer to the aggregate.

        @param CacheClearerInterface clearer

        """
        assert isinstance(clearer, CacheClearerInterface);

        self._clearers.append(clearer);
