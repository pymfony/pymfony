# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import sys;
from pymfony.component.dependency.interface import ContainerInterface
if sys.version_info[0] >= 3:
    from configparser import ConfigParser;
else:
    from ConfigParser import ConfigParser;

import os.path;
import json;

from pymfony.component.system.oop import abstract;
from pymfony.component.system.types import String;

from pymfony.component.config import FileLocatorInterface;
from pymfony.component.config.loader import FileLoader as BaseFileLoader;
from pymfony.component.config.resource import FileResource;

from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency import Definition;
from pymfony.component.dependency import Reference;
from pymfony.component.dependency.definition import Alias;
from pymfony.component.dependency.definition import DefinitionDecorator
from pymfony.component.dependency.exception import InvalidArgumentException;

from pymfony.component.yaml import Yaml;

"""
"""

@abstract
class FileLoader(BaseFileLoader):
    def __init__(self, container, locator):
        assert isinstance(container, ContainerBuilder);
        assert isinstance(locator, FileLocatorInterface);

        self._container = container;
        BaseFileLoader.__init__(self, locator);



class IniFileLoader(FileLoader):
    """IniFileLoader loads parameters from INI files."""

    def load(self, resource, resourceType=None):
        path = self._locator.locate(resource);

        self._container.addResource(FileResource(path));

        content = self._parseFile(path);

        if not content:
            return;

        self.__parseParameters(content);

    def supports(self, resource, resourceType=None):
        if isinstance(resource, String):
            if os.path.basename(resource).endswith(".ini"):
                return True;
        return False;

    def _parseFile(self, filename):
        """Parses a INI file.

        @param filename: string The path file

        @return: dict The file content

        @raise InvalidArgumentException: When INI file is not valid
        """
        content = dict();
        cfgParser = ConfigParser();
        result = cfgParser.read(filename);
        if not result:
            raise InvalidArgumentException(
                'The "{0]" file is not valid.'.format(filename)
            );

        for section in cfgParser.sections():
            content[section] = dict();
            for key, value in cfgParser.items(section):
                content[section][key] = value;
        return content;

    def __parseParameters(self, content):
        if 'parameters' in content:
            for key, value in dict(content['parameters']).items():
                self._container.setParameter(key, value);


