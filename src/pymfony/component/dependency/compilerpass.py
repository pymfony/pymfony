# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

from pymfony.component.system import clone;
from pymfony.component.system.types import Array;

from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency.extension import PrependExtensionInterface;
from pymfony.component.dependency.definition import DefinitionDecorator;
from pymfony.component.dependency.definition import Definition;
from pymfony.component.dependency.definition import Alias;
from pymfony.component.dependency.definition import Reference;
from pymfony.component.dependency.exception import ServiceCircularReferenceException;
from pymfony.component.dependency.exception import ScopeWideningInjectionException;
from pymfony.component.dependency.exception import ScopeCrossingInjectionException;
from pymfony.component.dependency.exception import ServiceNotFoundException;
from pymfony.component.dependency.exception import ParameterNotFoundException;
from pymfony.component.dependency.exception import RuntimeException;
from pymfony.component.dependency.exception import InvalidArgumentException;
from pymfony.component.dependency.interface import RepeatablePassInterface;
from pymfony.component.dependency.interface import CompilerPassInterface;
from pymfony.component.dependency.interface import ContainerInterface;

"""
"""

class RepeatedPass(CompilerPassInterface):
    """A pass that might be run repeatedly.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self, passes):
        """Constructor.
     *
     * @param RepeatablePassInterface[] passes An array of RepeatablePassInterface objects
     *
     * @raise InvalidArgumentException when the passes don't implement RepeatablePassInterface

        """
        assert isinstance(passes, list);

        self.__repeat = False;
        """@var Boolean

        """

        self.__passes = None;
        """@var RepeatablePassInterface[]

        """

        for cPass in passes:
            if ( not isinstance(cPass, RepeatablePassInterface)) :
                raise InvalidArgumentException(
                    'passes must be an array of RepeatablePassInterface.'
                );


            cPass.setRepeatedPass(self);


        self.__passes = passes;


    def process(self, container):
        """Process the repeatable passes that run more than once.
     *
     * @param ContainerBuilder container

        """

        self.__repeat = False;

        for cPass in self.__passes:
            cPass.process(container);


        if (self.__repeat) :
            self.process(container);



    def setRepeat(self):
        """Sets if the pass should repeat:

        """

        self.__repeat = True;


    def getPasses(self):
        """Returns the passes
     *
     * @return RepeatablePassInterface[] An array of RepeatablePassInterface objects

        """

        return self.__passes;


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

            extension.load(config, tmpContainer);

            container.merge(tmpContainer);

        container.addDefinitions(definitions);
        container.addAliases(aliases);
        container.getParameterBag().add(parameters);


class ResolveParameterPlaceHoldersPass(CompilerPassInterface):
    """Resolves all parameter placeholders "%somevalue%" to their real values.
    """
    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        parameterBag = container.getParameterBag();

        for identifier, definition in container.getDefinitions().items():
            try:
                definition.setClass(parameterBag.resolveValue(definition.getClass()));
                definition.setFile(parameterBag.resolveValue(definition.getFile()));
                definition.setArguments(parameterBag.resolveValue(definition.getArguments()));

                calls = list();
                for name, arguments in definition.getMethodCalls():
                    calls.append([parameterBag.resolveValue(name), parameterBag.resolveValue(arguments)]);

                definition.setMethodCalls(calls);

                definition.setProperties(parameterBag.resolveValue(definition.getProperties()));
            except ParameterNotFoundException as e:
                e.setSourceId(identifier);
                raise e;

        aliases = dict();
        for name, target in container.getAliases().items():
            aliases[parameterBag.resolveValue(name)] = parameterBag.resolveValue(target);

        container.setAliases(aliases);

        parameterBag.resolve();

class ResolveDefinitionTemplatesPass(CompilerPassInterface):
    """This replaces all DefinitionDecorator instances with their equivalent fully
 * merged Definition instance.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self):
        self.__container = None;
        self.__compiler = None;
        self.__formatter = None;

    def process(self, container):
        """Process the ContainerBuilder to replace DefinitionDecorator instances with their real Definition instances.
     *
     * @param ContainerBuilder container

        """
        assert isinstance(container, ContainerBuilder);

        self.__container = container;
        self.__compiler = container.getCompiler();
        self.__formatter = self.__compiler.getLoggingFormatter();

        for identifier in container.getDefinitions().keys():
            # yes, we are specifically fetching the definition from the:
            # container to ensure we are not operating on stale data
            definition = container.getDefinition(identifier);
            if ( not isinstance(definition, DefinitionDecorator) or definition.isAbstract()) :
                continue;


            self.__resolveDefinition(identifier, definition);



    def __resolveDefinition(self, identifier, definition):
        """Resolves the definition
     *
     * @param string              identifier  The definition identifier:
     * @param DefinitionDecorator definition
     *
     * @return Definition
     *
     * @raise RuntimeException When the definition is invalid

        """
        assert isinstance(definition, DefinitionDecorator);

        parent = definition.getParent();
        if ( not self.__container.hasDefinition(parent)) :
            raise RuntimeException(
                'The parent definition "{0}" defined for definition "{1}" '
                'does not exist.'.format(parent, identifier)
            );


        parentDef = self.__container.getDefinition(parent);
        if (isinstance(parentDef, DefinitionDecorator)) :
            parentDef = self.__resolveDefinition(parent, parentDef);


        self.__compiler.addLogMessage(self.__formatter.formatResolveInheritance(self, identifier, parent));
        newdef = Definition();

        # merge in parent definition
        # purposely ignored attributes: scope, abstract tags
        newdef.setClass(parentDef.getClass());
        newdef.setArguments(parentDef.getArguments());
        newdef.setMethodCalls(parentDef.getMethodCalls());
        newdef.setProperties(parentDef.getProperties());
        newdef.setFactoryClass(parentDef.getFactoryClass());
        definition.setFactoryMethod(parentDef.getFactoryMethod());
        newdef.setFactoryService(parentDef.getFactoryService());
        newdef.setConfigurator(parentDef.getConfigurator());
        newdef.setFile(parentDef.getFile());
        newdef.setPublic(parentDef.isPublic());

        # overwrite with values specified in the decorator:
        changes = definition.getChanges();
        if 'class' in changes :
            newdef.setClass(definition.getClass());

        if 'factory_class' in changes :
            newdef.setFactoryClass(definition.getFactoryClass());

        if 'factory_method' in changes :
            newdef.setFactoryMethod(definition.getFactoryMethod());

        if 'factory_service' in changes :
            newdef.setFactoryService(definition.getFactoryService());

        if 'configurator' in changes :
            newdef.setConfigurator(definition.getConfigurator());

        if 'file' in changes :
            newdef.setFile(definition.getFile());

        if 'public' in changes :
            newdef.setPublic(definition.isPublic());

        # UPDATED
        # merge arguments
        for index in definition.getOverwriteArguments():
            argument = definition.getOverwriteArguments()[index];

            newdef.replaceArgument(index, argument);


        # merge properties
        for k, v in definition.getProperties().items():
            newdef.setProperty(k, v);


        # append method calls
        calls = definition.getMethodCalls();
        if (len(calls) > 0) :
            newdef.setMethodCalls(newdef.getMethodCalls() + calls);


        # these attributes are always taken from the child
        newdef.setAbstract(definition.isAbstract());
        newdef.setScope(definition.getScope());
        newdef.setTags(definition.getTags());

        # set new definition on container
        self.__container.setDefinition(identifier, newdef);

        return newdef;


