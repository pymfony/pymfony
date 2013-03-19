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

from pymfony.component.system.types import String;

from pymfony.component.config.loader import LoaderResolver;
from pymfony.component.config.loader import LoaderInterface;
from pymfony.component.config.exception import FileLoaderLoadException;
from pymfony.component.config.loader import Loader;

"""
"""


class LoaderTest(unittest.TestCase):

    def testGetSetResolver(self):
        """
        @covers Symfony\Component\Config\Loader\Loader.getResolver
        @covers Symfony\Component\Config\Loader\Loader.setResolver

        """

        resolver = LoaderResolver();
        loader = ProjectLoader1();
        loader.setResolver(resolver);
        self.assertEqual(resolver, loader.getResolver(), '->setResolver() sets the resolver loader');


    def testResolve(self):
        """
        @covers Symfony\Component\Config\Loader\Loader.resolve

        """

        loader1 = LoaderInterfaceMock1();
        resolver = LoaderResolver([loader1]);
        loader = ProjectLoader1();
        loader.setResolver(resolver);

        self.assertEqual(loader, loader.resolve('foo.foo'), '->resolve() finds a loader');
        self.assertEqual(loader1, loader.resolve('foo.xml'), '->resolve() finds a loader');

        loader1 = LoaderInterfaceMock2();
        resolver = LoaderResolver([loader1]);
        loader = ProjectLoader1();
        loader.setResolver(resolver);
        try:
            loader.resolve('FOOBAR');
            self.fail('->resolve() raise a FileLoaderLoadException if the resource cannot be loaded');
        except FileLoaderLoadException as e:
            self.assertTrue(isinstance(e, FileLoaderLoadException), '->resolve() raise a FileLoaderLoadException if the resource cannot be loaded');



    def testImports(self):

        loader = LoaderMock();

        self.assertEqual('yes', loader.imports('foo'));



class ProjectLoader1(Loader):

    def load(self, resource, type_ = None):
        pass;


    def supports(self, resource, type_ = None):

        return isinstance(resource, String) and resource.endswith("{0}foo".format(os.path.extsep));


    def getType(self):
        pass;





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

class LoaderMock(Loader):
    def load(self, resource, resourceType=None):
        return 'yes';
    def supports(self, resource, resourceType=None):
        return True;

if __name__ == '__main__':
    unittest.main();