class JsonFileLoader(FileLoader):
    """JsonFileLoader loads parameters from JSON files."""

    def load(self, resource, resourceType = None):
        path = self._locator.locate(resource);

        content = self._parseFile(path);

        self._container.addResource(FileResource(path));

        # empty file
        if content is None:
            return;

        # imports
        self.__parseImports(content, path);

        # parameters
        if 'parameters' in content:
            for key, value in content['parameters'].items():
                self._container.setParameter(key, self.__resolveServices(value));

        # extensions
        self.__loadFromExtensions(content);

        # services
        self.__parseDefinitions(content, resource);


    def supports(self, resource, resourceType = None):
        """Returns true if this class supports the given resource.

        @param resource:     mixed  A resource
        @param resourceType: string The resource type

        @return Boolean true if this class supports the given resource,
            false otherwise

        """
        return isinstance(resource, String) and resource.endswith("{0}json".format(os.path.extsep));

    def _parseFile(self, filename):
        """Parses a JSON file.

        @param filename: string The path file

        @return: dict The file content

        @raise InvalidArgumentException: When JSON file is not valid
        """
        f = open(filename);
        s = f.read().strip();
        f.close();
        del f;

        if not s:
            return None;

        try:
            result = json.loads(s);
        except ValueError as e:
            raise InvalidArgumentException(e);

        return self.__validate(result, filename);

    def __validate(self, content, resource):
        """Validates a YAML file.

        @param content:  mixed
        @param resource: string

        @return: dict

        @raise InvalidArgumentException: When service file is not valid

        """
        if content is None:
            return;

        if not isinstance(content, dict):
            raise InvalidArgumentException('The "{0}" file is not valid.'.format(
                resource
            ));

        for namespace in content.keys():
            if namespace in ['imports', 'parameters', 'services']:
                continue;

            if not self._container.hasExtension(namespace):
                extensionNamespaces = filter(None, map(lambda e: e.getAlias(), self._container.getExtensions()));
                raise InvalidArgumentException(
                    'There is no extension able to load the configuration '
                    'for "{0}" (in {1}). Looked for namespace "{0}", found "{2}"'
                    ''.format(
                        namespace,
                        resource,
                        '", "'.join(extensionNamespaces)
                ));

        return content;


    def __parseImports(self, content, resource):
        """Parses all imports

        @param content:  dict
        @param resource: string

        """
        if 'imports' not in content:
            return;

        for imports in content['imports']:
            self.setCurrentDir(os.path.dirname(resource));
            self.imports(imports['resource'], None, bool(imports['ignore_errors']) if 'ignore_errors' in imports else False, resource);


    def __parseDefinitions(self, content, resource):
        """Parses definitions

        @param content:  dict
        @param resource: string

        """
        if not 'services' in content:
            return;

        for identifier, service in content['services'].items():
            self.__parseDefinition(identifier, service, resource);


    def __parseDefinition(self, identifier, service, resource):
        """Parses a definition.

        @param identifier: string
        @param service:    dict
        @param resource:   string

        @raise InvalidArgumentException: When tags are invalid

        """

        if isinstance(service, String) and service.startswith('@') :
            self._container.setAlias(identifier, service[1:]);

            return;
        elif 'alias' in service :
            public = 'public' not in service or bool(service['public']);
            self._container.setAlias(identifier, Alias(service['alias'], public));

            return;


        if 'parent' in service :
            definition = DefinitionDecorator(service['parent']);
        else :
            definition = Definition();

        if 'class' in service:
            definition.setClass(service['class']);

        if 'scope' in service:
            definition.setScope(service['scope']);

        if 'synthetic' in service:
            definition.setSynthetic(service['synthetic']);

        if 'public' in service:
            definition.setPublic(service['public']);

        if 'abstract' in service:
            definition.setAbstract(service['abstract']);

        if 'factory_class' in service:
            definition.setFactoryClass(service['factory_class']);

        if 'factory_method' in service:
            definition.setFactoryMethod(service['factory_method']);

        if 'factory_service' in service:
            definition.setFactoryService(service['factory_service']);

        if 'file' in service:
            definition.setFile(service['file']);

        if 'arguments' in service:
            definition.setArguments(self.__resolveServices(service['arguments']));

        if 'properties' in service:
            definition.setProperties(self.__resolveServices(service['properties']));

        if 'configurator' in service:
            if isinstance(service['configurator'], String):
                definition.setConfigurator(service['configurator']);
            else:
                definition.setConfigurator([
                    self.__resolveServices(service['configurator'][0]),
                    service['configurator'][1]
                ]);

        if 'calls' in service:
            for call in service['calls']:
                args = self.__resolveServices(call[1]) if len(call) >= 2 else [];
                definition.addMethodCall(call[0], args);

        if 'tags' in service:
            if not isinstance(service['tags'], list):
                raise InvalidArgumentException(
                    'Parameter "tags" must be a list for service '
                    '"{0}" in {1}.'.format(identifier, resource)
                );

            for tag in service['tags']:
                if not isinstance(tag, dict) or 'name' not in tag:
                    raise InvalidArgumentException(
                        'A "tags" entry is missing a "name" key for service '
                        '"{0}" in {1}.'.format(identifier, resource)
                    );

                name = tag['name'];
                del tag['name'];

                for value in tag.values():
                    if not isinstance(value, (type(None),String,int,float,bool)):
                        raise InvalidArgumentException(
                            'A "tags" attribute must be of a scalar-type '
                            'for service "{0}", tag "{1}" in {2}.'
                            ''.format(identifier, name, resource)
                        );

                definition.addTag(name, tag);

        self._container.setDefinition(identifier, definition);


    def __resolveServices(self, value):
        """Resolves services.

        @param value: string

        @return: Reference

        """
        if isinstance(value, list):
            value = list(map(self.__resolveServices, value));
        if isinstance(value, String) and value.startswith("@"):
            if value.startswith('@@'):
                value = value[1:];
                invalidBehavior = None;
            elif value.startswith("@?"):
                value = value[2:];
                invalidBehavior = ContainerInterface.IGNORE_ON_INVALID_REFERENCE;
            else:
                value = value[1:];
                invalidBehavior = ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE;

            if value.endswith("="):
                value = value[:-1];
                strict = False;
            else:
                strict = True;

            if None is not invalidBehavior:
                value = Reference(value, invalidBehavior, strict);

        return value;


    def __loadFromExtensions(self, content):
        """Loads from Extensions

        @param content: dict

        """
        assert isinstance(content, dict);

        for namespace, values in content.items():
            if namespace in ['imports', 'parameters', 'services']:
                continue;

            if not isinstance(values, dict) :
                values = {};

            self._container.loadFromExtension(namespace, values);


