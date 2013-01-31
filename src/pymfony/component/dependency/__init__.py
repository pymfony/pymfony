# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""
"""

from __future__ import absolute_import;

import re;
import ConfigParser;
import os.path;
import json;

from pymfony.component.system import Object, abstract, interface;
import pymfony.component.system as system;
from pymfony.component.system import Tool;
from pymfony.component.system import Array;
from pymfony.component.config import FileLoader as BaseFileLoader;
from pymfony.component.config import FileResource;
from pymfony.component.config import ResourceInterface;
from pymfony.component.config import Processor;

@interface
class ContainerInterface(Object):
    def set(self, identifier, service):
        """Sets a service.

        @param identifier: string The service identifier
        @param service: object The service instance
        """
        pass;

    def get(self, identifier):
        """Gets a service.

        @param identifier: string  The service identifier

        @return: object The associated service
        """
        pass;

    def has(self, identifier):
        """Returns true if the given service is defined.

        @param identifier: string The service identifier

        @return: boolean True if the service is defined, False otherwise
        """
        pass;

    def setParameter(self, name, value):
        """Sets a parameter.

        @param name: string  The parameter name
        @param value: mixed  The parameter value
        """
        pass;

    def getParameter(self, name):
        """Gets a parameter.

        @param name: string The parameter name
        @return: mixed The parameter value
        """
        pass;

    def hasParameter(self, name):
        """Checks if a parameter exists.

        @param name: string The parameter name
        @return: boolean Return True if the parameter exist.
        """
        pass;

@interface
class ParameterBagInterface(Object):

    def clear(self):
        """Clears all parameters."""
        pass;

    def add(self, parameters):
        """Adds parameters to the service container parameters.

        @param parameters: dict An array of parameters
        """
        pass;

    def all(self):
        """Gets the service container parameters.
        
        @return: dict An array of parameters
        """
        pass;

    def get(self, name):
        """Gets a service container parameter.
        
        @param name: string The parameter name

        @return: mixed The parameter value

        @raise ParameterNotFoundException: if the parameter is not defined
        """

    def set(self, name, value):
        """Sets a service container parameter.

        @param name: string The parameter name
        @param value: mixed The parameter value
        """
        pass;

    def has(self, name):
        """Returns true if a parameter name is defined.
        
        @param name: string The parameter name
        @return: Boolean true if the parameter name is defined, false otherwise
        """
        pass;

    def resolve(self):
        """Replaces parameter placeholders (%name%)
        by their values for all parameters.
        """
        pass;

    def resolveValue(self, value):
        """Replaces parameter placeholders (%name%) by their values.

        @param value: mixed A value

        @raise ParameterNotFoundException: 
        if a placeholder references a parameter that does not exist 
        """
        pass;

    def escapeValue(self, value):
        """Escape parameter placeholders %

        @param mixed $value

        @return: mixed
        """
        pass;

    def unescapeValue(self, value):
        """Unescape parameter placeholders %

        @param value:  mixed

        @return: mixed
        """
        pass;

@interface
class ContainerAwareInterface(Object):
    def setContainer(self, container):
        """Sets the Container.

        @param container: ContainerInterface A ContainerInterface instance
        """
        pass;

@interface
class ExtensionInterface(Object):
    """ExtensionInterface is the interface implemented
    by container extension classes.
    """
    def load(self, configs, container):
        """Loads a specific configuration.

        @param configs: list An array of configuration values
        @param container: ContainerBuilder A ContainerBuilder instance

        @raise AttributeError: When provided tag is not defined
            in this extension
        """
        pass;


    def getNamespace(self):
        """Returns the namespace to be used for this extension (XML namespace).

        @return: string The XSD base path
        """
        pass;


    def getXsdValidationBasePath(self):
        """Returns the base path for the XSD files.

        @return: string The XSD base path
        """
        pass;


    def getAlias(self):
        """Returns the recommended alias to use in XML.

        This alias is also the mandatory prefix to use when using YAML.

        @return: string The alias
        """
        pass;

@interface
class ConfigurationExtensionInterface(Object):
    """ConfigurationExtensionInterface is the interface implemented
    by container extension classes.
    """

    def getConfiguration(self, configs, container):
        """Returns extension configuration

        @param configs: dict An array of configuration values
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

@interface
class TaggedContainerInterface(ContainerInterface):
    """TaggedContainerInterface is the interface implemented when a
    container knows how to deals with tags.
    """


    def findTaggedServiceIds(self, name):
        """Returns service ids for a given tag.

        @param name: string The tag name

        @return: dict An array of tags
        """
        pass;