class CheckDefinitionValidityPass(CompilerPassInterface):
    """This pass validates each definition individually only taking the information
 * into account which is contained in the definition itself.
 *
 * Later passes can rely on the following, and specifically do not need to:
 * perform these checks themselves:
 *
 * - non synthetic, non @abstract
services always have a class set():
 * - synthetic services are always public
 * - synthetic services are always of non-prototype scope
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def process(self, container):
        """Processes the ContainerBuilder to validate the Definition.
     *
     * @param ContainerBuilder container
     *
     * @raise RuntimeException When the Definition is invalid

        """
        assert isinstance(container, ContainerBuilder);

        for identifier,  definition in container.getDefinitions().items():
            # synthetic service is public
            if (definition.isSynthetic() and  not definition.isPublic()) :
                raise RuntimeException(
                    'A synthetic service ("{0}") must be public.'.format(
                    identifier
                ));


            # synthetic service has non-prototype scope
            if (definition.isSynthetic() and ContainerInterface.SCOPE_PROTOTYPE == definition.getScope()) :
                raise RuntimeException(
                    'A synthetic service ("{0}") cannot be of scope '
                    '"prototype".'.format(
                    identifier
                ));


            # non-synthetic, non-abstract service has class
            if (not definition.isAbstract() and not definition.isSynthetic() and not definition.getClass()):
                if (definition.getFactoryClass() or definition.getFactoryService()) :
                    raise RuntimeException(
                        'Please add the class to service "{0}" even if it is '
                        'constructed by a factory since we might need to add '
                        'method calls based on compile-time checks.'.format(
                       identifier
                    ));


                raise RuntimeException(
                    'The definition for "{0}" has no class. If you intend to '
                    'inject this service dynamically at runtime, please mark '
                    'it as synthetic=True. If this is an abstract definition '
                    'solely used by child definitions, please add abstract '
                    'True, otherwise specify a class to get rid of this error.'
                    ''.format(
                   identifier
                ));


class ResolveReferencesToAliasesPass(CompilerPassInterface):
    """Replaces all references to aliases with references to the actual service.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self):
        self.__container = None;

    def process(self, container):
        """Processes the ContainerBuilder to replace references to aliases with actual service references.
     *
     * @param ContainerBuilder container

        """
        assert isinstance(container, ContainerBuilder);

        self.__container = container;

        for definition in container.getDefinitions().values():
            if (definition.isSynthetic() or definition.isAbstract()) :
                continue;


            definition.setArguments(self.__processArguments(definition.getArguments()));
            definition.setMethodCalls(self.__processArguments(definition.getMethodCalls()));
            definition.setProperties(self.__processArguments(definition.getProperties()));


        for identifier, alias in container.getAliases().items():
            aliasId = str(alias);
            defId = self.__getDefinitionId(aliasId);
            if aliasId  != defId :
                container.setAlias(identifier, Alias(defId, alias.isPublic()));




    def __processArguments(self, arguments):
        """Processes the arguments to replace aliases.
     *
     * @param list arguments An list of References
     *
     * @return array An array of References

        """
        assert isinstance(arguments, (list, dict));

        if isinstance(arguments, dict):
            keys = arguments.keys();
        else:
            keys = range(len(arguments));

        for k in keys:
            argument = arguments[k];
            if isinstance(argument, (list, dict)) :
                arguments[k] = self.__processArguments(argument);
            elif (isinstance(argument, Reference)) :
                identifier = str(argument);
                defId = self.__getDefinitionId(identifier);

                if (defId  != identifier) :
                    arguments[k] = Reference(defId, argument.getInvalidBehavior(), argument.isStrict());

        return arguments;


    def __getDefinitionId(self, identifier):
        """Resolves an alias into a definition identifier.
     *
     * @param string identifier The definition or alias identifier to resolve
     *
     * @return string The definition identifier with aliases resolved

        """

        while self.__container.hasAlias(identifier):
            identifier = str(self.__container.getAlias(identifier));


        return identifier;


