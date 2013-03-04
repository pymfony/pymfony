# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

from pymfony.component.system.oop import abstract;

from pymfony.component.dependency.compilerpass import MergeExtensionConfigurationPass as BaseMergeExtensionConfigurationPass;

from pymfony.component.dependency.extension import Extension as BaseExtension;
from pymfony.component.dependency import ContainerBuilder;

"""
"""

@abstract
class Extension(BaseExtension):
    """Allow adding classes to the class cache."""

    def __init__(self):
        self.__classes = list();

    def getClassesToCompile(self):
        """Gets the classes to cache.

        @return: dict A dict of classes
        """
        return self.__classes;

    def addClassesToCompile(self, classes):
        """Adds classes to the class cache.

        @param classes: list A list of classes
        """
        assert isinstance(classes, list);

        self.__classes.extend(classes);

@abstract
class ConfigurableExtension(Extension):
    def load(self, configs, container):
        """@final:"""
        self._loadInternal(self._processConfiguration(self.getConfiguration(list(), container), configs), container);

    @abstract
    def _loadInternal(self, mergedConfig, container):
        """Configures the passed container according to the merged
        configuration.

        @param mergedConfig: dict
        @param container: ContainerBuilder
        """
        pass;


class MergeExtensionConfigurationPass(BaseMergeExtensionConfigurationPass):
    """Ensures certain extensions are always loaded.
    """
    def __init__(self, extensions):
        """Constructor.

        @param extensions: list A list of extension name
        """
        assert isinstance(extensions, list);

        self.__extensions = extensions;

    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        for extension in self.__extensions:
            if not container.getExtensionConfig(extension):
                container.loadFromExtension(extension, dict());

        BaseMergeExtensionConfigurationPass.process(self, container);
