# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import sys;
if sys.version_info[0] >= 3:
    basestring = str;
    from configparser import ConfigParser;
else:
    from ConfigParser import ConfigParser;

import os.path;
import json;

from pymfony.component.system import abstract;
from pymfony.component.config import FileLocatorInterface;
from pymfony.component.config.loader import FileLoader as BaseFileLoader;
from pymfony.component.config.resource import FileResource;

from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency import Definition;
from pymfony.component.dependency import Reference;
from pymfony.component.dependency.exception import InvalidArgumentException;

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

        self.__parseImports(content, path);

        self.__parseParameters(content);

    def supports(self, resource, resourceType=None):
        if isinstance(resource, basestring):
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
                'The "%s" file is not valid.'.format(filename)
            );

        for section in cfgParser.sections():
            content[section] = dict();
            for key, value in cfgParser.items(section):
                content[section][key] = value;
        return content;

    def __parseImports(self, content, path):
        if 'imports' not in content:
            return;

        for imports in content['imports']:
            self.setCurrentDir(os.path.dirname(path));
            self.imports(imports, None, 'ignore_error' in imports, path);


    def __parseParameters(self, content):
        if 'parameters' in content:
            for key, value in dict(content['parameters']).items():
                self._container.setParameter(key, value);


class JsonFileLoader(FileLoader):
    """JsonFileLoader loads parameters from JSON files."""

    def load(self, resource, resourceType=None):
        path = self._locator.locate(resource);

        self._container.addResource(FileResource(path));

        content = self._parseFile(path);

        if not content:
            return;

        # imports
        self.__parseImports(content, path);

        # parameters
        self.__parseParameters(content);

        # extensions
        self.__loadFromExtensions(content);

        # services
        self.__parseDefinitions(content, path);

    def supports(self, resource, resourceType=None):
        if isinstance(resource, basestring):
            if os.path.basename(resource).endswith(".json"):
                return True;
        return False;

    def _parseFile(self, filename):
        """Parses a JSON file.

        @param filename: string The path file

        @return: dict The file content

        @raise InvalidArgumentException: When JSON file is not valid
        """
        f = open(filename);
        s = f.read();
        f.close();
        del f;

        try:
            result = json.loads(s);
        except ValueError as e:
            raise InvalidArgumentException(e);

        return self.__validate(result, filename);

    def __validate(self, content, path):
        if content is None:
            return;

        if not isinstance(content, dict):
            raise InvalidArgumentException(
                'The "{0}" file is not valid.'
                ''.format(path)
            );

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
                        path,
                        '", "'.join(extensionNamespaces)
                ));

        return content;

    def __parseImports(self, content, path):
        if 'imports' not in content:
            return;

        for imports in content['imports']:
            self.setCurrentDir(os.path.dirname(path));
            self.imports(imports, None, 'ignore_error' in imports, path);


    def __parseParameters(self, content):
        if not 'parameters' in content:
            return;

        for key, value in content['parameters'].items():
            self._container.setParameter(key, value);


    def __parseDefinitions(self, content, path):
        if not 'services' in content:
            return;

        for identifier, service in content['services'].items():
            self.__parseDefinition(identifier, service, path);

    def __parseDefinition(self, identifier, service, path):
        definition = Definition();

        if 'class' in service:
            definition.setClass(service['class']);
        if 'arguments' in service:
            definition.setArguments(
                self.__resolveServices(service['arguments'])
            );
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
        if 'properties' in service:
            definition.setProperties(
                self.__resolveServices(service['properties'])
            );
        if 'configurator' in service:
            if isinstance(service['configurator'], basestring):
                definition.setConfigurator(service['configurator']);
            else:
                definition.setConfigurator([
                    self.__resolveServices(service['configurator'])[0],
                    service['configurator'][1]
                ]);
        if 'calls' in service:
            for call in service['calls']:
                if len(call) == 2:
                    args = self.__resolveServices(call[1]);
                else:
                    args = list();
                definition.addMethodCall(call[0], args);
        if 'tags' in service:
            if not isinstance(service['tags'], list):
                raise InvalidArgumentException(
                    'Parameter "tags" must be an array for service '
                    '"{0}" in {1}.'.format(identifier, path)
                );

            for tag in service['tags']:
                if not isinstance(tag, dict) and 'name' in tag:
                    raise InvalidArgumentException(
                        'A "tags" entry is missing a "name" key for service '
                        '"{0}" in {1}.'.format(identifier, path)
                    );

                name = tag['name'];
                del tag['name'];

                for attributes, value in tag.items():
                    if not isinstance(
                        value,
                        (type(None),basestring,int,float,bool)
                        ):
                        raise InvalidArgumentException(
                            'A "tags" attribute must be of a scalar-type '
                            'for service "{0}", tag "{1}" in {2}.'
                            ''.format(identifier, name, path)
                        );

                definition.addTag(name, tag);

        self._container.setDefinition(identifier, definition);

    def __resolveServices(self, value):
        if isinstance(value, list):
            value = list(map(self.__resolveServices, value));
        if isinstance(value, basestring) and value.startswith("@"):
            value = value[1:];
            if value.endswith("="):
                value = value[:-1];
                strict = False;
            else:
                strict = True;
            value = Reference(value, strict);

        return value;


    def __loadFromExtensions(self, content):
        """Loads from Extensions
     *
     * @param array content

        """
        assert isinstance(content, dict);

        for namespace, values in content.items():
            if namespace in ['imports', 'parameters', 'services']:
                continue;

            if not isinstance(values, (list, dict)) :
                values = {};

            self._container.loadFromExtension(namespace, values);
