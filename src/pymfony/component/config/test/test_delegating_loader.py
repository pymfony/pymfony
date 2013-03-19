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
from pymfony.component.config.loader import DelegatingLoader;
from pymfony.component.config.loader import LoaderInterface;
from pymfony.component.config.exception import FileLoaderLoadException;

"""
"""


class DelegatingLoaderTest(unittest.TestCase):

    def testConstructor(self):
        """
        @covers Symfony\Component\Config\Loader\DelegatingLoader.__construct

        """

        resolver = LoaderResolver();
        loader = DelegatingLoader(resolver);
        self.assertTrue(True, '__init__() takes a loader resolver as its first argument');


    def testGetSetResolver(self):
        """
        @covers Symfony\Component\Config\Loader\DelegatingLoader.getResolver
        @covers Symfony\Component\Config\Loader\DelegatingLoader.setResolver

        """

        resolver = LoaderResolver();
        loader = DelegatingLoader(resolver);
        self.assertEqual(resolver, loader.getResolver(), '->getResolver() gets the resolver loader');
        resolver = LoaderResolver();
        loader.setResolver(resolver);
        self.assertEqual(resolver, loader.getResolver(), '->setResolver() sets the resolver loader');


    def testSupports(self):
        """
        @covers Symfony\Component\Config\Loader\DelegatingLoader.supports

        """

        loader1 = LoaderInterfaceMock1();
        loader = DelegatingLoader(LoaderResolver([loader1]));
        self.assertTrue(loader.supports('foo.xml'), '->supports() returns True if the resource is loadable');

        loader1 = LoaderInterfaceMock2();
        loader = DelegatingLoader(LoaderResolver([loader1]));
        self.assertFalse(loader.supports('foo.foo'), '->supports() returns False if the resource is not loadable');


    def testLoad(self):
        """
        @covers Symfony\Component\Config\Loader\DelegatingLoader.load

        """

        loader = LoaderInterfaceMock1();
        resolver = LoaderResolver([loader]);
        loader = DelegatingLoader(resolver);

        loader.load('foo');


    def testLoadThrowsAnExceptionIfTheResourceCannotBeLoaded(self):
        """@expectedException Symfony\Component\Config\Exception\FileLoaderLoadException

        """

        try:
            loader = LoaderInterfaceMock2();
            resolver = LoaderResolver([loader]);
            loader = DelegatingLoader(resolver);

            loader.load('foo');

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, FileLoaderLoadException));



class LoaderInterfaceMock1(LoaderInterface):
    def getResolver(self):
        pass;
    def load(self, resource, resourceType=None):
        pass;
    def setResolver(self, resolver):
        pass;
    def supports(self, resource, resourceType=None):
        return True;

class LoaderInterfaceMock2(LoaderInterface):
    def getResolver(self):
        pass;
    def load(self, resource, resourceType=None):
        pass;
    def setResolver(self, resolver):
        pass;
    def supports(self, resource, resourceType=None):
        return False;

if __name__ == '__main__':
    unittest.main();