class ResolveInvalidReferencesPass(CompilerPassInterface):
    """Emulates the invalid behavior if the reference is not found within the:
 * container.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self):
        self.__container = None;

    def process(self, container):
        """Process the ContainerBuilder to resolve invalid references.
     *
     * @param ContainerBuilder container

        """
        assert isinstance(container, ContainerBuilder);

        self.__container = container;
        for definition in container.getDefinitions().values():
            if (definition.isSynthetic() or definition.isAbstract()) :
                continue;


            definition.setArguments(
                self.__processArguments(definition.getArguments())
            );

            calls = list();
            for call in definition.getMethodCalls():
                try:
                    calls.append([call[0], self.__processArguments(call[1], True)]);
                except RuntimeException:
                    # this call is simply removed
                    pass;

            definition.setMethodCalls(calls);

            properties = dict();
            for name, value in definition.getProperties().items():
                try:
                    value = self.__processArguments([value], True);
                    properties[name] = value[0];
                except RuntimeException:
                    # ignore property
                    pass;


            definition.setProperties(properties);



    def __processArguments(self, arguments, inMethodCall = False):
        """Processes arguments to determine invalid references.
     *
     * @param array   arguments    An array of Reference objects
     * @param Boolean inMethodCall
     *
     * @return array
     *
     * @raise RuntimeException When the config is invalid

        """
        assert isinstance(arguments, (list, dict));

        if isinstance(arguments, dict):
            keys = arguments.keys();
        else:
            keys = range(len(arguments));

        for k in keys:
            argument = arguments[k];
            if isinstance(argument, (list, dict)) :
                arguments[k] = self.__processArguments(argument, inMethodCall);
            elif isinstance(argument, Reference) :
                identifier = str(argument);

                invalidBehavior = argument.getInvalidBehavior();
                exists = self.__container.has(identifier);

                # resolve invalid behavior
                if exists and ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE != invalidBehavior :
                    arguments[k] = Reference(identifier, ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE, argument.isStrict());
                elif ( not exists and ContainerInterface.NULL_ON_INVALID_REFERENCE == invalidBehavior) :
                    arguments[k] = None;
                elif ( not exists and ContainerInterface.IGNORE_ON_INVALID_REFERENCE == invalidBehavior) :
                    if (inMethodCall) :
                        raise RuntimeException("Method shouldn't be called.");


                    arguments[k] = None;

        return arguments;


class AnalyzeServiceReferencesPass(RepeatablePassInterface):
    """Run this pass before passes that need to know more about the relation of
 * your services.
 *
 * This class will(, populate the ServiceReferenceGraph with information. You can):
 * retrieve the graph in other passes from the compiler.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """


    def __init__(self, onlyConstructorArguments = False):
        """Constructor.
     *
     * @param Boolean onlyConstructorArguments Sets this Service Reference pass to ignore method calls

        """

        self.__graph = None;
        self.__container = None;
        self.__currentId = None;
        self.__currentDefinition = None;
        self.__repeatedPass = None;
        self.__onlyConstructorArguments = None;

        self.__onlyConstructorArguments = bool(onlyConstructorArguments);

    def setRepeatedPass(self, repeatedPass):
        """@inheritDoc

        """
        assert isinstance(repeatedPass, RepeatedPass);

        self.__repeatedPass = repeatedPass;


    def process(self, container):
        """Processes a ContainerBuilder object to populate the service reference graph.
     *
     * @param ContainerBuilder container

        """
        assert isinstance(container, ContainerBuilder);

        self.__container = container;
        self.__graph     = container.getCompiler().getServiceReferenceGraph();
        self.__graph.clear();

        for identifier, definition in container.getDefinitions().items():
            if definition.isSynthetic() or definition.isAbstract() :
                continue;


            self.__currentId = identifier;
            self.__currentDefinition = definition;
            self.__processArguments(definition.getArguments());

            if ( not self.__onlyConstructorArguments) :
                self.__processArguments(definition.getMethodCalls());
                self.__processArguments(definition.getProperties());
                if (definition.getConfigurator()) :
                    self.__processArguments([definition.getConfigurator()]);




        for identifier, alias in container.getAliases().items():
            self.__graph.connect(identifier, alias, str(alias), self.__getDefinition(str(alias)), None);



    def __processArguments(self, arguments):
        """Processes service definitions for arguments to find relationships for the service graph.
     *
     * @param array arguments An array of Reference or Definition objects relating to service definitions

        """
        assert isinstance(arguments, (list, dict));

        if isinstance(arguments, dict):
            keys = arguments.keys();
        else:
            keys = range(len(arguments));

        for k in keys:
            argument = arguments[k];
            if isinstance(argument, (list, dict)):
                self.__processArguments(argument);
            elif (isinstance(argument, Reference)) :
                self.__graph.connect(
                    self.__currentId,
                    self.__currentDefinition,
                    self.__getDefinitionId(str(argument)),
                    self.__getDefinition(str(argument)),
                    argument
                );
            elif (isinstance(argument, Definition)) :
                self.__processArguments(argument.getArguments());
                self.__processArguments(argument.getMethodCalls());
                self.__processArguments(argument.getProperties());




    def __getDefinition(self, identifier):
        """Returns a service definition given the full name or an alias.
     *
     * @param string identifier A full identifier or alias for a service definition.
     *
     * @return Definition|None The definition related to the supplied identifier

        """

        identifier = self.__getDefinitionId(identifier);

        if identifier is None:
            return None;
        else:
            return self.__container.getDefinition(identifier);


    def __getDefinitionId(self, identifier):

        while (self.__container.hasAlias(identifier)):
            identifier = str(self.__container.getAlias(identifier));


        if ( not self.__container.hasDefinition(identifier)) :
            return None;

        return identifier;

class CheckCircularReferencesPass(CompilerPassInterface):
    """Checks your services for circular references
 *
 * References from method calls are ignored since we might be able to resolve
 * these references depending on the order in which services are called.
 *
 * Circular reference from method calls will only be detected at run-time.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self):
        self.__currentId = None;
        self.__currentPath = None;

    def process(self, container):
        """Checks the ContainerBuilder object for circular references.
     *
     * @param ContainerBuilder container The ContainerBuilder instances

        """
        assert isinstance(container, ContainerBuilder);

        graph = container.getCompiler().getServiceReferenceGraph();

        for identifier, node in graph.getNodes().items():
            self.__currentId = identifier;
            self.__currentPath = [identifier];

            self.__checkOutEdges(node.getOutEdges());



    def __checkOutEdges(self, edges):
        """Checks for circular references.
     *
     * @param ServiceReferenceGraphEdge[] edges An array of Edges
     *
     * @raise ServiceCircularReferenceException When a circular reference is found.

        """
        assert isinstance(edges, list);

        for edge in edges:
            node = edge.getDestNode();
            identifier = node.getId();
            self.__currentPath.append(identifier);

            if self.__currentId == identifier :
                raise ServiceCircularReferenceException(self.__currentId, self.__currentPath);


            self.__checkOutEdges(node.getOutEdges());
            self.__currentPath.pop();



