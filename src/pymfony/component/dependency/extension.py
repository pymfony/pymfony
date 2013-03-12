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
from pymfony.component.system.oop import abstract;
from pymfony.component.system.oop import final;
from pymfony.component.system.reflection import ReflectionObject;
from pymfony.component.system.reflection import ReflectionClass;

from pymfony.component.config.resource import FileResource;
from pymfony.component.config.definition import Processor;

from pymfony.component.dependency.exception import BadMethodCallException;
from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency import ExtensionInterface;

"""
"""

@interface
class ConfigurationExtensionInterface(Object):
    """ConfigurationExtensionInterface is the interface implemented
    by container extension classes.
    """

    def getConfiguration(self, configs, container):
        """Returns extension configuration

        @param configs: list A list of unmerge dict of configuration values
        @param container: ContainerBuilder A ContainerBuilder instance

        @return: ConfigurationInterface|null The configuration or null
        """

@interface
class PrependExtensionInterface(Object):
    def prepend(self, container):
        """Allow an extension to prepend the extension configurations.

        @param container: ContainerBuilder
        """
        pass;

@abstract
class Extension(ExtensionInterface, ConfigurationExtensionInterface):
    def getXsdValidationBasePath(self):
        return False;

    def getNamespace(self):
        return 'http://example.org/schema/dic/{0}'.format(self.getAlias());

    def getAlias(self):
        className = str(type(self).__name__);
        if not className.endswith("Extension"):
            raise BadMethodCallException(
                'This extension does not follow the naming convention; '
                'you must overwrite the getAlias() method.'
            );
        classBaseName = className[:-9];
        return ContainerBuilder.underscore(classBaseName);

    @final
    def _processConfiguration(self, configuration, configs):
        """
        """
        assert isinstance(configs, list);
        processor = Processor();
        return processor.processConfiguration(configuration, configs);

    def getConfiguration(self, configs, container):
        assert isinstance(configs, list);
        assert isinstance(container, ContainerBuilder);

        className = ReflectionObject(self).getNamespaceName()+'.'+'Configuration';

        r = ReflectionClass(className);

        if r.exists():
            configuration = r.newInstance();
            path = ReflectionObject(configuration).getFileName();
            container.addResource(FileResource(path));
            return configuration;

        return None;
