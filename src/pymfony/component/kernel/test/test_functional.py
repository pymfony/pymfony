#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""
"""

from __future__ import absolute_import;

from os.path import dirname;

from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency import JsonFileLoader
from pymfony.component.kernel import Kernel;
from pymfony.component.kernel import Bundle;
from pymfony.component.kernel import ConfigurableExtension;
from pymfony.component.kernel import Extension;
from pymfony.component.config import ConfigurationInterface;
from pymfony.component.config import TreeBuilder;
from pymfony.component.config import FileLocator;

class AppExtension(ConfigurableExtension):
    def _loadInternal(self, mergedConfig, container):
        assert isinstance(mergedConfig, dict);
        assert isinstance(container, ContainerBuilder);

        for name, value in mergedConfig.items():
            container.getParameterBag().set(self.getAlias()+'.'+name, value);

    def getAlias(self):
        return 'app';

class Configuration(ConfigurationInterface):
    def getConfigTreeBuilder(self):
        treeBuilder = TreeBuilder();
        rootNode = treeBuilder.root('app');

        node =  rootNode.children();
        node =      node.scalarNode('foo');
        node =          node.defaultValue("bar");
        node =      node.end();
        node =  node.end();

        return treeBuilder;

class AppKernel(Kernel):
    def registerBundles(self):
        return [
            FrameworkBundle(),
        ];

    def registerContainerConfiguration(self, loader):
        path = self.locateResource("@/Resources/config/config_{0}.ini".format(
            self.getEnvironment()
        ));
        loader.load(path);


class FrameworkBundle(Bundle):
    pass;

class FrameworkExtension(Extension):
    def load(self, configs, container):
        loader = JsonFileLoader(container, FileLocator(
            dirname(__file__)+"/Resources/config"
        ));

        loader.load("services.json");

        configuration = self.getConfiguration(configs, container);
        config = self._processConfiguration(configuration, configs);




import unittest
import os.path as op;


class Test(unittest.TestCase):
    def setUp(self):
        self._kernel = AppKernel("test", True);
        self._kernel.boot();
        self.container = self._kernel.getContainer();


    def tearDown(self):
        self._kernel.shutdown();


    def testLocateResource(self):
        currdir = op.realpath(op.dirname(__file__));
        formater = lambda v: op.normpath(op.normcase(op.realpath(v)));
        values = {
            "@/Resources/config/services.json": op.join(currdir, "Resources/config/services.json"),
            "../__init__.py": op.join(currdir, "../__init__.py"),
        };

        locator = self.container.get('file_locator');
        self.assertTrue(isinstance(locator, FileLocator), repr(locator));

        for value, expected in values.items():
            result = locator.locate(value, currdir);
            self.assertEqual(formater(result), formater(expected));


    def testExtensionConfig(self):
        self.assertEqual(
            self.container.getParameter('app.foo'),
            'bar'
        );
        self.assertEqual(
            self.container.getParameter('locale'),
            'en'
        );


if __name__ == "__main__":
    unittest.main();