@interface
class CompilerPassInterface(Object):
    """Interface that must be implemented by compilation passes
    """
    def process(self, container):
        """You can modify the container here before it is dumped to PHP code.

        @param container: ContainerBuilder
        """
        pass;

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
        return Container.underscore(classBaseName);

    def _processConfiguration(self, configuration, configs):
        """@final
        """
        assert isinstance(configs, list);
        processor = Processor();
        return processor.processConfiguration(configuration, configs);

    def getConfiguration(self, configs, container):
        assert isinstance(configs, dict);
        assert isinstance(container, ContainerBuilder);
        moduleName = str(type(self).__module__);
        className = 'Configuration';
        try:
            module = __import__(moduleName, globals(), {}, [className], 0);
        except TypeError:
            module = __import__(moduleName, globals(), {}, ['__init__'], 0);

        if hasattr(module, 'Configuration'):
            configuration = getattr(module, 'Configuration')();
            path = system.ReflectionObject(configuration).getFileName();
            container.addResource(FileResource(path));
            return configuration;

        return None;

class FileLoader(BaseFileLoader):
    def __init__(self, container, locator):
        assert isinstance(container, ContainerBuilder);
        self._container = container;
        BaseFileLoader.__init__(self, locator);

class Alias(Object):
    def __init__(self, identifier, public=True):
        self.__id = str(identifier).lower();
        self.__public = bool(public);

    def isPublic(self):
        return self.__public;

    def setPublic(self, boolean):
        self.__public = bool(boolean);

    def __str__(self):
        return self.__id;


class PassConfig(Object):
    """Compiler Pass Configuration

    This class has a default configuration embedded.
    """
    TYPE_BEFORE_OPTIMIZATION = 'BeforeOptimization';

    def __init__(self):
        self.__mergePass = MergeExtensionConfigurationPass();

        self.__beforeOptimizationPasses = list();

    def getPasses(self):
        """Returns all passes in order to be processed.

        @return: list An list of all passes to process
        """

        passes = [self.__mergePass];
        passes.extend(self.__beforeOptimizationPasses);

        return passes;

    def addPass(self, cPass, cType=TYPE_BEFORE_OPTIMIZATION):
        """Adds a pass.

        @param cPass: CompilerPassInterface A Compiler pass
        @param cType: string The pass type

        @raise InvalidArgumentException: when a pass type doesn't exist
        """
        assert isinstance(cPass, CompilerPassInterface);

        propertyName = "get{0}Passes".format(cType);

        if not hasattr(self, propertyName):
            raise InvalidArgumentException(
                'Invalid type "{0}".'.format(cType)
            );

        getattr(self, propertyName)().append(cPass);

    def getMergePass(self):
        """Gets the Merge Pass.

        @return: CompilerPassInterface A merge pass
        """
        return self.__mergePass;

    def setMergePass(self, mergePass):
        """Sets the Merge Pass.

        @param mergePass: CompilerPassInterface A merge pass
        """
        assert isinstance(mergePass, CompilerPassInterface);

        self.__mergePass = mergePass;

    def getBeforeOptimizationPasses(self):
        """
        @return: list
        """
        return self.__beforeOptimizationPasses;

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
        cfgParser = ConfigParser.ConfigParser();
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

        self.__parseImports(content, path);

        self.__parseParameters(content);

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
        result = json.loads(s);

        return self.__validate(result, filename);

    def __validate(self, content, path):
        if content is None:
            return;

        if not isinstance(content, dict):
            raise InvalidArgumentException(
                'The "{0}" file is not valid.'
                ''.format(path)
            );

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
                if not isinstance(service['tags'], dict):
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

                definition.addTag(name, attributes);

        self._container.setDefinition(identifier, definition);

    def __resolveServices(self, value):
        if isinstance(value, list):
            value = map(self.__resolveServices, value);
        if isinstance(value, basestring) and value.startswith("@"):
            value = value[1:];
            if value.endswith("="):
                value = value[:-1];
                strict = False;
            else:
                strict = True;
            value = Reference(value, strict);

        return value;


class ContainerAware(ContainerAwareInterface):
    def __init__(self):
        self._container = None;

    def setContainer(self, container=None):
        assert isinstance(container, ContainerInterface);
        self._container = container;

