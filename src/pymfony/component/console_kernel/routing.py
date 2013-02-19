# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import json
import os
from pickle import dumps as serialize;
from pickle import loads as unserialize;

from pymfony.component.system.oop import interface
from pymfony.component.system import Object
from pymfony.component.console import Request
from pymfony.component.config.loader import LoaderInterface
from pymfony.component.system.exception import InvalidArgumentException
from pymfony.component.system import SerializableInterface
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
from pymfony.component.dependency.interface import ContainerInterface

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



class Router(RouterInterface):
    """The Router class is(, an example of the integration of all pieces of the):
    routing system for easier use.

    @author: Fabien Potencier <fabien@symfony.com>

    """




    def __init__(self, loader, resource, collection, options = dict()):
        """Constructor.

        @param: LoaderInterface loader   A LoaderInterface instance
        @param mixed           resource The main resource to load
        @param collection       RouteCollection The main resource to load
        @param dict            options  A dictionary of options

        """
        assert isinstance(options, dict);
        assert isinstance(loader, LoaderInterface);
        assert isinstance(collection, RouteCollection);

        self._matcher = None;
        # @var: RequestMatcherInterface|None

        self._loader = None;
        # @var: LoaderInterface

        self.__isLoaded = False;

        self._collection = collection;
        # @var: RouteCollection|None

        self._resource = None;
        # @var: mixed

        self._options = dict();
        # @var: array

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


    def getRouteCollection(self):
        """@inheritdoc

        """

        if not self.__isLoaded :
            try:
                self._collection.addCollection(self._loader.load(
                    self._resource, self._options['resource_type']
                ));
            except FileLoaderLoadException:
                pass;
            finally:
                self.__isLoaded = True;


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

        if not request.getFirstArgument():
            if '_default' in self._routes.all():
                route = self._routes.get('_default');
                self._handleRouteBinding(request, '_default', route);
                return self._getAttributes(route, '_default', request);

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

            if request.getFirstArgument() != route.getCommandName():
                continue;

            # bind the input against the command specific arguments/options
            status = self._handleRouteBinding(request, name, route);

            if (self.ROUTE_MATCH == status[0]) :
                return status[1];


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
        attributes.update(route.getDefaults());
        attributes.update(request.getOptions());
        attributes.update(request.getArguments());
        attributes['_route'] = name;

        return attributes;

    def _handleRouteBinding(self, request, name, route):
        """Handles specific route requirements.:

        @param: Request request The path
        @param string name     The route name
        @param Route  route    The route

        @return array The first element represents the status, the second contains additional information

        """
        assert isinstance(route, Route);
        assert isinstance(request, Request);

        try:
            request.bind(route);
        except Exception:
            return [self.REQUIREMENT_MISMATCH, None];
        else:
            return [self.REQUIREMENT_MATCH, None];




class Route(InputDefinition):
    """A Route describes a route and its parameters.

    @api

    """

    def __init__(self, commandName, parentName = "", definition=list(), description="", defaults = dict()):
        assert isinstance(definition, list);
        assert isinstance(parentName, String);


        self.__decription = None;
        # @var: string

        self.__commandName = None;
        # @var: string

        self.__defaults = None;
        # @var: dict

        self.__compiled = None;
        # @var: CompiledRoute

        self.__parentName = parentName;
        self.__parent = None;

        self.setCommandName(commandName);
        self.setDescription(description);
        self.setDefaults(defaults);

        InputDefinition.__init__(self, definition);

    def setDescription(self, description):
        self.__decription = str(description);

    def getDescription(self):
        return self.__decription;

    def getCommandName(self):
        """Returns the command name.

        @return: string The command name

        """

        return self.__commandName;


    def setCommandName(self, commandName):
        """Sets the command name.

        This method implements a fluent interface.

        @param: string commandName The command name

        @return Route The current Route instance

        """
        self.__commandName = str(commandName).strip();

        return self;

    def setParentName(self, parentName):
        assert isinstance(parentName, String);

        self.__parentName = parentName;

    def getParentName(self):
        return self.__parentName;

    def setParent(self, parent):
        if parent is not None:
            assert isinstance(parent, Route);

        self.__parent = parent;

    def getParent(self):
        return self.__parent;

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

@interface
class RouteCompilerInterface(Object):
    """RouteCompilerInterface is the interface that all RouteCompiler classes
    must implement.
    """
    def compile(self, route):
        """Compiles the current route instance.

        @param Route $route A Route instance

        @return CompiledRoute A CompiledRoute instance

        """
        assert isinstance(route, Route);


