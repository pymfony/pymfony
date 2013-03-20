# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import re;

from pymfony.component.system import ClassLoader;
from pymfony.component.system import Object;
from pymfony.component.system import Tool;
from pymfony.component.system import SourceFileLoader;
from pymfony.component.system.oop import abstract;
from pymfony.component.system.reflection import ReflectionObject;
from pymfony.component.system.types import OrderedDict;
from pymfony.component.system.types import Array;

from pymfony.component.config.resource import FileResource;
from pymfony.component.config.resource import ResourceInterface;

from pymfony.component.dependency.interface import ScopeInterface;
from pymfony.component.dependency.interface import ContainerInterface;
from pymfony.component.dependency.interface import IntrospectableContainerInterface;
from pymfony.component.dependency.interface import ContainerAwareInterface;
from pymfony.component.dependency.interface import TaggedContainerInterface;
from pymfony.component.dependency.interface import ExtensionInterface;
from pymfony.component.dependency.definition import Alias;
from pymfony.component.dependency.definition import Definition;
from pymfony.component.dependency.definition import Reference;
from pymfony.component.dependency.exception import BadMethodCallException;
from pymfony.component.dependency.exception import ServiceNotFoundException;
from pymfony.component.dependency.exception import InvalidArgumentException;
from pymfony.component.dependency.exception import LogicException;
from pymfony.component.dependency.exception import RuntimeException;
from pymfony.component.dependency.exception import ServiceCircularReferenceException
from pymfony.component.dependency.parameterbag import ParameterBag;
from pymfony.component.dependency.parameterbag import ParameterBagInterface;
from pymfony.component.dependency.parameterbag import FrozenParameterBag;
from pymfony.component.dependency.compiler import PassConfig;
from pymfony.component.dependency.compiler import Compiler;
from pymfony.component.dependency.interface import CompilerPassInterface;
"""
"""

class Scope(ScopeInterface):
    """Scope class.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    @api:

    """


    def __init__(self, name, parentName = ContainerInterface.SCOPE_CONTAINER):
        """
        @api:

        """

        self.__name = None;
        self.__parentName = None;

        self.__name = name;
        self.__parentName = parentName;


    def getName(self):
        """
        @api:

        """

        return self.__name;


    def getParentName(self):
        """
        @api:

        """

        return self.__parentName;


@abstract
class ContainerAware(ContainerAwareInterface):
    def __init__(self):
        self._container = None;

    def setContainer(self, container = None):
        assert isinstance(container, (ContainerInterface, type(None)));

        self._container = container;