class Container(ContainerInterface):
    def __init__(self, parameterBag=None):
        self._services = dict();
        self._parameterBag = None
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

        * Parameter values are resolved;
        * The parameter bag is frozen.
        """
        self._parameterBag.resolve();
        self._parameterBag = FrozenParameterBag(self._parameterBag.all());

    def isFrozen(self):
        """Returns true if the container parameter bag are frozen.

        @return: boolean
        """
        return isinstance(self._parameterBag, FrozenParameterBag);

    def getParameterBag(self):
        """Gets the service container parameter bag.
        
        @return: ParameterBagInterface A ParameterBagInterface instance
        """
        return self._parameterBag;

    def getParameter(self, name):
        return self._parameterBag.get(name);

    def hasParameter(self, name):
        return self._parameterBag.has(name);

    def setParameter(self, name, value):
        self._parameterBag.set(name, value);

    def set(self, identifier, service):
        identifier = self._formatIdentifier(identifier);
        self._services[identifier] = service;

    def get(self, identifier):
        identifier = self._formatIdentifier(identifier);
        if identifier in self._services.keys():
            return self._services[identifier];
        raise ServiceNotFoundException(identifier);

    def has(self, identifier):
        identifier = self._formatIdentifier(identifier);
        return identifier in self._services;

    def initialized(self, identifier):
        """Returns true if the given service has actually been initialized

        @param identifier: string The service identifier

        @return Boolean
        """
        identifier = self._formatIdentifier(identifier);
        return identifier in self._services;

    def _formatIdentifier(self, identifier):
        return identifier.lower();

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

class ContainerBuilder(Container, TaggedContainerInterface):
    def __init__(self, parameterBag=None):
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
        to depend on the Config component, set this flag to false.

        @param track: true if you want to track resources, false otherwise
        """
        self.__trackResources = bool(track);

    def isTrackingResources(self):
        """Checks if resources are tracked.

        @return: true if you want to track resources, false otherwise
        """
        return self.__trackResources;

    def get(self, identifier):
        """
        @raise ParameterCircularReferenceException:
        @raise LogicException:
        """
        identifier = self._formatIdentifier(identifier);
        try:
            return Container.get(self, identifier);
        except InvalidArgumentException as e:
            if identifier in self._loading:
                raise LogicException(
                    'The service "{0}" has a circular reference to itself.'
                    ''.format(identifier)
                );

            if not self.hasDefinition(identifier) \
                and identifier in self.getAliases():
                return self.get(self.__aliases[identifier]);

            try:
                definition = self.getDefinition(identifier);
            except InvalidArgumentException as e:
                raise e;

            self._loading[identifier] = True;
            service = self.__createService(definition, identifier);
            del self._loading[identifier];
            return service;

    def set(self, identifier, service):
        """Sets a service.

        @param identifier: string The service identifier
        @param service: object The service instance

        @raise BadMethodCallException: When this ContainerBuilder is frozen
        """
        if self.isFrozen():
            if identifier not in self.__definitions or \
            not self.__definitions[identifier].isSynthetic():
                raise BadMethodCallException(
                    'Setting service on a frozen container is not allowed'
                );

        identifier = self._formatIdentifier(identifier);
        self.removeDefinition(identifier);

        Container.set(self, identifier, service);

    def register(self, identifier, className=None):
        identifier = self._formatIdentifier(identifier);
        self.setDefinition(identifier, Definition(className));

    def registerExtension(self, extension):
        assert isinstance(extension, ExtensionInterface);

        self.__extensions[extension.getAlias()] = extension;
        if extension.getNamespace():
            self.__extensionsByNs[extension.getNamespace()] = extension;

    def getExtension(self, name):
        if name in self.__extensions:
            return self.__extensions[name];

        if name in self.__extensionsByNs:
            return self.__extensionsByNs[name];

        raise LogicException(
            'Container extension "%s" is not registered'.format(name)
        );

    def getExtensions(self):
        """Returns all registered extensions.

        @return: ExtensionInterface[] An dict of ExtensionInterface
        """
        return self.__extensions;

    def loadFromExtension(self, extension, values={}):
        """Loads the configuration for an extension.

        @param extension: string The extension alias or namespace
        @param values: An array of values that customizes the extension

        @return: ContainerBuilder The current instance

        @raise LogicException: if the container is frozen
        """
        if self.isFrozen():
            raise BadMethodCallException(
                'Cannot load from an extension on a frozen container.'
            );

        namespace = self.getExtension(extension).getAlias();
        self.__extensionConfigs[namespace].append(values);

        return self;


    def addCompilerPass(self, cpass,
                        cType=PassConfig.TYPE_BEFORE_OPTIMIZATION):
        """Adds a compiler pass.

        @param cpass: CompilerPassInterface A compiler pass
        @param cType: The type of compiler pass

        @return: ContainerBuilder The current instance
        """
        assert isinstance(cpass, CompilerPassInterface);

        if self.__compiler is None:
            self.__compiler = Compiler();

        self.__compiler.addPass(cpass, cType);

        self.addObjectResource(cpass);

        return self;


    def getCompilerPassConfig(self):
        """Returns the compiler pass config which can then be modified.

        @return: PassConfig The compiler pass config
        """
        if self.__compiler is None:
            self.__compiler = Compiler();

        return self.__compiler.getPassConfig();

    def getCompiler(self):
        """Returns the compiler.

        @return: Compiler The compiler
        """
        if self.__compiler is None:
            self.__compiler = Compiler();

        return self.__compiler;

    def getDefinition(self, identifier):
        """Gets a service definition.

        @param identifier: The service identifier

        @return: Definition A Definition instance

        @raise InvalidArgumentException: if the service definition
            does not exist
        """
        identifier = self._formatIdentifier(identifier);

        if not self.hasDefinition(identifier):
            raise InvalidArgumentException(
                'The service definition "{0}" does not exist.'
                ''.format(identifier)
            );

        return self.__definitions[identifier];

    def removeDefinition(self, identifier):
        """Removes a service definition.

        @param identifier: string The service identifier
        """
        identifier = self._formatIdentifier(identifier);
        try:
            del self.__definitions[identifier];
        except KeyError:
            pass;

    def has(self, identifier):
        """Returns true if a service definition exists under
        the given identifier.

        @param identifier: string The service identifier

        @return: Boolean true if the service definition exists, false otherwise
        """
        identifier = self._formatIdentifier(identifier);
        return identifier in self.__definitions or\
             Container.has(self, identifier);

    def addResource(self, resource):
        """Adds a resource for this configuration.

        @param resource: ResourceInterface

        @return: ContainerBuilder The current instance
        """
        assert isinstance(resource, ResourceInterface);

        if not self.__trackResources:
            return self;

        self.__resources.append(resource);

        return self;

    def setResource(self, resources):
        """Sets the resources for this configuration.

        @param resource: ResourceInterface[]

        @return: ContainerBuilder The current instance
        """
        for resource in resources:
            assert isinstance(resource, ResourceInterface);

        if not self.__trackResources:
            return self;

        self.__resources = resources;

        return self;

    def getResources(self):
        """Returns an array of resources loaded to build this configuration.

        @return: ResourceInterface[]
        """
        return Array.uniq(self.__resources);

    def addObjectResource(self, objectResource):
        """Adds the object class hierarchy as resources.

        @param objectResource: Object An object instance

        @return: ContainerBuilder The current instance
        """
        assert isinstance(objectResource, Object);
        if not self.__trackResources:
            return self;

        mro = system.ReflectionObject(objectResource).getmro();
        for parent in mro:
            filename = system.ReflectionClass(parent).getFileName();
            self.addResource(FileResource(filename));

        return self;

    def merge(self, container):
        """Merges a ContainerBuilder with the current ContainerBuilder
        configuration.

        Service definitions overrides the current defined ones.

        But for parameters, they are overridden by the current ones. It allows
        the parameters passed to the container constructor to have precedence
        over the loaded ones.

        container = ContainerBuilder(dict('foo': "bar"));
        loader = LoaderXXX(container);
        loader.load('resource_name');
        container.register('foo', stdClass());

        In the above example, even if the loaded resource defines a foo
        parameter, the value will still be 'bar' as defined in the
        ContainerBuilder constructor.

        @param container: ContainerBuilder instance to merge.

        @raise BadMethodCallException: When this ContainerBuilder is frozen
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

        for name, extension in self.__extensions.items():
            if name not in self.__extensionConfigs:
                self.__extensionConfigs[name] = list();

            if container.getExtensionConfig(name):
                self.__extensionConfigs[name] = \
                    list(self.__extensionConfigs[name]) +\
                    list(container.getExtensionConfig[name]);

    def getExtensionConfig(self, name):
        if not name in self.__extensionConfigs:
            self.__extensionConfigs[name] = list();

        return self.__extensionConfigs[name];

    def prependExtensionConfig(self, name, config):
        assert isinstance(config, list);

        if not name in self.__extensionConfigs:
            self.__extensionConfigs[name] = list();

        self.__extensionConfigs[name].insert(0, config);

    def compile(self):
        if self.__compiler is None:
            self.__compiler = Compiler();

        if self.__trackResources:
            for cpass in self.__compiler.getPassConfig().getPasses():
                self.addObjectResource(cpass);

        self.__compiler.compile(self);

        self.__extensionConfigs = list();

        Container.compile(self);

    def getServiceIds(self):
        return Array.uniq(
            self.getDefinitions().keys() +\
            self.getAliases().keys() +\
            Container.getServiceIds()
        );

    def addAliases(self, aliases):
        assert isinstance(aliases, dict);

        for alias, identifier in self.getAliases().items():
            self.setAlias(alias, identifier);

    def setAliases(self, aliases):
        assert isinstance(aliases, dict);

        self.__aliases = dict();
        self.addAliases(aliases);

    def __formatAlias(self, identifer):
        return self._formatIdentifier(identifer);

    def setAlias(self, alias, identifer):
        alias = self.__formatAlias(alias);

        if isinstance(identifer, basestring):
            identifer = Alias(identifer);
        elif not isinstance(identifer, Alias):
            raise InvalidArgumentException(
                '$id must be a string, or an Alias object.'
            );

        if alias == str(identifer).lower():
            raise InvalidArgumentException(
                'An alias can not reference itself, got a circular reference '
                'on "{0}".'.format(alias)
            );

        try:
            del self.__definitions[alias];
        except KeyError:
            pass;

        self.__aliases[alias] = identifer;

    def removeAlias(self, alias):
        alias = self.__formatAlias(alias);
        try:
            del self.__aliases[alias];
        except KeyError:
            pass;

    def hasAlias(self, alias):
        alias = self.__formatAlias(alias);
        return alias in self.__aliases;

    def getAliases(self):
        return self.__aliases;

    def getAlias(self, identifier):
        identifier = self.__formatAlias(identifier);

        if not self.hasAlias(identifier):
            raise InvalidArgumentException(
                'The service alias "{0}" does not exist.'
                ''.format(identifier)
            );

        return self.__aliases[identifier];


    def addDefinitions(self, definitions):
        """Adds the service definitions.

        @param definitions: Definition[] An dict of service definitions
        """
        assert isinstance(definitions, dict);

        for identifier, definition in definitions.items():
            self.setDefinition(identifier, definition);

    def setDefinitions(self, definitions):
        """Sets the service definitions.

        @param definitions: Definition[] An dict of service definitions
        """
        assert isinstance(definitions, dict);

        self.__definitions = dict();
        self.addDefinitions(definitions);

    def setDefinition(self, identifier, definition):
        """Sets a service definition.

        @param identifier: string The service identifier
        @param definition: Definition A Definition instance

        @return: Definition the service definition

        @raise BadMethodCallException: When this ContainerBuilder is frozen
        """
        assert isinstance(definition, Definition);

        if self.isFrozen():
            raise BadMethodCallException(
                'Adding definition to a frozen container is not allowed'
            );

        identifier = self._formatIdentifier(identifier);
        self.__definitions[identifier] = definition;

        return definition;

    def getDefinitions(self):
        """Gets all service definitions.

        @return: Definition[] An dict of Definition instances
        """
        return self.__definitions;

    def hasDefinition(self, identifier):
        """Returns true if a service definition exists under the given
        identifier.

        @param identifier: string The service identifier

        @return: Boolean true if the service definition exists, false otherwise
        """
        identifier = self._formatIdentifier(identifier);
        return identifier in self.__definitions;

    def findDefinition(self, identifier):
        while self.hasAlias(identifier):
            identifier = str(self.getAlias(identifier));

        return self.getDefinition(identifier);

    def resolveServices(self, value):
        """Replaces service references by the real service instance.

        @param value: mixed

        @return: mixed The same value with all service references
            replaced by the real service instances
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
            value = self.get(str(value));
        elif isinstance(value, Definition):
            value = self.__createService(value, None);
        return value;


    def __createService(self, definition, identifier):
        assert isinstance(definition, Definition);

        if definition.isSynthetic():
            raise RuntimeException(
                'You have requested a synthetic service ("{0}"). '
                'The DIC does not know how to construct this service.'
                ''.format(identifier)
            );
        parameterBag = self.getParameterBag();

        value = parameterBag.resolveValue(definition.getArguments());
        value = parameterBag.unescapeValue(value);
        arguments = self.resolveServices(value);

        if not definition.getFactoryMethod() is None:
            if not definition.getFactoryClass() is None:
                factory = parameterBag.resolveValue(
                    definition.getFactoryClass()
                );
            elif not definition.getFactoryService() is None:
                factory = self.get(parameterBag.resolveValue(
                    definition.getFactoryService()
                ));
            else:
                raise RuntimeException(
                    'Cannot create service from factory method without '
                    'a factory service or factory class.'
                );

            className = ".".join([factory, definition.getFactoryMethod()]);
        else:
            className = parameterBag.resolveValue(definition.getClass());

        moduleName, className = Tool.split(className);
        try:
            module = __import__(moduleName, globals(), {}, [className], 0);
        except TypeError:
            module = __import__(moduleName, globals(), {}, ["__init__"], 0);
        service = getattr(module, className)(*arguments);

        self._services[self._formatIdentifier(identifier)] = service;

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
    
            if not Tool.isCallable(closure):
                raise InvalidArgumentException(
                    'The configure callable for class "{0}" is not a callable.'
                    ''.format(type(service).__name__)
                );
            closure(service);

        return service;

    def findTaggedServiceIds(self, name):
        tags = dict();
        for identifier, definition in self.getDefinitions().items():
            if definition.getTag(name):
                tags[identifier] = definition.getTag(name);
        return tags;

    def findTags(self):
        """Returns all tags the defined services use.

        @return: dict An array of tags
        """
        tags = dict();
        for definition in self.getDefinitions().values():
            tags.update(definition.getTags().keys());

        return tags;


    @classmethod
    def getServiceConditionals(cls, value):
        services = list();

        if isinstance(value, list):
            for v in value:
                iterable = cls.getServiceConditionals(v);
                services = Array.uniq(services.extend(iterable));
        elif isinstance(value, Reference):
            services.append(str(value));

        return services;

