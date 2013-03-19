# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.config.loader import LoaderResolver;
from pymfony.component.config.loader import LoaderInterface

"""
"""


class LoaderResolverTest(unittest.TestCase):

    def testConstructor(self):
        """
        @covers Symfony\Component\Config\Loader\LoaderResolver.__construct

        """

        loader = LoaderInterfaceMock1();
        resolver = LoaderResolver([
            loader
        ]);

        self.assertEqual([loader], resolver.getLoaders(), '__init__() takes an array of loaders as its first argument');


    def testResolve(self):
        """
        @covers Symfony\Component\Config\Loader\LoaderResolver.resolve

        """

        loader = LoaderInterfaceMock1();
        resolver = LoaderResolver([loader]);
        self.assertFalse(resolver.resolve('foo.foo'), '->resolve() returns False if no loader is able to load the resource');

        loader = LoaderInterfaceMock2();
        resolver = LoaderResolver([loader]);
        self.assertEqual(loader, resolver.resolve(lambda: None), '->resolve() returns the loader for the given resource');


    def testLoaders(self):
        """
        @covers Symfony\Component\Config\Loader\LoaderResolver.getLoaders
        @covers Symfony\Component\Config\Loader\LoaderResolver.addLoader

        """

        resolver = LoaderResolver();
        loader = LoaderInterfaceMock1();
        resolver.addLoader(loader);

        self.assertEqual([loader], resolver.getLoaders(), 'addLoader() adds a loader');

class LoaderInterfaceMock1(LoaderInterface):
    def getResolver(self):
        pass;
    def load(self, resource, resourceType=None):
        pass;
    def setResolver(self, resolver):
        pass;
    def supports(self, resource, resourceType=None):
        pass;

class LoaderInterfaceMock2(LoaderInterface):
    def getResolver(self):
        pass;
    def load(self, resource, resourceType=None):
        pass;
    def setResolver(self, resolver):
        pass;
    def supports(self, resource, resourceType=None):
        return True;

if __name__ == '__main__':
    unittest.main();