class RouteCompiler(RouteCompilerInterface):
    """RouteCompiler compiles Route instances to CompiledRoute instances.
    """
    def __init__(self, container):
        assert isinstance(container, ContainerInterface);

        self._container = container;

    def compile(self, route):
        """Compiles the current route instance.

        @param Route $route A Route instance

        @return CompiledRoute A CompiledRoute instance

        """
        assert isinstance(route, Route);

        if isinstance(route, CompiledRoute):
            return route;

        preCompiledRoute = clone(route);
        assert isinstance(preCompiledRoute, Route);

        preCompiledRoute = self.__mergeWithParent(preCompiledRoute, route);

        parent = preCompiledRoute.getParent();
        while parent:
            preCompiledRoute = self.__mergeWithParent(preCompiledRoute, parent);
            parent = preCompiledRoute.getParent();

        parent = preCompiledRoute.getParent();
        parentName = preCompiledRoute.getParentName();
        if parentName and not parent:
            return preCompiledRoute;

        compiledRoute = CompiledRoute(preCompiledRoute.getCommandName());

        compiledRoute.setArguments(preCompiledRoute.getArguments());
        compiledRoute.setDefaults(preCompiledRoute.getDefaults());
        compiledRoute.setDescription(preCompiledRoute.getDescription());
        compiledRoute.setOptions(preCompiledRoute.getOptions());
        compiledRoute.setParent(preCompiledRoute.getParent());
        compiledRoute.setParentName(preCompiledRoute.getParentName());

        compiledRoute = self.__finalize(compiledRoute);


        return compiledRoute;

    def __mergeWithParent(self, route, parent):
        assert isinstance(route, Route);
        assert isinstance(parent, InputDefinition);

        currentArguments = route.getArguments();
        route.setArguments(parent.getArguments());
        route.addArguments(currentArguments);

        route.addOptions(parent.getOptions());

        return route;

    def __finalize(self, route):
        return self.__mergeWithParent(route, self._container.get('console_kernel').getDefinition());

class CompiledRoute(Route):
    """CompiledRoutes are returned by the RouteCompiler class.
    """
    pass;


class RouteCollection(IteratorAggregateInterface, CountableInterface):
    """A RouteCollection represents a set of Route instances.

    When adding a route at the end of the collection, an existing route
    with the same name is removed first. So there can only be one route
    with a given name.

    @author: Fabien Potencier <fabien@symfony.com>
    @author Tobias Schultze <http://tobion.de>

    @api

    """

    def __init__(self):

        self.__routes = Array();
        # @var: Route[]

        self.__resources = list();
        # @var: array


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

        route.setParent(self.get(route.getParentName()));

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

        For BC it's also removed from the root, which will not be the case in 2.3
        as the RouteCollection won't be a tree structure.

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

        # we need to remove all routes with the same names first because just replacing them
        # would not place the new route at the end of the merged array
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


class CompliedRouteCollection(RouteCollection):
    def __init__(self, compiler):
        assert isinstance(compiler, RouteCompilerInterface);

        self.__compiler = compiler;
        # @var: RouteCompilerInterface

        RouteCollection.__init__(self);

    def add(self, name, route):
        assert isinstance(route, Route);

        route.setParent(self.get(route.getParentName()));

        compiledRoute = self.__compiler.compile(route);

        RouteCollection.add(self, name, compiledRoute);


class JsonFileLoader(FileLoader):
    """JsonFileLoader loads Yaml routing files.

    @author: Fabien Potencier <fabien@symfony.com>
    @author Tobias Schultze <http://tobion.de>

    @api

    """
    # TODO: pymfony/component/console/test/Fixtures/definition_asxml.txt
    __availableKeys = [
        'resource',
        'type',
        'prefix',
        'pattern',
        'path',
        'defaults',
        'requirements',
        'options',
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
        return
        path = self._locator.locate(filename);

        configs = self._parseFile(path);

        collection = RouteCollection();
        collection.addResource(FileResource(path));

        # empty file
        if (None is configs) :
            return collection;


        # not an array
        if not isinstance(configs, dict) :
            raise InvalidArgumentException(
                'The file "{0}" must contain a Json array.'.format(path)
            );


        for name, config in configs.items():
            if 'pattern' in config :
                if 'path' in config :
                    raise InvalidArgumentException(
                        'The file "{0}" cannot define both a "path" and a '
                        '"pattern" attribute. Use only "path".'
                        ''.format(path)
                    );


                config['path'] = config['pattern'];
                del config['pattern'];


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
        s = f.read();
        f.close();
        del f;

        try:
            result = json.loads(s);
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

        defaults = config['defaults'] if 'defaults' in config else dict();
        requirements = config['requirements'] if 'requirements' in config else dict();
        options = config['options'] if 'options' in config else dict();

        route = Route(config['path'], defaults, requirements, options);

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
        options = config['options'] if 'options' in config else dict();

        self.setCurrentDir(os.path.dirname(path));

        subCollection = self.imports(config['resource'], resource_type, False, filename);
        subCollection.addPrefix(prefix);
        # @var subCollection RouteCollection

        subCollection.addDefaults(defaults);
        subCollection.addRequirements(requirements);
        subCollection.addOptions(options);

        collection.addCollection(subCollection);


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
                'The definition of "{0}" in "{1}" must be a Json array.'
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
                '", "'.joihn(self.availableKeys),
            ));

        if 'resource' in config and 'path' in config :
            raise InvalidArgumentException(
                'The routing file "{0}" must not specify both the "resource" '
                'key and the "path" key for "{1}". Choose between an import '
                'and a route definition.'.format(
                path, name
            ));

        if 'resource' not in config and 'type' in config :
            raise InvalidArgumentException(
                'The "type" key for the route definition "{0}" in "{1}" is '
                'unsupported. It is only available for imports in combination '
                'with the "resource" key.'.format(
                name, path
            ));

        if 'resource' not in config and  'path' not in config :
            raise InvalidArgumentException(
                'You must define a "path" for the route "{0}" in file "{1}".'
                ''.format(name, path
            ));
