# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.system import IteratorAggregateInterface;
from pymfony.component.system import CountableInterface;
from pymfony.component.system import clone;
from pymfony.component.system.oop import interface;
from pymfony.component.system.types import String;
from pymfony.component.system.types import Array;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.reflection import ReflectionClass;

from pymfony.component.console import Request;
from pymfony.component.console.input import InputDefinition;
from pymfony.component.console.input import InputArgument;
from pymfony.component.console.input import InputOption;

from pymfony.component.console_routing.interface import RouterInterface;
from pymfony.component.console_routing.interface import LoaderInterface;

from pymfony.component.config.resource import ResourceInterface;

"""
"""

class Router(RouterInterface):
    """The Router class is(, an example of the integration of all pieces of the):
    routing system for easier use.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    COMMAND_KEY = 'command';

    def __init__(self, loader, resource, options = None):
        """Constructor.

        @param: LoaderInterface loader    A LoaderInterface instance
        @param mixed           resource   The main resource to load
        @param dict            options    A dictionary of options

        """
        if options is None:
            options = dict();
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
            'matcher_class'          : "pymfony.component.console_routing.matcher.RequestMatcher",
            'matcher_base_class'     : "pymfony.component.console_routing.matcher.RequestMatcher",
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


        return self._options[key];

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

        if None is self._collection :
            self._collection = RouteCollection(self.getDefinition());
            if self._resource:
                self._collection.addCollection(self._loader.load(
                    self._resource, self._options['resource_type']
                ));


        return self._collection;


    def matchRequest(self, request):
        assert isinstance(request, Request);

        return self.getRequestMatcher().matchRequest(request);


    def getRequestMatcher(self):
        """Gets the RequestMatcher instance associated with this Router.

        @return: RequestMatcherInterface A RequestMatcherInterface instance

        """

        if self._matcher is None:
            self._matcher = ReflectionClass(self.getOption('matcher_class')).newInstance(self.getRouteCollection());
        return self._matcher;


class Route(InputDefinition):
    """A Route describes a route and its parameters.

    @api

    """

    def __init__(self, path, description="", defaults = None, definition = None, requirements = None):
        """Constructor.

        @param: string path The path pattern to match
        @param: string description The description
        @param: dict defaults An array of default parameter values
        @param: list definition The definition list
        @param: dict requirements An array of requirements for parameters (regexes)

        @api:
        """
        if defaults is None:
            defaults = dict();

        if definition is None:
            definition = list();

        if requirements is None:
            requirements = dict();

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

    def __init__(self, definition = None):
        if definition is None:
            definition = InputDefinition();
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