class CheckReferenceValidityPass(CompilerPassInterface):
    """Checks the validity of references
 *
 * The following checks are performed by this pass:
 * - target definitions are not abstract
 * - target definitions are of equal or wider scope
 * - target definitions are in the same scope hierarchy
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self):
        self.__container = None;
        self.__currentId = None;
        self.__currentDefinition = None;
        self.__currentScope = None;
        self.__currentScopeAncestors = None;
        self.__currentScopeChildren = None;

    def process(self, container):
        """Processes the ContainerBuilder to validate References.
     *
     * @param ContainerBuilder container

        """
        assert isinstance(container, ContainerBuilder);

        self.__container = container;

        children = self.__container.getScopeChildren();
        ancestors = dict();

        scopes = self.__container.getScopes();
        for name, parent in scopes.items():
            ancestors[name] = [parent];

            while parent in scopes :
                parent = scopes[parent];
                ancestors[name].append(parent);


        for identifier, definition in container.getDefinitions().items():
            if (definition.isSynthetic() or definition.isAbstract()) :
                continue;


            self.__currentId = identifier;
            self.__currentDefinition = definition;
            scope = definition.getScope();
            self.__currentScope = scope;

            if (ContainerInterface.SCOPE_CONTAINER == scope) :
                self.__currentScopeChildren = scopes.keys();
                self.__currentScopeAncestors = dict();
            elif (ContainerInterface.SCOPE_PROTOTYPE  != scope) :
                self.__currentScopeChildren = children[scope];
                self.__currentScopeAncestors = ancestors[scope];


            self.__validateReferences(definition.getArguments());
            self.__validateReferences(definition.getMethodCalls());
            self.__validateReferences(definition.getProperties());



    def __validateReferences(self, arguments):
        """Validates an array of References.
     *
     * @param array arguments An array of Reference objects
     *
     * @raise RuntimeException when there is a reference to an abstract 
                               definition.

        """
        assert isinstance(arguments, (list, dict));

        if isinstance(arguments, dict):
            keys = arguments.keys();
        else:
            keys = range(len(arguments));

        for k in keys:
            argument = arguments[k];
            if isinstance(argument, (list, dict)):
                self.__validateReferences(argument);
            elif (isinstance(argument, Reference)) :
                targetDefinition = self.__getDefinition(str(argument));

                if (None is not targetDefinition and targetDefinition.isAbstract()) :
                    raise RuntimeException(
                        'The definition "{0}" has a reference to an abstract'
                        'definition "{1}". Abstract definitions cannot be the '
                        'target of references.'.format(
                       self.__currentId,
                       argument
                    ));


                self.__validateScope(argument, targetDefinition);




    def __validateScope(self, reference, definition = None):
        """Validates the scope of a single Reference.
     *
     * @param Reference  reference
     * @param Definition definition
     *
     * @raise ScopeWideningInjectionException when the definition references a service of a narrower scope
     * @raise ScopeCrossingInjectionException when the definition references a service of another scope hierarchy

        """
        if definition is not None:
            assert isinstance(definition, Definition);
        assert isinstance(reference, Reference);

        if (ContainerInterface.SCOPE_PROTOTYPE == self.__currentScope) :
            return;


        if ( not reference.isStrict()) :
            return;


        if (None is definition) :
            return;

        scope = definition.getScope();
        if (self.__currentScope == scope) :
            return;


        identifier = str(reference);

        if scope in self.__currentScopeChildren :
            raise ScopeWideningInjectionException(self.__currentId, self.__currentScope, identifier, scope);


        if scope not in self.__currentScopeAncestors :
            raise ScopeCrossingInjectionException(self.__currentId, self.__currentScope, identifier, scope);



    def __getDefinition(self, identifier):
        """Returns the Definition given an identifier.
     *
     * @param string identifier Definition identifier:
     *
     * @return Definition

        """

        if ( not self.__container.hasDefinition(identifier)) :
            return None;


        return self.__container.getDefinition(identifier);


class RemovePrivateAliasesPass(CompilerPassInterface):
    """Remove private aliases from the container. They were only used to establish
 * dependencies between services, and these dependencies have been resolved in
 * one of the previous passes.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def process(self, container):
        """Removes private aliases from the ContainerBuilder
     *
     * @param ContainerBuilder container

        """
        assert isinstance(container, ContainerBuilder);

        compiler = container.getCompiler();
        formatter = compiler.getLoggingFormatter();

        for identifier, alias in container.getAliases().items():
            if (alias.isPublic()) :
                continue;


            container.removeAlias(identifier);
            compiler.addLogMessage(formatter.formatRemoveService(self, identifier, 'private alias'));