class YamlFileLoader(FileLoader):
    """YamlFileLoader loads YAML files service definitions.

    The YAML format does not support anonymous services (cf. the XML loader).

    @author Fabien Potencier <fabien@symfony.com>

    """

    def load(self, resource, resourceType = None):
        """Loads a Yaml file.

        @param resource:     mixed  The resource
        @param resourceType: string The resource type

        """
        path = self._locator.locate(resource);

        content = self._loadFile(path);

        self._container.addResource(FileResource(path));

        # empty file
        if content is None:
            return;

        # imports
        self.__parseImports(content, path);

        # parameters
        if 'parameters' in content:
            for key, value in content['parameters'].items():
                self._container.setParameter(key, self.__resolveServices(value));


        # extensions
        self.__loadFromExtensions(content);

        # services
        self.__parseDefinitions(content, resource);


    def supports(self, resource, resourceType = None):
        """Returns true if this class supports the given resource.

        @param resource:     mixed  A resource
        @param resourceType: string The resource type

        @return Boolean true if this class supports the given resource,
            false otherwise

        """
        return isinstance(resource, String) and resource.endswith("{0}yml".format(os.path.extsep));


    def __parseImports(self, content, resource):
        """Parses all imports

        @param content:  dict
        @param resource: string

        """
        if 'imports' not in content:
            return;

        for imports in content['imports']:
            self.setCurrentDir(os.path.dirname(resource));
            self.imports(imports['resource'], None, bool(imports['ignore_errors']) if 'ignore_errors' in imports else False, resource);


    def __parseDefinitions(self, content, resource):
        """Parses definitions

        @param content:  dict
        @param resource: string

        """
        if not 'services' in content:
            return;

        for identifier, service in content['services'].items():
            self.__parseDefinition(identifier, service, resource);

    def __parseDefinition(self, identifier, service, resource):
        """Parses a definition.

        @param identifier: string
        @param service:    dict
        @param resource:   string

        @raise InvalidArgumentException: When tags are invalid

        """

        if isinstance(service, String) and service.startswith('@') :
            self._container.setAlias(identifier, service[1:]);

            return;
        elif 'alias' in service :
            public = 'public' not in service or bool(service['public']);
            self._container.setAlias(identifier, Alias(service['alias'], public));

            return;


        if 'parent' in service :
            definition = DefinitionDecorator(service['parent']);
        else :
            definition = Definition();

        if 'class' in service:
            definition.setClass(service['class']);

        if 'scope' in service:
            definition.setScope(service['scope']);

        if 'synthetic' in service:
            definition.setSynthetic(service['synthetic']);

        if 'public' in service:
            definition.setPublic(service['public']);

        if 'abstract' in service:
            definition.setAbstract(service['abstract']);

        if 'factory_class' in service:
            definition.setFactoryClass(service['factory_class']);

        if 'factory_method' in service:
            definition.setFactoryMethod(service['factory_method']);

        if 'factory_service' in service:
            definition.setFactoryService(service['factory_service']);

        if 'file' in service:
            definition.setFile(service['file']);

        if 'arguments' in service:
            definition.setArguments(self.__resolveServices(service['arguments']));

        if 'properties' in service:
            definition.setProperties(self.__resolveServices(service['properties']));

        if 'configurator' in service:
            if isinstance(service['configurator'], String):
                definition.setConfigurator(service['configurator']);
            else:
                definition.setConfigurator([
                    self.__resolveServices(service['configurator'][0]),
                    service['configurator'][1]
                ]);

        if 'calls' in service:
            for call in service['calls']:
                args = self.__resolveServices(call[1]) if len(call) >= 2 else [];
                definition.addMethodCall(call[0], args);

        if 'tags' in service:
            if not isinstance(service['tags'], list):
                raise InvalidArgumentException(
                    'Parameter "tags" must be a list for service '
                    '"{0}" in {1}.'.format(identifier, resource)
                );

            for tag in service['tags']:
                if not isinstance(tag, dict) or 'name' not in tag:
                    raise InvalidArgumentException(
                        'A "tags" entry is missing a "name" key for service '
                        '"{0}" in {1}.'.format(identifier, resource)
                    );

                name = tag['name'];
                del tag['name'];

                for value in tag.values():
                    if not isinstance(value, (type(None),String,int,float,bool)):
                        raise InvalidArgumentException(
                            'A "tags" attribute must be of a scalar-type '
                            'for service "{0}", tag "{1}" in {2}.'
                            ''.format(identifier, name, resource)
                        );

                definition.addTag(name, tag);

        self._container.setDefinition(identifier, definition);


    def _loadFile(self, resource):
        """Loads a YAML file.

        @param resource: string

        @return dict The file content

        """

        return self.__validate(Yaml.parse(resource), resource);


    def __validate(self, content, resource):
        """Validates a YAML file.

        @param content:  mixed
        @param resource: string

        @return: dict

        @raise InvalidArgumentException: When service file is not valid

        """
        if content is None:
            return;

        if not isinstance(content, dict):
            raise InvalidArgumentException('The "{0}" file is not valid.'.format(
                resource
            ));

        for namespace in content.keys():
            if namespace in ['imports', 'parameters', 'services']:
                continue;

            if not self._container.hasExtension(namespace):
                extensionNamespaces = filter(None, map(lambda e: e.getAlias(), self._container.getExtensions()));
                raise InvalidArgumentException(
                    'There is no extension able to load the configuration '
                    'for "{0}" (in {1}). Looked for namespace "{0}", found "{2}"'
                    ''.format(
                        namespace,
                        resource,
                        '", "'.join(extensionNamespaces)
                ));

        return content;


    def __resolveServices(self, value):
        """Resolves services.

        @param value: string

        @return: Reference

        """
        if isinstance(value, list):
            value = list(map(self.__resolveServices, value));
        if isinstance(value, String) and value.startswith("@"):
            if value.startswith('@@'):
                value = value[1:];
                invalidBehavior = None;
            elif value.startswith("@?"):
                value = value[2:];
                invalidBehavior = ContainerInterface.IGNORE_ON_INVALID_REFERENCE;
            else:
                value = value[1:];
                invalidBehavior = ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE;

            if value.endswith("="):
                value = value[:-1];
                strict = False;
            else:
                strict = True;

            if None is not invalidBehavior:
                value = Reference(value, invalidBehavior, strict);

        return value;


    def __loadFromExtensions(self, content):
        """Loads from Extensions

        @param content: dict

        """
        assert isinstance(content, dict);

        for namespace, values in content.items():
            if namespace in ['imports', 'parameters', 'services']:
                continue;

            if not isinstance(values, dict) :
                values = {};

            self._container.loadFromExtension(namespace, values);