class Reference(Object):
    def __init__(self, identifier, strict=True):
        self.__id = str(identifier).lower();
        self.__strict = bool(strict);

    def isStrict(self):
        return self.__strict;

    def __str__(self):
        return str(self.__id);


class Definition(Object):
    def __init__(self, className=None, arguments=None):
        if arguments is None:
            arguments = list();
        assert isinstance(arguments, list);

        self._arguments = arguments;
        self.__class = className;

        self.__file = None;
        self.__factoryClass = None;
        self.__factoryMethod = None;
        self.__factoryService = None;
        self.__configurator = None;
        self.__properties = dict();
        self.__calls = list();
        self.__tags = dict();
        self.__public = True;
        self.__synthetic = False;
        self.__abstract = False;

    def setFactoryClass(self, factoryClass):
        self.__factoryClass = factoryClass;
        return self;

    def getFactoryClass(self):
        return self.__factoryClass;

    def setFactoryMethod(self, factoryMethod):
        self.__factoryMethod = factoryMethod;
        return self;

    def getFactoryMethod(self):
        return self.__factoryMethod;

    def setFactoryService(self, factoryService):
        self.__factoryService = factoryService;
        return self;

    def getFactoryService(self):
        return self.__factoryService;

    def setClass(self, classNama):
        self.__class = classNama;
        return self;

    def getClass(self):
        return self.__class;

    def setArguments(self, arguments):
        assert isinstance(arguments, list);
        self._arguments = arguments;
        return self;

    def setProperties(self, properties):
        assert isinstance(properties, dict)
        self.__properties = properties;
        return self;

    def getProperties(self):
        return self.__properties;

    def setProperty(self, key, value):
        self.__properties[key] = value;
        return self;

    def addArgument(self, argument):
        self._arguments.append(argument);
        return self;

    def replaceArgument(self, index, argument):
        if index < 0 or index > len(self._arguments) - 1:
            raise OutOfBoundsException(
                'The index "{!d}" is not in the range [0, {!d}].'
                ''.format(index, len(self._arguments) - 1)
            );
        self._arguments[index] = argument;
        return self;

    def getArguments(self):
        return self._arguments;

    def getArgument(self, index):
        if index < 0 or index > len(self._arguments) - 1:
            raise OutOfBoundsException(
                'The index "{!d}" is not in the range [0, {!d}].'
                ''.format(index, len(self._arguments) - 1)
            );
        return self._arguments[index];

    def setMethodCalls(self, calls):
        self.__calls = list();
        for call in list(calls):
            self.addMethodCall(call[0], call[1]);
        return self;

    def addMethodCall(self, method, arguments=None):
        if arguments is None:
            arguments = list();
        arguments = list(arguments);
        method = str(method);
        if not method:
            raise InvalidArgumentException('Method name cannot be empty.');
        self.__calls.append([method, arguments]);
        return self;

    def removeMethodCall(self, method):
        for i, call in dict(self.__calls).items():
            if call[0] == method:
                del self.__calls[i];
                break;
        return self;

    def hasMethodCall(self, method):
        for call in self.__calls:
            if call[0] == method:
                return True;
        return False;

    def getMethodCalls(self):
        return self.__calls;

    def setTags(self, tags):
        assert isinstance(tags, dict);
        self.__tags = tags;
        return self;

    def getTags(self):
        return self.__tags;

    def getTag(self, name):
        if name in self.__tags:
            return self.__tags[name];
        else:
            return list();

    def addTag(self, name, attributes=None):
        if attributes is None:
            attributes = list();
        attributes = list(attributes);
        self.__tags[name] = list(self.__tags[name]);
        self.__tags[name].append(attributes);
        return self;

    def hasTag(self, name):
        return name in self.__tags;

    def clearTag(self, name):
        if self.hasTag(name):
            del self.__tags[name];
        return self;

    def clearTags(self):
        self.__tags = dict();
        return self;

    def setFile(self, filename):
        self.__file = filename;
        return self;

    def getFile(self):
        return self.__file;

    def setPublic(self, boolean):
        self.__public = bool(boolean);
        return self;

    def isPublic(self):
        return self.__public;
                
    def setSynthetic(self, boolean):
        self.__synthetic = bool(boolean);
        return self;

    def isSynthetic(self):
        return self.__synthetic;

    def setObject(self, boolean):
        self.__abstract = bool(boolean);
        return self;

    def isAbstract(self):
        return self.__abstract;

    def setConfigurator(self, closure):
        assert Tool.isCallable(closure);
        self.__configurator;
        return self;

    def getConfigurator(self):
        return self.__configurator;