class Container(IntrospectableContainerInterface):
    """Container is a dependency injection container.

    It gives access to object instances (services).

    Services and parameters are simple key/pair stores.

    Parameter and service keys are case insensitive.

    A service id can contain lowercased letters, digits, underscores, and dots.
    Underscores are used to separate words, and dots to group services
    under namespaces:

    <ul>
      <li>request</li>
      <li>mysql_session_storage</li>
      <li>symfony.mysql_session_storage</li>
    </ul>

    A service can also be defined by creating a method named
    getXXXService(), where XXX is the camelized version of the id:

    <ul>
      <li>request -> getRequestService()</li>
      <li>mysql_session_storage -> getMysqlSessionStorageService()</li>
      <li>symfony.mysql_session_storage -> getSymfony_MysqlSessionStorageService()</li>
    </ul>

    The container can have three possible behaviors when a service does not exist:

    * EXCEPTION_ON_INVALID_REFERENCE: Throws an exception (the default)
    * None_ON_INVALID_REFERENCE:      Returns None
    * IGNORE_ON_INVALID_REFERENCE:    Ignores the wrapping command asking for the reference
                                      (for instance, ignore a setter if the service does not exist):

    @author: Fabien Potencier <fabien@symfony.com>
    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    @api:

    """
    def __init__(self, parameterBag=None):
        """Constructor.

        @param: ParameterBagInterface parameterBag A ParameterBagInterface instance

        @api

        """
        self._services = dict();
        self._scopes = dict();
        self._scopeChildren = dict();
        self._scopedServices = dict();
        self._scopeStacks = dict();
        self._parameterBag = None;
        self._loading = dict();

        if parameterBag is None:
            self._parameterBag = ParameterBag();
        else:
            assert isinstance(parameterBag, ParameterBagInterface);
            self._parameterBag = parameterBag;

        self.set('service_container', self);

    def compile(self):
        """Compiles the container.

        This method does two things:

            Parameter values are resolved;
            The parameter bag is frozen.

        @api:

        """
        self._parameterBag.resolve();
        self._parameterBag = FrozenParameterBag(self._parameterBag.all());

    def isFrozen(self):
        """Returns True if the container parameter bag are frozen.:

        @return: Boolean True if the container parameter bag are frozen, False otherwise

        @api:

        """
        return isinstance(self._parameterBag, FrozenParameterBag);

    def getParameterBag(self):
        """Gets the service container parameter bag.

        @return: ParameterBagInterface A ParameterBagInterface instance

        @api

        """
        return self._parameterBag;

    def getParameter(self, name):
        """Gets a parameter.

        @param: string name The parameter name

        @return mixed  The parameter value

        @raise InvalidArgumentException if the parameter is not defined:

        @api

        """
        return self._parameterBag.get(name);

    def hasParameter(self, name):
        """Checks if a parameter exists.:

        @param: string name The parameter name

        @return Boolean The presence of parameter in container

        @api

        """
        return self._parameterBag.has(name);

    def setParameter(self, name, value):
        """Sets a parameter.

        @param: string name  The parameter name
        @param mixed  value The parameter value

        @api

        """
        self._parameterBag.set(name, value);

    def set(self, identifier, service, scope = ContainerInterface.SCOPE_CONTAINER):
        """Sets a service.

        @param: string identifier  The service identifier:
        @param object service      The service instance
        @param string scope        The scope of the service

        @raise RuntimeException When trying to set a service in an inactive scope
        @raise InvalidArgumentException When trying to set a service in the prototype scope

        @api

        """
        if (self.SCOPE_PROTOTYPE == scope) :
            raise InvalidArgumentException(
                'You cannot set service "{0}" of scope "prototype".'
                ''.format(identifier)
            );

        identifier = self._formatIdentifier(identifier);

        if (self.SCOPE_CONTAINER  != scope) :
            if not scope in self._scopedServices :
                raise RuntimeException(
                    'You cannot set service "{0}" of inactive scope.'
                    ''.format(identifier)
                );

            self._scopedServices[scope][identifier] = service;


        self._services[identifier] = service;

    def has(self, identifier):
        """Returns True if the given service is defined.:

        @param: string id The service identifier:

        @return Boolean True if the service is defined, False otherwise:

        @api

        """
        identifier = self._formatIdentifier(identifier);
        method = 'get'+identifier.replace('_', '').replace('.', '_')+'Service';
        return identifier in self._services.keys() or (hasattr(self, method) and isinstance(getattr(self, method), type(self.get)));

    def get(self, identifier, invalidBehavior = ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE):
        """Gets a service.

        If a service is defined both through a set() method and
        with a getidService() method, the former has always precedence.

        @param: string  id              The service identifier:
        @param integer invalidBehavior The behavior when the service does not exist

        @return object The associated service

        @raise InvalidArgumentException if the service is not defined:
        @raise ServiceCircularReferenceException When a circular reference is detected
        @raise ServiceNotFoundException When the service is not defined

        @see Reference

        @api

        """
        identifier = self._formatIdentifier(identifier);
        if identifier in self._services.keys():
            return self._services[identifier];

        if identifier in self._loading.keys():
            raise ServiceCircularReferenceException(identifier, self._loading.keys());

        method = 'get'+identifier.replace('_', '').replace('.', '_')+'Service';
        if (hasattr(self, method) and isinstance(getattr(self, method), type(self.get))):
            self._loading[identifier] = True;

            try:
                service = getattr(self, method)();
            except Exception as e:
                self._loading.pop(identifier, None);

                self._services.pop(identifier, None);

                raise e;

            self._loading.pop(identifier, None);

            return service;

        if (self.EXCEPTION_ON_INVALID_REFERENCE == invalidBehavior) :
            raise ServiceNotFoundException(identifier);

    def initialized(self, identifier):
        """Returns True if the given service has actually been initialized:

        @param: string id The service identifier:

        @return Boolean True if service has already been initialized, False otherwise:

        """
        identifier = self._formatIdentifier(identifier);
        return identifier in self._services;

    def getServiceIds(self):
        """Gets all service ids.

        @return: list An array of all defined service ids

        """

        ids = list();
        r = ReflectionObject(self);
        for method in r.getMethods():
            match = re.match('^get(.+)Service$', method.getName());
            if match :
                ids.append(self.underscore(match.group(1)));

        return Array.uniq(ids + list(self._services.keys()));

    def enterScope(self, name):
        """This is called when you enter a scope

        @param: string name

        @raise RuntimeException         When the parent scope is inactive
        @raise InvalidArgumentException When the scope does not exist

        @api

        """

        if name not in self._scopes :
            raise InvalidArgumentException(
                'The scope "{0}" does not exist.'.foemat(name)
            );


        if self.SCOPE_CONTAINER != self._scopes[name] and  self._scopes[name] not in self._scopedServices :
            raise RuntimeException(
                'The parent scope "{0}" must be active when entering this '
                'scope.'.format(self._scopes[name])
            );


        # check if a scope of this name is already active, if so we need to
        # remove all services of this scope, and those of any of its child
        # scopes from the global services map
        if name in self._scopedServices :
            services = OrderedDict();
            services[0] = self._services;
            services[name] = self._scopedServices[name];
            self._scopedServices.pop(name, None);

            for child in self._scopeChildren[name]:
                if child in self._scopedServices:
                    services[child] = self._scopedServices[child];
                    self._scopedServices.pop(child, None);


            # update global map
            self._services = Array.diffKey(*services.values());
            services.pop(0);

            # add stack entry for this scope so we can restore the removed services later
            if name not in self._scopeStacks :
                self._scopeStacks[name] = list();

            self._scopeStacks[name].append(services);


        self._scopedServices[name] = dict();


    def leaveScope(self, name):
        """This is called to leave the current scope, and move back to the parent
        scope.

        @param: string name The name of the scope to leave

        @raise InvalidArgumentException if the scope is not active:

        @api

        """

        if name not in self._scopedServices :
            raise InvalidArgumentException(
                'The scope "{0}" is not active.'.format(name)
            );


        # remove all services of this scope, or any of its child scopes from
        # the global service map
        services = [self._services, self._scopedServices[name]];
        self._scopedServices.pop(name, None);
        for child in self._scopeChildren[name]:
            if child not in self._scopedServices :
                continue;


            services.append(self._scopedServices[child]);
            self._scopedServices.pop(child, None);

        self._services = Array.diffKey(*services);

        # check if we need to restore services of a previous scope of this type:
        if name in self._scopeStacks and self._scopeStacks[name] :
            services = self._scopeStacks[name].pop();
            self._scopedServices.update(services);

            for scopeServices in services.values():
                self._services.update(scopeServices);



    def addScope(self, scope):
        """Adds a scope to the container.

        @param: ScopeInterface scope

        @raise InvalidArgumentException

        @api

        """
        assert isinstance(scope, ScopeInterface);

        name = scope.getName();
        parentScope = scope.getParentName();

        if (self.SCOPE_CONTAINER == name or self.SCOPE_PROTOTYPE == name) :
            raise InvalidArgumentException(
                'The scope "{0}" is reserved.'.format(name)
            );

        if name in self._scopes :
            raise InvalidArgumentException(
                'A scope with name "{0}" already exists.'.format(name)
            );

        if self.SCOPE_CONTAINER != parentScope and  parentScope not in self._scopes :
            raise InvalidArgumentException(
                'The parent scope "{0}" does not exist, or is invalid.'
                ''.format(parentScope)
            );


        self._scopes[name] = parentScope;
        self._scopeChildren[name] = list();

        # normalize the child relations
        while (parentScope != self.SCOPE_CONTAINER):
            self._scopeChildren[parentScope].append(name);
            parentScope = self._scopes[parentScope];



    def hasScope(self, name):
        """Returns whether this container has a certain scope

        @param: string name The name of the scope

        @return Boolean

        @api

        """

        return name in self._scopes;


    def isScopeActive(self, name):
        """Returns whether this scope is currently active

        This does not actually check if the passed scope actually exists.:

        @param: string name

        @return Boolean

        @api

        """

        return name in self._scopedServices;


    @classmethod
    def camelize(self, identifier):
        """Camelizes a string.

        @param: string identifier A string to camelize

        @return string The camelized string

        """
        def callback(match):
            if '.' == match.group(1):
                return '_'+match.group(2);
            else:
                return ''+match.group(2);

        return re.sub('(^|_|\.)+(.)', callback, identifier);

    @classmethod
    def underscore(cls, identifier):
        """A string to underscore.

        @param identifier: string The string to underscore

        @return: string The underscored string
        """
        value = str(identifier);
        # value = value.replace("_", ".");
        patterns = [
            r"([A-Z]+)([A-Z][a-z])",
            r"([a-z\d])([A-Z])",
        ]
        repls = [
            '\\1_\\2',
            '\\1_\\2',
        ];

        for i in range(len(patterns)):
            value = re.sub(patterns[i], repls[i], value);

        return value.lower();

    def _formatIdentifier(self, identifier):
        return str(identifier).lower();



