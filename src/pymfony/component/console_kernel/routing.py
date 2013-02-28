# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import os
import re

from pymfony.component.system.oop import interface
from pymfony.component.system import Object
from pymfony.component.console import Request
from pymfony.component.config.loader import LoaderInterface as BaseLoaderInterface
from pymfony.component.system.exception import InvalidArgumentException
from pymfony.component.system.types import String
from pymfony.component.system import CountableInterface
from pymfony.component.system import IteratorAggregateInterface
from pymfony.component.system import clone
from pymfony.component.config.resource import FileResource
from pymfony.component.console_kernel.exception import NotFoundConsoleException
from pymfony.component.system.types import Array
from pymfony.component.config.loader import FileLoader
from pymfony.component.config.resource import ResourceInterface
from pymfony.component.console.input import InputDefinition
from pymfony.component.console.input import InputArgument
from pymfony.component.console.input import InputOption
from pymfony.component.config.exception import FileLoaderLoadException
from pymfony.component.system.json import JSONDecoderOrderedDict
from pymfony.component.system.types import OrderedDict

"""
"""


@interface
class RequestMatcherInterface(Object):
    """RequestMatcherInterface is the interface that all request matcher classes must implement.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    def matchRequest(self, request):
        """Tries to match a request with a set of routes.

        If the matcher can not find information, it must raise one of the exceptions documented
        below.

        @param: Request request The request to match

        @return dict An array of parameters

        @raise ResourceNotFoundException If no matching resource could be found
        @raise MethodNotAllowedException If a matching resource was found but the request method is not allowed

        """
        assert isinstance(request, Request);


@interface
class RouterInterface(RequestMatcherInterface):
    """RouterInterface is the interface that all Router classes must implement.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    def getRouteCollection(self):
        """Gets the RouteCollection instance associated with this Router.

        @return: RouteCollection A RouteCollection instance

        """

@interface
class LoaderInterface(BaseLoaderInterface):
    def load(self, resource, resourceType=None):
        """Loads a resource.

        @param resource: mixed
        @param resourceType: string The resource type

        @return: RouteCollection
        """
        pass