class ParameterBag(ParameterBagInterface):
    def __init__(self, parameters=None):
        if parameters is None:
            parameters = dict();
        else:
            assert isinstance(parameters, dict);

        self._parameters = dict();
        self._resolved = False;

        self.add(parameters);

    def _formatName(self, name):
        return str(name).lower();

    def clear(self):
        self._parameters = dict();

    def add(self, parameters):
        assert isinstance(parameters, dict);

        for name, value in parameters.items():
            name = self._formatName(name);
            self._parameters[name] = value;

    def all(self):
        return self._parameters;

    def get(self, name):
        name = self._formatName(name);

        if not self.has(name):
            raise ParameterNotFoundException(name);

        return self._parameters[name];

    def set(self, name, value):
        name = self._formatName(name);
        self._parameters[name] = value;

    def has(self, name):
        name = self._formatName(name);
        return name in self._parameters.keys();

    def remove(self, name):
        name = self._formatName(name);
        del self._parameters[name];

    def resolve(self):
        if self._resolved:
            return;

        params = dict();
        for name, value in self._parameters.items():
            try:
                value = self.resolveValue(value);
                params[name] = self.unescapeValue(value);
            except ParameterNotFoundException as e:
                e.setSourceKey(name);
                raise e;

        self._parameters = params;
        self._resolved = True;

    def resolveValue(self, value, resolving=None):
        if resolving is None:
            resolving = dict();
        assert isinstance(resolving, dict);

        if isinstance(value, dict):
            args = dict();
            for k, v in value.items():
                k = self.resolveValue(k, resolving);
                args[k] = self.resolveValue(v, resolving);
            return args;

        if not isinstance(value, basestring):
            return value;

        return self.resolveString(value, resolving);

    def resolveString(self, value, resolving=None):
        if resolving is None:
            resolving = dict();
        assert isinstance(resolving, dict);

        match = re.search(r"^%([^%\s]+)%$", value);
        if match:
            key = match.group(1).lower();
            if key in resolving.keys():
                raise ParameterCircularReferenceException(resolving.keys());
            resolving[key] = True;
            if self._resolved:
                return self.get(key);
            else:
                return self.resolveValue(self.get(key), resolving);

        def callback(match):
            key = match.group(1);
            if key is None:
                return "%%";
            key = key.lower();
            if key in resolving.keys():
                raise ParameterCircularReferenceException(resolving.keys());
            resolved = self.get(key);
            if not isinstance(resolved, (str, float, int)):
                raise RuntimeException(
                    'A string value must be composed of strings and/or '
                    'numbers, but found parameter "{0}" of type {1} inside '
                    'string value "{2}".'
                    "".format(key, type(resolved), value)
                );
            resolved = str(resolved);
            resolving[key] = True;
            if self.isResolved():
                return resolved;
            else:
                return self.resolveString(resolved, resolving);

        return re.sub(r"%%|%([^%\s]+)%", callback, value);

    def isResolved(self):
        return self._resolved;

    def escapeValue(self, value):
        if isinstance(value, basestring):
            return value.replace("%", "%%");

        if isinstance(value, dict):
            result = dict();
            for k, v in value.items():
                result[k] = self.escapeValue(v);
            return result;

        return value;

    def unescapeValue(self, value):
        if isinstance(value, basestring):
            return value.replace("%%", "%");

        if isinstance(value, dict):
            result = dict();
            for k, v in value.items():
                result[k] = self.unescapeValue(v);
            return result;

        return value;