class RemoveAbstractDefinitionsPass(CompilerPassInterface):
    """Removes abstract Definitions
    """

    def process(self, container):
        """Removes abstract definitions from the ContainerBuilder
     *
     * @param ContainerBuilder container

        """
        assert isinstance(container, ContainerBuilder);

        compiler = container.getCompiler();
        formatter = compiler.getLoggingFormatter();

        for identifier, definition in container.getDefinitions().items():
            if (definition.isAbstract()) :
                container.removeDefinition(identifier);
                compiler.addLogMessage(formatter.formatRemoveService(self, identifier, 'abstract'));




class ReplaceAliasByActualDefinitionPass(CompilerPassInterface):
    """Replaces aliases with actual service definitions, effectively removing these
 * aliases.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self):
        self.__compiler = None;
        self.__formatter = None;
        self.__sourceId = None;

    def process(self, container):
        """Process the Container to replace aliases with service definitions.
     *
     * @param ContainerBuilder container
     *
     * @raise InvalidArgumentException if the service definition does not exist:

        """
        assert isinstance(container, ContainerBuilder);

        self.__compiler = container.getCompiler();
        self.__formatter = self.__compiler.getLoggingFormatter();

        for identifier, alias in container.getAliases().items():
            aliasId = str(alias);

            try:
                definition = container.getDefinition(aliasId);
            except InvalidArgumentException as e:
                raise InvalidArgumentException(
                    'Unable to replace alias "{0}" with "{1}".'.format(
                    alias, identifier
                ), None, e);


            if (definition.isPublic()) :
                continue;


            definition.setPublic(True);
            container.setDefinition(identifier, definition);
            container.removeDefinition(aliasId);

            self.__updateReferences(container, aliasId, identifier);

            # we have to restart the process due to concurrent modification of:
            # the container
            self.process(container);

            break;



    def __updateReferences(self, container, currentId, newId):
        """Updates references to remove aliases.
     *
     * @param ContainerBuilder container The container
     * @param string           currentId The alias identifier being replaced:
     * @param string           newId     The identifier of the service the alias points to

        """

        for identifier, alias in container.getAliases().items():
            if currentId == str(alias) :
                container.setAlias(identifier, newId);



        for identifier, definition in container.getDefinitions().items():
            self.__sourceId = identifier;

            definition.setArguments(
                self.__updateArgumentReferences(definition.getArguments(), currentId, newId)
            );

            definition.setMethodCalls(
                self.__updateArgumentReferences(definition.getMethodCalls(), currentId, newId)
            );

            definition.setProperties(
                self.__updateArgumentReferences(definition.getProperties(), currentId, newId)
            );



    def __updateArgumentReferences(self, arguments, currentId, newId):
        """Updates argument references.
     *
     * @param array  arguments An array of Arguments
     * @param string currentId The alias identifier:
     * @param string newId     The identifier the alias points to:
     *
     * @return array

        """
        assert isinstance(arguments, (list, dict));

        if isinstance(arguments, dict):
            keys = arguments.keys();
        else:
            keys = range(len(arguments));

        for k in keys:
            argument = arguments[k];
            if isinstance(argument, (list, dict)) :
                arguments[k] = self.__updateArgumentReferences(argument, currentId, newId);
            elif (isinstance(argument, Reference)) :
                if currentId == str(argument) :
                    arguments[k] = Reference(newId, argument.getInvalidBehavior());
                    self.__compiler.addLogMessage(self.__formatter.formatUpdateReference(self, self.__sourceId, currentId, newId));

        return arguments;




class InlineServiceDefinitionsPass(RepeatablePassInterface):
    """Inline service definitions where this is possible.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self):
        self.__repeatedPass = None;
        self.__graph = None;
        self.__compiler = None;
        self.__formatter = None;
        self.__currentId = None;

    def setRepeatedPass(self, repeatedPass):
        """@inheritDoc

        """
        assert isinstance(repeatedPass, RepeatedPass);

        self.__repeatedPass = repeatedPass;


    def process(self, container):
        """Processes the ContainerBuilder for inline service definitions.
     *
     * @param ContainerBuilder container

        """
        assert isinstance(container, ContainerBuilder);

        self.__compiler = container.getCompiler();
        self.__formatter = self.__compiler.getLoggingFormatter();
        self.__graph = self.__compiler.getServiceReferenceGraph();

        for identifier, definition in container.getDefinitions().items():
            self.__currentId = identifier

            definition.setArguments(
                self.__inlineArguments(container, definition.getArguments())
            );

            definition.setMethodCalls(
                self.__inlineArguments(container, definition.getMethodCalls())
            );

            definition.setProperties(
                self.__inlineArguments(container, definition.getProperties())
            );



    def __inlineArguments(self, container, arguments):
        """Processes inline arguments.
     *
     * @param ContainerBuilder container The ContainerBuilder
     * @param list            arguments A list of arguments
     *
     * @return list

        """
        assert isinstance(arguments, (list, dict));
        assert isinstance(container, ContainerBuilder);

        if isinstance(arguments, dict):
            keys = arguments.keys();
        else:
            keys = range(len(arguments));

        for k in keys:
            argument = arguments[k];

            if isinstance(argument, (list, dict)) :
                arguments[k] = self.__inlineArguments(container, argument);
            elif (isinstance(argument, Reference)) :
                identifier = str(argument);
                if not container.hasDefinition(identifier) :
                    continue;

                definition = container.getDefinition(identifier);
                if (self.__isInlineableDefinition(container, identifier, definition)) :
                    self.__compiler.addLogMessage(self.__formatter.formatInlineService(self, identifier, self.__currentId));

                    if (ContainerInterface.SCOPE_PROTOTYPE != definition.getScope()) :
                        arguments[k] = definition;
                    else :
                        arguments[k] = clone(definition);


            elif isinstance(argument, Definition) :
                argument.setArguments(self.__inlineArguments(container, argument.getArguments()));
                argument.setMethodCalls(self.__inlineArguments(container, argument.getMethodCalls()));
                argument.setProperties(self.__inlineArguments(container, argument.getProperties()));



        return arguments;


    def __isInlineableDefinition(self, container, identifier, definition):
        """Checks if the definition is inlineable.:
     *
     * @param ContainerBuilder container
     * @param string           identifier
     * @param Definition       definition
     *
     * @return Boolean If the definition is inlineable

        """
        assert isinstance(definition, Definition);
        assert isinstance(container, ContainerBuilder);

        if (ContainerInterface.SCOPE_PROTOTYPE == definition.getScope()) :
            return True;


        if (definition.isPublic()) :
            return False;


        if ( not self.__graph.hasNode(identifier)) :
            return True;


        ids = list();
        for edge in self.__graph.getNode(identifier).getInEdges():
            ids.append(edge.getSourceNode().getId());


        if (len(Array.uniq(ids)) > 1) :
            return False;


        return container.getDefinition(ids[0]).getScope() == definition.getScope();