class Router(RouterInterface):
    """The Router class is(, an example of the integration of all pieces of the):
    routing system for easier use.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    COMMAND_KEY = 'command';

    def __init__(self, loader, resource, options = dict()):
        """Constructor.

        @param: LoaderInterface loader    A LoaderInterface instance
        @param mixed           resource   The main resource to load
        @param dict            options    A dictionary of options

        """
        assert isinstance(loader, LoaderInterface);
        assert isinstance(options, dict);

        self._matcher = None;  # @var: RequestMatcherInterface|None
        self._loader = None; # @var: LoaderInterface
        self.__isLoaded = False;
        self._collection = None; # @var: RouteCollection|None
        self._resource = None; # @var: mixed
        self._options = dict(); # @var: dict
        self.__definition = None; # @var InputDefinition

        self._loader = loader;
        self._resource = resource;
        self.setOptions(options);


    def setOptions(self, options):
        """Sets options.

        Available options:

             cache_dir:     The cache directory (or None to disable caching)
             debug:         Whether to enable debugging or not (False by default)
             resource_type: Type hint for the main resource (optional)

        @param: array options An array of options

        @raise InvalidArgumentException When unsupported option is provided

        """
        assert isinstance(options, dict);

        self._options = {
            'resource_type'          : None,
        };

        # check option names and live merge, if errors are encountered Exception will be thrown:
        invalid = list();
        for key, value in options.items():
            if key in self._options :
                self._options[key] = value;
            else :
                invalid.append(key);



        if (invalid) :
            raise InvalidArgumentException(
                'The Router does not support the following options: "{0}".'
                ''.format('\', \''.join(invalid)
            ));



    def setOption(self, key, value):
        """Sets an option.

        @param: string key   The key
        @param mixed  value The value

        @raise InvalidArgumentException

        """

        if key not in self._options :
            raise InvalidArgumentException(
                'The Router does not support the "{0}" option.'.format(
                    key
            ));


        self._options[key] = value;


    def getOption(self, key):
        """Gets an option value.

        @param: string key The key

        @return mixed The value

        @raise InvalidArgumentException

        """

        if key not in self._options :
            raise InvalidArgumentException(
                'The Router does not support the "{0}" option.'.format(
                    key
            ));


        return self.options[key];

    def getDefinition(self):
        """Gets the default input definition.

        @return InputDefinition An InputDefinition instance

        """
        if self.__definition is None:
            self.__definition = InputDefinition([
                InputArgument(self.COMMAND_KEY, InputArgument.REQUIRED, 'The command to execute'),

                InputOption('--help', '-h', InputOption.VALUE_NONE, 'Display this help message.'),
                InputOption('--quiet', '-q', InputOption.VALUE_NONE, 'Do not output any message.'),
                InputOption('--verbose', '-v', InputOption.VALUE_NONE, 'Increase verbosity of messages.'),
                InputOption('--version', '-V', InputOption.VALUE_NONE, 'Display this application version.'),
                InputOption('--ansi', '', InputOption.VALUE_NONE, 'Force ANSI output.'),
                InputOption('--no-ansi', '', InputOption.VALUE_NONE, 'Disable ANSI output.'),
                InputOption('--no-interaction', '-n', InputOption.VALUE_NONE, 'Do not ask any interactive question.'),
            ]);

        return self.__definition;

    def getRouteCollection(self):
        """@inheritdoc

        """

        if None is self._collection :
            self._collection = RouteCollection(self.getDefinition());
            if self._resource:
                self._collection.addCollection(self._loader.load(
                    self._resource, self._options['resource_type']
                ));


        return self._collection;


    def matchRequest(self, request):
        """@inheritdoc}

        """
        assert isinstance(request, Request);

        return self.getRequestMatcher().matchRequest(request);


    def getRequestMatcher(self):
        """Gets the UrlMatcher instance associated with this Router.

        @return: RequestMatcherInterface A RequestMatcherInterface instance

        """

        if self._matcher is None:
            self._matcher = RequestMatcher(self.getRouteCollection());
        return self._matcher;


class RequestMatcher(RequestMatcherInterface):
    """RequestMatcher matches Request based on a set of routes.

    @author: Fabien Potencier <fabien@symfony.com>

    @api

    """

    REQUIREMENT_MATCH     = 0;
    REQUIREMENT_MISMATCH  = 1;
    ROUTE_MATCH           = 2;
    BIND_MISMATCH         = 3;
    BIND_MATCH            = 4;

    def __init__(self, routes):
        """Constructor.

        @param: RouteCollection routes  A RouteCollection instance

        @api

        """
        assert isinstance(routes, RouteCollection);

        self._routes = None;
        # @var: RouteCollection

        self._routes = routes;


    def matchRequest(self, request):
        """@inheritdoc}

        """
        assert isinstance(request, Request);

        ret = self._matchCollection(request, self._routes)
        if (ret) :
            return ret;

        raise NotFoundConsoleException();


    def _matchCollection(self, request, routes):
        """Tries to match a request with a set of routes.

        @param: Request          request The path info to be parsed
        @param RouteCollection routes   The set of routes

        @return dict An array of parameters

        @raise ResourceNotFoundException If the resource could not be found
        @raise MethodNotAllowedException If the resource was found but the request method is not allowed

        """
        assert isinstance(routes, RouteCollection);
        assert isinstance(request, Request);

        for name, route in routes.all().items():
            assert isinstance(route, Route);

            # bind the input against the command specific arguments/options
            status = self._handleRouteBinds(request, name, route);

            if (self.BIND_MISMATCH == status[0]) :
                continue;

            if request.hasArgument(Router.COMMAND_KEY):
                if request.getArgument(Router.COMMAND_KEY) != route.getPath():
                    continue;

            status = self._handleRouteRequirements(request, name, route);

            if (self.REQUIREMENT_MISMATCH == status[0]) :
                continue;


            return self._getAttributes(route, name, request);



    def _getAttributes(self, route, name, request):
        """Returns an array of values to use as request attributes.

        As this method requires the Route object, it is not available
        in matchers that do not have access to the matched Route instance
        (like the PHP and Apache matcher dumpers).

        @param: Route  route      The route we are matching against
        @param string name       The name of the route
        @param: Request          request The path info to be parsed

        @return dict An array of parameters

        """
        assert isinstance(route, Route);
        assert isinstance(request, Request);

        attributes = dict();
        attributes['_route'] = name;
        attributes.update(request.getArguments());

        return attributes;

    def _handleRouteBinds(self, request, name, route):
        """Handles specific route binding.:

        @param: Request request The path
        @param string name     The route name
        @param Route  route    The route

        @return list The first element represents the status, the second contains additional information

        """
        assert isinstance(route, Route);
        assert isinstance(request, Request);

        try:
            request.bind(route);
            request.validate();
        except Exception:
            return [self.BIND_MISMATCH, None];
        else:
            return [self.BIND_MATCH, None];


    def _handleRouteRequirements(self, request, name, route):
        """Handles specific route requirements.:

        @param: Request request The path
        @param string name     The route name
        @param Route  route    The route

        @return list The first element represents the status, the second contains additional information

        """
        assert isinstance(route, Route);
        assert isinstance(request, Request);

        for key, regexp in route.getRequirements().items():
            if not re.match(regexp, request.getArgument(key)):
                return [self.REQUIREMENT_MISMATCH, None];
            elif not re.match(regexp, request.getOption(key)):
                return [self.REQUIREMENT_MISMATCH, None];
            else:
                return [self.REQUIREMENT_MISMATCH, None];

        return [self.REQUIREMENT_MATCH, None];



class Route(InputDefinition):
    """A Route describes a route and its parameters.

    @api

    """

    def __init__(self, path, description="", defaults = dict(), definition = list(), requirements = dict()):
        """Constructor.

        @param: string path The path pattern to match
        @param: string description The description
        @param: dict defaults An array of default parameter values
        @param: list definition The definition list
        @param: dict requirements An array of requirements for parameters (regexes)

        @api:
        """
        assert isinstance(path, String);
        assert isinstance(description, String);
        assert isinstance(defaults, dict);
        assert isinstance(definition, list);
        assert isinstance(requirements, dict);

        self.__path = None; # @var: string
        self.__defaults = None; # @var: dict
        self.__requirements = None; # @var: dict
        self.__decription = None; # @var: string
        self.__synopsis = None; # @var: string


        self.setPath(path);
        self.setDefaults(defaults);
        self.setRequirements(requirements);
        self.setDescription(description);

        InputDefinition.__init__(self, definition);

    def getPath(self):
        """Returns the path.

        @return: string The path

        """
        return self.__path;

    def setPath(self, path):
        """Sets the path of the input.

        This method implements a fluent interface.

        @param string path The path

        @return Route The current Route instance

        @api
        """
        assert isinstance(path, String);

        self.__path = str(path);

        return self;

    def getDescription(self):
        """Returns the route decription.

        @return: string The route decription

        """
        return self.__decription;

    def setDescription(self, description):
        """Sets the description of the command.

        This method implements a fluent interface.

        @param string description The description

        @return Route The current Route instance

        @api
        """
        assert isinstance(description, String);

        self.__decription = str(description);

        return self;

    def setDefinition(self, definition):
        """Sets the definition of the input.

        This method implements a fluent interface.

        @param list definition The definition list

        @return Route The current Route instance

        @api
        """

        InputDefinition.setDefinition(self, definition);

        return self;


    def getDefaults(self):
        """Returns the defaults.

        @return: dict The defaults

        """

        return self.__defaults;


    def setDefaults(self, defaults):
        """Sets the defaults.

        This method implements a fluent interface.

        @param: dict defaults The defaults

        @return Route The current Route instance

        """
        assert isinstance(defaults, dict);

        self.__defaults = dict();

        return self.addDefaults(defaults);


    def addDefaults(self, defaults):
        """Adds defaults.

        This method implements a fluent interface.

        @param: dict defaults The defaults

        @return Route The current Route instance

        """
        assert isinstance(defaults, dict);

        for name, default in defaults.items():
            self.__defaults[name] = default;

        return self;


    def getDefault(self, name):
        """Gets a default value.

        @param: string name A variable name

        @return mixed The default value or None when not given

        """

        return self.__defaults[name] if name in self.__defaults  else None;


    def hasDefault(self, name):
        """Checks if a default value is set for the given variable.:

        @param: string name A variable name

        @return Boolean True if the default value is set, False otherwise:

        """

        return name in self.__defaults;


    def setDefault(self, name, default):
        """Sets a default value.

        @param: string name    A variable name
        @param mixed  default The default value

        @return Route The current Route instance

        @api

        """

        self.__defaults[name] = default;

        return self;

    def getRequirements(self):
        """Returns the requirements.

        @return: array The requirements

        """

        return self.__requirements;


    def setRequirements(self, requirements):
        """Sets the requirements.

        This method implements a fluent interface.

        @param: array requirements The requirements

        @return Route The current Route instance

        """
        assert isinstance(requirements, dict);

        self.__requirements = dict();

        return self.addRequirements(requirements);


    def addRequirements(self, requirements):
        """Adds requirements.

        This method implements a fluent interface.

        @param: array requirements The requirements

        @return Route The current Route instance

        """
        assert isinstance(requirements, dict);

        for key, regex in requirements.items():
            self.setRequirement(key, regex);

        return self;


    def getRequirement(self, key):
        """Returns the requirement for the given key.

        @param: string key The key

        @return string|None The regex or None when not given

        """

        return self.__requirements[key] if key in self.__requirements else None;


    def hasRequirement(self, key):
        """Checks if a requirement is set for the given key.:

        @param: string key A variable name

        @return Boolean True if a requirement is specified, False otherwise:

        """

        return key in self.__requirements.keys();


    def setRequirement(self, key, regex):
        """Sets a requirement for the given key.

        @param: string key   The key
        @param string regex The regex

        @return Route The current Route instance

        @api

        """

        self.__requirements[key] = self.__sanitizeRequirement(key, regex);

        return self;

    def getSynopsis(self):
        """Returns the synopsis for the command.

        @return: string The synopsis

        """

        if None is self.__synopsis:
            self.__synopsis = InputDefinition.getSynopsis(self);

        return self.__synopsis;


    def __sanitizeRequirement(self, key, regex):

        if not isinstance(regex, String) :
            raise InvalidArgumentException(
                'Routing requirement for "{0}" must be a string.'.format(key)
            );


        if regex and regex.startswith('^') :
            regex = regex[1:]; # returns False for a single character


        if regex.endswith('$') :
            regex = regex[:-1];


        if not regex :
            raise InvalidArgumentException(
                'Routing requirement for "{0}" cannot be empty.'.format(key)
            );

        return regex;



class RouteCollection(IteratorAggregateInterface, CountableInterface):
    """A RouteCollection represents a set of Route instances.

    When adding a route at the end of the collection, an existing route
    with the same name is removed first. So there can only be one route
    with a given name.

    @author: Fabien Potencier <fabien@symfony.com>
    @author Tobias Schultze <http://tobion.de>

    @api

    """

    def __init__(self, definition = InputDefinition()):
        assert isinstance(definition, InputDefinition);

        self.__routes = Array(); # @var: Route[]

        self.__resources = list(); # @var: list

        self.__definition = definition; # @var: InputDefinition


    def __clone__(self):

        for name, route in self.__routes.items():
            self.__routes[name] = clone(route);


    def __iter__(self):
        """Gets the current RouteCollection as an Iterator that includes all routes.

        It implements IteratorAggregate.

        @see: all()

        @return ArrayIterator An ArrayIterator object for iterating over routes

        """

        return self.__routes.__iter__();


    def __len__(self):
        """Gets the number of Routes in this collection.

        @return: int The number of routes

        """

        return len(self.__routes);


    def add(self, name, route):
        """Adds a route.

        @param: string name  The route name
        @param Route  route A Route instance

        @api

        """
        assert isinstance(route, Route);

        self.__routes.pop(name, None);

        # Force the creation of the synopsis before the merge with
        # the collection definition
        route.getSynopsis();

        self.__mergeDefinition(route, self.__definition);

        self.__routes[name] = route;


    def all(self):
        """Returns all routes in this collection.

        @return: Route[] An array of routes

        """

        return self.__routes;


    def get(self, name):
        """Gets a route by name.

        @param: string name The route name

        @return Route|None A Route instance or None when not found

        """

        return self.__routes[name] if name in self.__routes else None;


    def remove(self, name):
        """Removes a route or an array of routes by name from the collection

        @param: string|list name The route name or an array of route names

        """

        if not isinstance(name, list):
            name = [name];

        for n in name:
            self.__routes.pop(n, None);



    def addCollection(self, collection):
        """Adds a route collection at the end of the current set by appending all
        routes of the added collection.

        @param: RouteCollection collection      A RouteCollection instance

        @api

        """
        assert isinstance(collection, RouteCollection);

        for name, route in collection.all().items():
            self.add(name, route);


        self.__resources = self.__resources + collection.getResources();


    def getResources(self):
        """Returns an array of resources loaded to build this collection.

        @return: ResourceInterface[] An array of resources

        """

        return Array.uniq(self.__resources);


    def addResource(self, resource):
        """Adds a resource for this collection.

        @param: ResourceInterface resource A resource instance

        """
        assert isinstance(resource, ResourceInterface);

        self.__resources.append(resource);


    def getDefinition(self):
        """Returns the definition of this collection.

        @return: InputDefinition The InputDefinition of this collection

        """

        return self.__definition;

    def setDefinition(self, definition):
        """Sets the definition of this collection.

        @param: InputDefinition definition A resource instance

        """
        assert isinstance(definition, InputDefinition);

        self.__definition = definition;


    def prependDefinition(self, definition):
        """Prepends a definition to the definition of all child routes.

        @param: InputDefinition  definition   A definition to prepend
        """
        assert isinstance(definition, InputDefinition);

        self.__mergeDefinition(self.__definition, definition);

        for route in self.__routes.values():
            self.__mergeDefinition(route, definition);


    def addPrefix(self, prefix):
        """Adds a prefix to the path of all child routes.

        @param: string prefix       An optional prefix to add before each pattern of the route collection

        @api

        """

        prefix = prefix.strip().strip(':');

        if not prefix :
            return;

        for route in self.__routes.values():
            route.setPath(prefix + ':' + route.getPath());


    def addDefaults(self, defaults):
        """Adds defaults to all routes.

        An existing default value under the same name in a route will be overridden.

        @param: dict defaults An array of default values

        """
        assert isinstance(defaults, dict);

        if defaults :
            for route in self.__routes.values():
                route.addDefaults(defaults);



    def addRequirements(self, requirements):
        """Adds requirements to all routes.

        An existing requirement under the same name in a route will be overridden.

        @param: dict requirements An array of requirements

        """
        assert isinstance(requirements, dict);

        if requirements :
            for route in self.__routes.values():
                route.addRequirements(requirements);

    def __mergeDefinition(self, definition, parentDefinition):
        """Merges the definition with the parentDefinition.

        @param: InputDefinition  definition        Initial definition to merge
        @param: InputDefinition  parentDefinition  A definition from merge

        @return: RouteCollection The current instance
        """
        assert isinstance(definition, InputDefinition);
        assert isinstance(parentDefinition, InputDefinition);

        currentArguments = definition.getArguments();
        definition.setArguments(parentDefinition.getArguments());
        definition.addArguments(currentArguments);

        definition.addOptions(parentDefinition.getOptions());

        return self;

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