class FrozenParameterBag(ParameterBag):
    def __init__(self, parameters=None):
        if parameters is None:
            parameters = dict();
        else:
            assert isinstance(parameters, dict);

        self._parameters = parameters;
        self._resolved = True;

    def clear(self):
        raise LogicException(
            'Impossible to call clear() on a frozen ParameterBag.'
        );

    def add(self, parameters):
        raise LogicException(
            'Impossible to call add() on a frozen ParameterBag.'
        );

    def set(self, name, value):
        raise LogicException(
            'Impossible to call set() on a frozen ParameterBag.'
        );

class Compiler(Object):
    """This class is used to remove circular dependencies between individual
    passes.
    """
    def __init__(self):
        """Constructor.
        """
        self.__passConfig = PassConfig();

    def getPassConfig(self):
        """Returns the PassConfig.

        @return: PassConfig The PassConfig instance
        """
        return self.__passConfig;

    def addPass(self, cPass, cType=PassConfig.TYPE_BEFORE_OPTIMIZATION):
        """Adds a pass to the PassConfig.

        @param cPass: CompilerPassInterface A compiler pass
        @param cType: string The type of the pass
        """
        assert isinstance(cPass, CompilerPassInterface);

        self.__passConfig.addPass(cPass, cType);

    def compile(self, container):
        """Run the Compiler and process all Passes.

        @param container: ContainerBuilder
        """
        assert isinstance(container, ContainerBuilder);

        for cPass in self.__passConfig.getPasses():
            cPass.process(container);




