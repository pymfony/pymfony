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
from pymfony.component.dependency.loader import JsonFileLoader
from pymfony.component.kernel.dependency import ConfigurableExtension;
from pymfony.component.config.definition import ConfigurationInterface;
from pymfony.component.config.definition.builder import TreeBuilder;
from pymfony.component.config import FileLocator;


class FrameworkExtension(ConfigurableExtension):
    def _loadInternal(self, config, container):
        assert isinstance(config, dict);
        assert isinstance(container, ContainerBuilder);

        loader = JsonFileLoader(container, FileLocator(
            dirname(__file__)+"/../Resources/config"
        ));

        loader.load("services.json");
        loader.load("cli.json");

        for name, value in config.items():
            container.getParameterBag().set(self.getAlias()+'.'+name, value);

        container.setParameter('kernel.default_locale', config['default_locale']);

    def getAlias(self):
        return 'framework';


class Configuration(ConfigurationInterface):
    def getConfigTreeBuilder(self):
        treeBuilder = TreeBuilder();
        rootNode = treeBuilder.root('framework');

        node =  rootNode.children();
        node =      node.scalarNode('default_locale');
        node =          node.defaultValue("en");
        node =      node.end();
        node =  node.end();

        return treeBuilder;