class ContainerBuilder(Container, TaggedContainerInterface):
    """ContainerBuilder is a DI container that provides an API to easily describe services.

    @author: Fabien Potencier <fabien@symfony.com>

    @api

    """
    def __init__(self, parameterBag=None):
        """Sets the track resources flag.

        If you are not using the loaders and therefore don't want
        to depend on the Config component, set this flag to False.

        @param: Boolean track True if you want to track resources, False otherwise:

        """
        self.__trackResources = True;
        self.__resources = [];
        self.__definitions = dict();
        self.__extensions = dict();
        self.__extensionsByNs = dict();
        self.__extensionConfigs  = dict();
        self.__aliases  = dict();
        self.__compiler = None;
        Container.__init__(self, parameterBag=parameterBag);

    def setResourceTracking(self, track):
        """Sets the track resources flag.

        If you are not using the loaders and therefore don't want
        to depend on the Config component, set this flag to False.

        @param: Boolean track True if you want to track resources, False otherwise:

        """
        self.__trackResources = bool(track);

    def isTrackingResources(self):
        """Checks if resources are tracked.:

        @return: Boolean True if resources are tracked, False otherwise:

        """
        return self.__trackResources;

    def registerExtension(self, extension):
        """Registers an extension.

        @param: ExtensionInterface extension An extension instance

        @api

        """
        assert isinstance(extension, ExtensionInterface);

        self.__extensions[extension.getAlias()] = extension;
        if extension.getNamespace():
            self.__extensionsByNs[extension.getNamespace()] = extension;

    def getExtension(self, name):
        """Returns an extension by alias or namespace.

        @param: string name An alias or a namespace

        @return ExtensionInterface An extension instance

        @raise LogicException if the extension is not registered:

        @api

        """
        if name in self.__extensions:
            return self.__extensions[name];

        if name in self.__extensionsByNs:
            return self.__extensionsByNs[name];

        raise LogicException(
            'Container extension "{0}" is not registered'.format(name)
        );


    def getExtensions(self):
        """Returns all registered extensions.

        @return: ExtensionInterface[] An array of ExtensionInterface

        @api

        """
        return self.__extensions;

    def hasExtension(self, name):
        """Checks if we have an extension.:

        @param: string name The name of the extension

        @return Boolean If the extension exists

        @api

        """
        return name in self.__extensions or name in self.__extensionsByNs;


    def getResources(self):
        """Returns an array of resources loaded to build this configuration.

        @return: ResourceInterface[] An array of resources

        @api

        """
        return Array.uniq(self.__resources);

    def addResource(self, resource):
        """Adds a resource for this configuration.

        @param: ResourceInterface resource A resource instance

        @return ContainerBuilder The current instance

        @api

        """
        assert isinstance(resource, ResourceInterface);

        if not self.__trackResources or not str(resource):
            return self;

        self.__resources.append(resource);

        return self;

    def setResources(self, resources):
        """Sets the resources for this configuration.

        @param: ResourceInterface[] resources An array of resources

        @return ContainerBuilder The current instance

        @api

        """
        assert isinstance(resources, list);

        if ( not self.__trackResources) :
            return self;


        self.__resources = resources;

        return self;

    def addObjectResource(self, objectResource):
        """Adds the object class hierarchy(, as resources.):

        @param: object object An object instance

        @return ContainerBuilder The current instance

        @api

        """
        assert isinstance(objectResource, Object);
        if not self.__trackResources:
            return self;

        parent = ReflectionObject(objectResource);
        while parent:
            self.addResource(FileResource(parent.getFileName()));
            parent = parent.getParentClass();

        return self;

    def loadFromExtension(self, extension, values = None):
        """Loads the configuration for an extension.

        @param: string extension The extension alias or namespace
        @param array  values    An array of values that customizes the extension

        @return ContainerBuilder The current instance
        @raise BadMethodCallException When this ContainerBuilder is frozen

        @raise LogicException if the container is frozen:

        @api

        """
        if values is None:
            values = dict();

        if self.isFrozen():
            raise BadMethodCallException(
                'Cannot load from an extension on a frozen container.'
            );

        namespace = self.getExtension(extension).getAlias();
        if namespace not in self.__extensionConfigs:
            self.__extensionConfigs[namespace] = list();
        self.__extensionConfigs[namespace].append(values);

        return self;


    def addCompilerPass(self, cpass,
                        cType=PassConfig.TYPE_BEFORE_OPTIMIZATION):
        """Adds a compiler pass.

        @param: CompilerPassInterface cpass A compiler pass
        @param string                cType The type of compiler pass

        @return ContainerBuilder The current instance

        @api

        """
        assert isinstance(cpass, CompilerPassInterface);

        if self.__compiler is None:
            self.__compiler = Compiler();

        self.__compiler.addPass(cpass, cType);

        self.addObjectResource(cpass);

        return self;


    def getCompilerPassConfig(self):
        """Returns the compiler pass config which can then be modified.:

        @return: PassConfig The compiler pass config

        @api

        """
        if self.__compiler is None:
            self.__compiler = Compiler();

        return self.__compiler.getPassConfig();

    def getCompiler(self):
        """Returns the compiler.

        @return: Compiler The compiler

        @api

        """
        if self.__compiler is None:
            self.__compiler = Compiler();

        return self.__compiler;

    def getScopes(self):
        """Returns all Scopes.

        @return: dict A dict of scopes

        @api

        """

        return self._scopes;

    def getScopeChildren(self):
        """Returns all Scope children.

        @return: dict A dict of scope children.

        @api

        """

        return self._scopeChildren;

    def set(self, identifier, service, scope = ContainerInterface.SCOPE_CONTAINER):
        """Sets a service.

        @param: string id      The service identifier:
        @param object service The service instance
        @param string scope   The scope

        @raise BadMethodCallException When this ContainerBuilder is frozen

        @api

        """
        if self.isFrozen():
            if identifier not in self.__definitions or \
            not self.__definitions[identifier].isSynthetic():
                raise BadMethodCallException(
                    'Setting service on a frozen container is not allowed'
                );

        identifier = self._formatIdentifier(identifier);
        self.__definitions.pop(identifier, None);
        self.__aliases.pop(identifier, None);

        Container.set(self, identifier, service, scope);

    def removeDefinition(self, identifier):
        """Removes a service definition.

        @param: string id The service identifier:

        @api

        """
        identifier = self._formatIdentifier(identifier);
        self.__definitions.pop(identifier, None);

    def has(self, identifier):
        """Returns True if the given service is defined.:

        @param: string id The service identifier:

        @return Boolean True if the service is defined, False otherwise:

        @api

        """
        identifier = self._formatIdentifier(identifier);
        return identifier in self.__definitions\
            or identifier in self.__aliases\
            or Container.has(self, identifier);

    def get(self, identifier, invalidBehavior = ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE):
        """Gets a service.

        @param: string  id              The service identifier:
        @param integer invalidBehavior The behavior when the service does not exist

        @return object The associated service

        @raise InvalidArgumentException if the service is not defined:
        @raise LogicException if the service has a circular reference to itself:

        @see Reference

        @api

        """
        identifier = self._formatIdentifier(identifier);
        try:
            return Container.get(self, identifier, ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE);
        except InvalidArgumentException as e:
            if identifier in self._loading:
                raise LogicException(
                    'The service "{0}" has a circular reference to itself.'
                    ''.format(identifier), 0, e
                );

            if not self.hasDefinition(identifier) \
                and identifier in self.__aliases:
                return self.get(self.__aliases[identifier]);

            try:
                definition = self.getDefinition(identifier);
            except InvalidArgumentException as e:
                if (ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE  != invalidBehavior):
                    return None;
                raise e;

            self._loading[identifier] = True;
            service = self.__createService(definition, identifier);
            self._loading.pop(identifier, None);
            return service;

    def merge(self, container):
        """Merges a ContainerBuilder with the current ContainerBuilder configuration.

        Service definitions overrides the current defined ones.

        But for parameters, they are overridden by the current ones. It allows
        the parameters passed to the container constructor to have precedence
        over the loaded ones.

        container = ContainerBuilder(array('foo' => 'bar'));
        loader = LoaderXXX(container);
        loader.load('resource_name');
        container.register('foo', stdClass());

        In the above example, even if the loaded resource defines a foo:
        parameter, the value will still be 'bar' as defined in the ContainerBuilder
        constructor.

        @param: ContainerBuilder container The ContainerBuilder instance to merge.


        @raise BadMethodCallException When this ContainerBuilder is frozen

        @api

        """
        assert isinstance(container, ContainerBuilder);
        if self.isFrozen():
            raise BadMethodCallException(
                'Cannot merge on a frozen container.'
            );

        self.addDefinitions(container.getDefinitions());
        self.addAliases(container.getAliases());
        self.getParameterBag().add(container.getParameterBag().all());

        if self.__trackResources:
            for resource in container.getResources():
                self.addResource(resource);

        for name in self.__extensions.keys():
            if name not in self.__extensionConfigs:
                self.__extensionConfigs[name] = list();

            if container.getExtensionConfig(name):
                self.__extensionConfigs[name] = \
                    list(self.__extensionConfigs[name]) +\
                    list(container.getExtensionConfig[name]);



    def getExtensionConfig(self, name):
        """Returns the configuration array for the given extension.

        @param: string name The name of the extension

        @return array An array of configuration

        @api

        """
        if not name in self.__extensionConfigs:
            self.__extensionConfigs[name] = list();

        return self.__extensionConfigs[name];



    def prependExtensionConfig(self, name, config):
        """Prepends a config array to the configs of the given extension.

        @param: string name    The name of the extension
        @param: list  config  The config to set

        """
        assert isinstance(config, list);

        if not name in self.__extensionConfigs:
            self.__extensionConfigs[name] = list();

        self.__extensionConfigs[name].insert(0, config);


    def compile(self):
        """Compiles the container.

        This method passes the container to compiler
        passes whose job is to manipulate and optimize
        the container.

        The main compiler passes roughly do four things:

            The extension configurations are merged;
            Parameter values are resolved;
            The parameter bag is frozen;
            Extension loading is disabled.

        @api:

        """
        if self.__compiler is None:
            self.__compiler = Compiler();

        if self.__trackResources:
            for cpass in self.__compiler.getPassConfig().getPasses():
                self.addObjectResource(cpass);

        self.__compiler.compile(self);

        self.__extensionConfigs = list();

        Container.compile(self);


    def getServiceIds(self):
        """Gets all service ids.

        @return: list A list of all defined service ids

        """
        return Array.uniq(
            list(self.getDefinitions().keys()) +\
            list(self.getAliases().keys()) +\
            Container.getServiceIds(self)
        );

    def addAliases(self, aliases):
        """Adds the service aliases.

        @param: dict aliases An dict of aliases

        @api

        """
        assert isinstance(aliases, dict);

        for alias, identifier in aliases.items():
            self.setAlias(alias, identifier);


    def setAliases(self, aliases):
        """Sets the service aliases.

        @param: dict aliases An array of aliases

        @api

        """
        assert isinstance(aliases, dict);

        self.__aliases = dict();
        self.addAliases(aliases);


    def setAlias(self, alias, identifier):
        """Sets an alias for an existing service.

        @param: string        alias The alias to create
        @param string|Alias  identifier    The service to alias

        @raise InvalidArgumentException if the id is not a string or an Alias:
        @raise InvalidArgumentException if the alias is for itself:

        @api

        """
        alias = self.__formatAlias(alias);

        if isinstance(identifier, str):
            identifier = Alias(identifier);
        elif not isinstance(identifier, Alias):
            raise InvalidArgumentException(
                '$id must be a string, or an Alias object.'
            );

        if alias == str(identifier).lower():
            raise InvalidArgumentException(
                'An alias can not reference itself, got a circular reference '
                'on "{0}".'.format(alias)
            );

        self.__definitions.pop(alias, None);

        self.__aliases[alias] = identifier;

    def removeAlias(self, alias):
        """Removes an alias.

        @param: string alias The alias to remove

        @api

        """
        alias = self.__formatAlias(alias);
        self.__aliases.pop(alias, None);


    def hasAlias(self, identifier):
        """Returns True if an alias exists under the given identifier.

        @param: string identifier The service identifier

        @return Boolean True if the alias exists, False otherwise:

        @api

        """
        alias = self.__formatAlias(identifier);
        return alias in self.__aliases;


    def getAliases(self):
        """Gets all defined aliases.

        @return: Alias[] An array of aliases

        @api

        """
        return self.__aliases;

    def getAlias(self, identifier):
        """Gets an alias.

        @param: string id The service identifier:

        @return Alias An Alias instance

        @raise InvalidArgumentException if the alias does not exist:

        @api

        """
        identifier = self.__formatAlias(identifier);

        if not self.hasAlias(identifier):
            raise InvalidArgumentException(
                'The service alias "{0}" does not exist.'
                ''.format(identifier)
            );

        return self.__aliases[identifier];





    def register(self, identifier, className=None):
        """Registers a service definition.

        This methods allows for simple registration of service definition
        with a fluid interface.

        @param: string id    The service identifier
        @param string class The service class

        @return Definition A Definition instance

        @api

        """
        identifier = self._formatIdentifier(identifier);
        return self.setDefinition(identifier, Definition(className));


    def addDefinitions(self, definitions):
        """Adds the service definitions.

        @param: Definition[] definitions An array of service definitions

        @api

        """
        assert isinstance(definitions, dict);

        for identifier, definition in definitions.items():
            self.setDefinition(identifier, definition);


    def setDefinitions(self, definitions):
        """Sets the service definitions.

        @param: Definition[] definitions An array of service definitions

        @api

        """
        assert isinstance(definitions, dict);

        self.__definitions = dict();
        self.addDefinitions(definitions);


    def getDefinitions(self):
        """Gets all service definitions.

        @return: Definition[] An array of Definition instances

        @api

        """
        return self.__definitions;

    def setDefinition(self, identifier, definition):
        """Sets a service definition.

        @param: string     id         The service identifier:
        @param Definition definition A Definition instance

        @return Definition the service definition

        @raise BadMethodCallException When this ContainerBuilder is frozen

        @api

        """
        assert isinstance(definition, Definition);

        if self.isFrozen():
            raise BadMethodCallException(
                'Adding definition to a frozen container is not allowed'
            );

        identifier = self._formatIdentifier(identifier);
        self.__aliases.pop(identifier, None);

        self.__definitions[identifier] = definition;

        return definition;


    def hasDefinition(self, identifier):
        """Returns True if a service definition exists under the given identifier.:

        @param: string id The service identifier:

        @return Boolean True if the service definition exists, False otherwise:

        @api

        """
        identifier = self._formatIdentifier(identifier);
        return identifier in self.__definitions;

    def getDefinition(self, identifier):
        """Gets a service definition.

        @param: string id The service identifier:

        @return Definition A Definition instance

        @raise InvalidArgumentException if the service definition does not exist:

        @api

        """
        identifier = self._formatIdentifier(identifier);

        if not self.hasDefinition(identifier):
            raise InvalidArgumentException(
                'The service definition "{0}" does not exist.'
                ''.format(identifier)
            );

        return self.__definitions[identifier];


    def findDefinition(self, identifier):
        """Gets a service definition by id or alias.

        The method "unaliases" recursively to return a Definition instance.

        @param: string id The service identifier or alias:

        @return Definition A Definition instance

        @raise InvalidArgumentException if the service definition does not exist:

        @api

        """
        while self.hasAlias(identifier):
            identifier = str(self.getAlias(identifier));

        return self.getDefinition(identifier);

    def __createService(self, definition, identifier):
        """Creates a service for a service definition.

        @param: Definition definition A service definition instance
        @param string     id         The service identifier:

        @return object The service described by the service definition

        @raise RuntimeException When the scope is inactive
        @raise RuntimeException When the factory definition is incomplete
        @raise RuntimeException When the service is a synthetic service
        @raise InvalidArgumentException When configure callable is not callable

        """
        assert isinstance(definition, Definition);

        if definition.isSynthetic():
            raise RuntimeException(
                'You have requested a synthetic service ("{0}"). '
                'The DIC does not know how to construct this service.'
                ''.format(identifier)
            );

        parameterBag = self.getParameterBag();

        if None is not definition.getFile() :
            path = parameterBag.resolveValue(definition.getFile());
            module = SourceFileLoader.load(path);
        else:
            module = None;

        value = parameterBag.resolveValue(definition.getArguments());
        value = parameterBag.unescapeValue(value);
        arguments = self.resolveServices(value);

        if not definition.getFactoryMethod() is None:
            if not definition.getFactoryClass() is None:
                factory = parameterBag.resolveValue(
                    definition.getFactoryClass()
                );
                if module is not None:
                    factory = getattr(module, factory);
                else:
                    factory = ClassLoader.load(factory);
            elif not definition.getFactoryService() is None:
                factory = self.get(parameterBag.resolveValue(
                    definition.getFactoryService()
                ));
            else:
                raise RuntimeException(
                    'Cannot create service "{0}" from factory method without '
                    'a factory service or factory class.'
                    ''.format(identifier)
                );

            service = getattr(factory, definition.getFactoryMethod())(*arguments);
        else:
            className = parameterBag.resolveValue(definition.getClass());
            if module is not None:
                service = getattr(module, className)(*arguments);
            else:
                service = ClassLoader.load(className)(*arguments);

        scope = definition.getScope();
        if self.SCOPE_PROTOTYPE  != scope :
            if self.SCOPE_CONTAINER != scope and scope not in self._scopedServices :
                raise RuntimeException(
                    'You tried to create the "{0}" service of an inactive '
                    'scope.'.format(identifier)
                );

            lowerId = self._formatIdentifier(identifier);
            self._services[lowerId] = service;

            if (self.SCOPE_CONTAINER != scope) :
                self._scopedServices[scope][lowerId] = service;

        for call in definition.getMethodCalls():
            services = self.getServiceConditionals(call[1]);
            ok = True;
            for s in services:
                if not self.has(s):
                    ok = False;
                    break;
            if ok:
                args = self.resolveServices(parameterBag.resolveValue(
                    call[1]
                ));
                getattr(service, call[0])(*args);

        properties = self.resolveServices(parameterBag.resolveValue(
            definition.getProperties()
        ));
        for name, value in properties.items():
            setattr(service, name, value);

        closure = definition.getConfigurator();
        if closure:
            if isinstance(closure, list):
                if isinstance(closure[0], Reference):
                    closure[0] = self.get(str(closure[0]));
                else:
                    closure[0] = parameterBag.resolveValue(closure[0]);
                    closure[0] = ClassLoader.load(closure[0]);

                closure = getattr(closure[0], closure[1]);

            if not Tool.isCallable(closure):
                raise InvalidArgumentException(
                    'The configure callable for class "{0}" is not a callable.'
                    ''.format(type(service).__name__)
                );

            closure(service);

        return service;

    def resolveServices(self, value):
        """Replaces service references by the real service instance.

        @param: mixed value A value

        @return mixed The same value with all service references replaced by the real service instances

        """
        if isinstance(value, dict):
            for k, v in value.items():
                value[k] = self.resolveServices(v);
        if isinstance(value, list):
            i = 0;
            for v in value:
                value[i] = self.resolveServices(v);
                i+=1;
        elif isinstance(value, Reference):
            value = self.get(str(value), value.getInvalidBehavior());
        elif isinstance(value, Definition):
            value = self.__createService(value, None);
        return value;


    def findTaggedServiceIds(self, name):
        """Returns service ids for a given tag.

        @param: string name The tag name

        @return array An array of tags

        @api

        """
        tags = dict();
        for identifier, definition in self.getDefinitions().items():
            if definition.getTag(name):
                tags[identifier] = definition.getTag(name);
        return tags;

    def findTags(self):
        """Returns all tags the defined services use.

        @return: array An array of tags

        """
        tags = dict();
        for definition in self.getDefinitions().values():
            tags.update(definition.getTags().keys());

        return tags;

    @classmethod
    def getServiceConditionals(cls, value):
        """Returns the Service Conditionals.

        @param: mixed value An array of conditionals to return.

        @return array An array of Service conditionals

        """
        services = list();

        if isinstance(value, list):
            for v in value:
                iterable = cls.getServiceConditionals(v);
                services.extend(iterable);
                services = Array.uniq(services);
        elif isinstance(value, Reference):
            services.append(str(value));

        return services;


    def __formatAlias(self, identifer):
        return self._formatIdentifier(identifer);