class ServiceReferenceGraph():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class LoggingFormatter():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);


class MergeExtensionConfigurationPass(CompilerPassInterface):
    """Merges extension configs into the container builder"""
    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        parameters = container.getParameterBag().all();
        definitions = container.getDefinitions();
        aliases = container.getAliases();

        for extension in container.getExtensions().values():
            if isinstance(extension, PrependExtensionInterface):
                extension.prepend(container);

        for name, extension in container.getExtensions().items():
            config = container.getExtensionConfig(name);
            if not config:
                # this extension was not called
                continue;

            config = container.getParameterBag().resolveValue(config);

            tmpContainer = ContainerBuilder(container.getParameterBag());
            tmpContainer.setResourceTracking(container.isTrackingResources());
            tmpContainer.addObjectResource(extension);
            tmpContainer.set('kernel', container.get('kernel'));

            extension.load(config, tmpContainer);

            container.merge(tmpContainer);

        container.addDefinitions(definitions);
        container.addAliases(aliases);
        container.getParameterBag().add(parameters);


class ResolveDefinitionTemplatesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class ResolveParameterPlaceHoldersPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class CheckDefinitionValidityPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class ResolveReferencesToAliasesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class ResolveInvalidReferencesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class AnalyzeServiceReferencesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class CheckCircularReferencesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class CheckReferenceValidityPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class RemovePrivateAliasesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class RemoveAbstractDefinitionsPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class ReplaceAliasByActualDefinitionPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class RepeatedPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class InlineServiceDefinitionsPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class RemoveUnusedDefinitionsPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class CheckExceptionOnInvalidReferenceBehaviorPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);



