# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import os;

from pymfony.component.system.types import OrderedDict;
from pymfony.component.system.types import Array;
from pymfony.component.system.types import String;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.json import JSONDecoderOrderedDict;

from pymfony.component.config.loader import FileLoader;
from pymfony.component.config.resource import FileResource;

from pymfony.component.console.input import InputDefinition;
from pymfony.component.console.input import InputArgument;
from pymfony.component.console.input import InputOption;

from pymfony.component.console_routing import RouteCollection;
from pymfony.component.console_routing import Route;
from pymfony.component.console_routing.interface import LoaderInterface;

"""
"""

class JsonFileLoader(FileLoader, LoaderInterface):
    """JsonFileLoader loads Json routing files.

    @author: Fabien Potencier <fabien@symfony.com>
    @author Tobias Schultze <http://tobion.de>

    @api

    """
    __availableKeys = [
        'defaults',
        'definition',
        'requirements',

        'resource',
        'type',
        'prefix',

        'path',
        'description',
    ];

    def load(self, filename, resource_type = None):
        """Loads a Yaml file.

        @param: string      file A Yaml file path
        @param string|None resource_type The resource type

        @return RouteCollection A RouteCollection instance

        @raise InvalidArgumentException When a route can't be parsed because YAML is invalid

        @api

        """

        path = self._locator.locate(filename);

        configs = self._parseFile(path);

        collection = RouteCollection();
        collection.addResource(FileResource(path));

        # empty file
        if (None is configs) :
            return collection;


        # not a OrderedDict
        if not isinstance(configs, OrderedDict) :
            raise InvalidArgumentException(
                'The file "{0}" must contain a Json object.'.format(path)
            );


        for name, config in configs.items():

            self._validate(config, name, path);

            if 'resource' in config :
                self._parseImport(collection, config, path, filename);
            else :
                self._parseRoute(collection, name, config, path);


        return collection;


    def supports(self, resource, resource_type = None):
        """@inheritdoc

        @api

        """
        if isinstance(resource, String):
            if os.path.basename(resource).endswith(".json"):
                if resource_type is None or resource_type == "json":
                    return True;
        return False;

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
            return OrderedDict();

        try:
            result = JSONDecoderOrderedDict().decode(s);
        except ValueError as e:
            raise InvalidArgumentException(e);

        return result;


    def _parseRoute(self, collection, name, config, path):
        """Parses a route and adds it to the RouteCollection.

        @param: RouteCollection collection A RouteCollection instance
        @param string          name       Route name
        @param dict           config     Route definition
        @param string          path       Full path of the YAML file being processed

        """
        assert isinstance(config, dict);
        assert isinstance(collection, RouteCollection);

        description = config['description'] if 'description' in config else '';
        defaults = config['defaults'] if 'defaults' in config else dict();
        requirements = config['requirements'] if 'requirements' in config else dict();
        definition = self._parseDefinition(config['definition'], defaults) if 'definition' in config else list();

        route = Route(config['path'], description, defaults, definition, requirements);

        collection.add(name, route);


    def _parseImport(self, collection, config, path, filename):
        """Parses an import and adds the routes in the resource to the RouteCollection.

        @param: RouteCollection collection A RouteCollection instance
        @param dict           config     Route definition
        @param string          path       Full path of the YAML file being processed
        @param string          file       Loaded file name

        """
        assert isinstance(config, dict);
        assert isinstance(collection, RouteCollection);

        resource_type = config['type'] if 'type' in config else None;
        prefix = config['prefix'] if 'prefix' in config else '';
        defaults = config['defaults'] if 'defaults' in config else dict();
        requirements = config['requirements'] if 'requirements' in config else dict();
        definition = self._parseDefinition(config['definition'], defaults) if 'definition' in config else list();

        self.setCurrentDir(os.path.dirname(path));

        subCollection = self.imports(config['resource'], resource_type, False, filename);
        assert isinstance(subCollection, RouteCollection);
        # @var subCollection RouteCollection

        subCollection.addPrefix(prefix);
        subCollection.prependDefinition(InputDefinition(definition));
        subCollection.addDefaults(defaults);
        subCollection.addRequirements(requirements);

        collection.addCollection(subCollection);

    def _parseDefinition(self, definition, defaults):
        definitionList = list();
        if 'arguments' in definition:
            for name, argument in definition['arguments'].items():
                mode = InputArgument.OPTIONAL if name in defaults else InputArgument.REQUIRED;
                mode = mode | InputArgument.IS_ARRAY if 'is_array' in argument and argument['is_array'] is True else mode;
                description = argument['description'] if 'description' in argument else "";
                default = defaults[name] if name in defaults else None;

                definitionList.append(InputArgument(name, mode, description, default));

        if 'options' in definition:
            for name, option in definition['options'].items():
                shortcut = option['shortcut'] if 'shortcut' in option else None;
                mode = InputOption.VALUE_OPTIONAL if name in defaults else InputOption.VALUE_REQUIRED;
                mode = mode | InputOption.VALUE_IS_ARRAY if 'is_array' in option and option['is_array'] is True else mode;
                mode = InputOption.VALUE_NONE if not ('accept_value' in option and option['accept_value'] is True) else mode;
                description = option['description'] if 'description' in option else "";
                default = defaults[name] if name in defaults else None;

                definitionList.append(InputOption(name, shortcut, mode, description, default));

        return definitionList;


    def _validate(self, config, name, path):
        """Validates the route configuration.

        @param: dict  config A resource config
        @param string name   The config key
        @param string path   The loaded file path

        @raise InvalidArgumentException If one of the provided config keys is not supported,
                                          something is missing or the combination is nonsense

        """

        if not isinstance(config, dict) :
            raise InvalidArgumentException(
                'The definition of "{0}" in "{1}" must be a Json object.'
                ''.format(name, path)
            );

        extraKeys = Array.diff(config.keys(), self.__availableKeys);
        if (extraKeys) :
            raise InvalidArgumentException(
                'The routing file "{0}" contains unsupported keys for "{1}": '
                '"{2}". Expected one of: "{3}".'.format(
                path,
                name,
                '", "'.join(extraKeys),
                '", "'.join(self.__availableKeys),
            ));

        if 'resource' in config and 'path' in config :
            raise InvalidArgumentException(
                'The routing file "{0}" must not specify both the "resource" '
                'key and the "path" key for "{1}". Choose between an import '
                'and a route definition.'.format(
                path, name
            ));

        if 'resource' in config and 'description' in config :
            raise InvalidArgumentException(
                'The routing file "{0}" must not specify both the "resource" '
                'key and the "description" key for "{1}". Choose between an '
                'import and a route definition.'.format(
                path, name
            ));

        if 'resource' not in config and 'type' in config :
            raise InvalidArgumentException(
                'The "type" key for the route definition "{0}" in "{1}" is '
                'unsupported. It is only available for imports in combination '
                'with the "resource" key.'.format(
                name, path
            ));

        if 'resource' not in config and 'path' not in config :
            raise InvalidArgumentException(
                'You must define a "path" for the route "{0}" in file "{1}".'
                ''.format(name, path)
            );

        if 'definition' in config:
            if 'arguments' in config['definition']:
                if not isinstance(config['definition']['arguments'], OrderedDict):
                    raise InvalidArgumentException(
                        'The definition.arguments key should be a JSON object '
                        'in route "{0}" in file "{1}".'
                        ''.format(name, path)
                    );
            if 'options' in config['definition']:
                if not isinstance(config['definition']['options'], dict):
                    raise InvalidArgumentException(
                        'The definition.options key should be a JSON object '
                        'in route "{0}" in file "{1}".'
                        ''.format(name, path)
                    );
