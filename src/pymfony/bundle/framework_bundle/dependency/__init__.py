# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

from os.path import dirname;

from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency.loader import YamlFileLoader;

from pymfony.component.config import FileLocator;
from pymfony.component.config.definition import ConfigurationInterface;
from pymfony.component.config.definition.builder import TreeBuilder;

from pymfony.component.kernel.dependency import Extension;

"""
"""

class FrameworkExtension(Extension):
    """FrameworkExtension.

    @author: Fabien Potencier <fabien@symfony.com>
    @author: Jeremy Mikola <jmikola@gmail.com>
    """
    def load(self, configs, container):
        """Responds to the app.config configuration parameter.

        @param configs: list
        @param container: ContainerBuilder
        """
        assert isinstance(configs, list);
        assert isinstance(container, ContainerBuilder);

        loader = YamlFileLoader(container, FileLocator(
            dirname(__file__)+"/../Resources/config"
        ));

        loader.load("services.yml");

        configuration = self.getConfiguration(configs, container);
        config = self._processConfiguration(configuration, configs);

        container.setParameter('kernel.default_locale', config['default_locale']);


    def __registerConsoleConfiguration(self, config, container, loader):
        """Loads the console configuration.

        @param config:    dict             A router configuration array
        @param container: ContainerBuilder A ContainerBuilder instance
        @param loader:    JsonFileLoader   An JsonFileLoader instance
        """
        assert isinstance(config, dict);
        assert isinstance(container, ContainerBuilder);

        loader.load("console.yml");

        if 'router' in config:
            self.__registerConsoleRouterConfiguration(config['router'], container, loader);

        container.setParameter('console.exception_controller', config['exception_controller']);


    def __registerConsoleRouterConfiguration(self, config, container, loader):
        """Loads the console router  configuration.

        @param config:    dict             A router configuration array
        @param container: ContainerBuilder A ContainerBuilder instance
        @param loader:    JsonFileLoader   An JsonFileLoader instance
        """
        assert isinstance(config, dict);

        loader.load("console_routing.yml");

        container.setParameter('console.router.resource', config['resource']);
        container.setParameter('console.router.default_route', config['default_route']);
        container.setParameter('console.router.auto_regitration', config['auto_regitration']);



class Configuration(ConfigurationInterface):
    """FrameworkExtension configuration structure.

    @author: Jeremy Mikola <jmikola@gmail.com>
    """
    def getConfigTreeBuilder(self):
        """Generates the configuration tree builder.

        @return: TreeBuilder The tree builder

        @raise RuntimeException: When using the deprecated 'charset' setting
        """
        treeBuilder = TreeBuilder();
        rootNode = treeBuilder.root('framework');

        node =  rootNode.children();
        node =      node.scalarNode('default_locale').defaultValue("en").end();
        node =  node.end();

        return treeBuilder;