class ExceptionInterface(Object, Exception):
    pass;

class OutOfBoundsException(ExceptionInterface):
    pass;

class LogicException(ExceptionInterface):
    pass;

class BadMethodCallException(LogicException):
    pass;

class InvalidArgumentException(ExceptionInterface):
    pass;


class ServiceNotFoundException(InvalidArgumentException):
    def __init__(self, identifier, sourceId=None):
        self.__id = identifier;
        self.__sourceId = sourceId;

        self.updateRepr();

    def updateRepr(self):
        if self.__sourceId is None:
            self.message = (
                'You have requested a non-existent parameter "{0}".'
                "".format(self.__id)
            );
        else:
            self.message = (
                'The service "{1}" has a dependency '
                'on a non-existent service "{0}".'
                "".format(self.__id, self.__sourceId)
            );

    def getKey(self):
        return self.__key;

    def setSourceId(self, key):
        self.__sourceId = key;

    def getSourceId(self):
        return self.__sourceId;


class ParameterNotFoundException(InvalidArgumentException):
    def __init__(self, key, sourceId=None, sourceKey=None):
        self.__key = key;
        self.__sourceKey = sourceKey;
        self.__sourceId = sourceId;

        self.updateRepr();

    def updateRepr(self):
        if not self.__sourceId is None:
            self.message = (
                'The service "{1}" has a dependency '
                'on a non-existent parameter "{0}".'
                "".format(self.__key, self.__sourceId)
            );
        elif not self.__sourceKey is None:
            self.message = (
                'The parameter "{1}" has a dependency '
                'on a non-existent parameter "{0}".'
                "".format(self.__key, self.__sourceKey)
            );
        else:
            self.message = (
                'You have requested a non-existent parameter "{0}".'
                "".format(self.__key)
            );

    def getKey(self):
        return self.__key;

    def setSourceKey(self, key):
        self.__sourceKey = key;

    def getSourceKey(self):
        return self.__sourceKey;

    def setSourceId(self, key):
        self.__sourceId = key;

    def getSourceId(self):
        return self.__sourceId;

class RuntimeException(ExceptionInterface):
    pass;

class ParameterCircularReferenceException(RuntimeException):
    pass;