class RemoveUnusedDefinitionsPass(RepeatablePassInterface):
    """Removes unused service definitions from the container.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self):
        self.__repeatedPass = None;

    def setRepeatedPass(self, repeatedPass):
        """@inheritDoc

        """
        assert isinstance(repeatedPass, RepeatedPass);

        self.__repeatedPass = repeatedPass;


    def process(self, container):
        """Processes the ContainerBuilder to remove unused definitions.
     *
     * @param ContainerBuilder container

        """
        assert isinstance(container, ContainerBuilder);

        compiler = container.getCompiler();
        formatter = compiler.getLoggingFormatter();
        graph = compiler.getServiceReferenceGraph();

        hasChanged = False;
        definitions = container.getDefinitions().copy();
        for identifier, definition in definitions.items():
            if (definition.isPublic()) :
                continue;


            if (graph.hasNode(identifier)) :
                edges = graph.getNode(identifier).getInEdges();
                referencingAliases = list();
                sourceIds = list();
                for edge in edges:
                    node = edge.getSourceNode();
                    sourceIds.append(node.getId());

                    if (node.isAlias()) :
                        referencingAliases.append(node.getValue());


                isReferenced = (len(Array.uniq(sourceIds)) - len(referencingAliases)) > 0;
            else :
                referencingAliases = list();
                isReferenced = False;


            if (1 == len(referencingAliases) and False is isReferenced) :
                container.setDefinition(str(referencingAliases[0]), definition);
                definition.setPublic(True);
                container.removeDefinition(identifier);
                compiler.addLogMessage(formatter.formatRemoveService(self, identifier, 'replaces alias '+referencingAliases[0]));
            elif (0 == len(referencingAliases) and False is isReferenced) :
                container.removeDefinition(identifier);
                compiler.addLogMessage(formatter.formatRemoveService(self, identifier, 'unused'));
                hasChanged = True;



        if (hasChanged) :
            self.__repeatedPass.setRepeat();


class CheckExceptionOnInvalidReferenceBehaviorPass(CompilerPassInterface):
    """Checks that all references are pointing to a valid service.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self):
        self.__container = None;
        self.__sourceId = None;

    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        self.__container = container;

        for identifier, definition in container.getDefinitions().items():
            self.__sourceId = identifier;
            self.__processDefinition(definition);



    def __processDefinition(self, definition):
        assert isinstance(definition, Definition);

        self.__processReferences(definition.getArguments());
        self.__processReferences(definition.getMethodCalls());
        self.__processReferences(definition.getProperties());


    def __processReferences(self, arguments):
        assert isinstance(arguments, (list, dict));

        if isinstance(arguments, dict):
            keys = arguments.keys();
        else:
            keys = range(len(arguments));

        for k in keys:
            argument = arguments[k];

            if isinstance(argument, (list, dict)) :
                self.__processReferences(argument);
            elif (isinstance(argument, Definition)) :
                self.__processDefinition(argument);
            elif (isinstance(argument, Reference) and ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE == argument.getInvalidBehavior()) :
                destId = str(argument);

                if ( not self.__container.has(destId)) :
                    raise ServiceNotFoundException(destId, self.__sourceId);
