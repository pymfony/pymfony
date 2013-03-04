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

"""
"""

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
class ContainerInterface(Object):
    """ContainerInterface is the interface implemented by service container classes.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>
 *
 * @api

    """

    EXCEPTION_ON_INVALID_REFERENCE = 1;
    NULL_ON_INVALID_REFERENCE      = 2;
    IGNORE_ON_INVALID_REFERENCE    = 3;
    SCOPE_CONTAINER                = 'container';
    SCOPE_PROTOTYPE                = 'prototype';

    def set(self, identifier, service, scope = SCOPE_CONTAINER):
        """Sets a service.
     *
     * @param string identifier The service identifier:
     * @param object service    The service instance
     * @param string scope      The scope of the service
     *
     * @api

        """

    def get(self, identifier, invalidBehavior = EXCEPTION_ON_INVALID_REFERENCE):
        """Gets a service.
     *
     * @param string identifier      The service identifier:
     * @param int    invalidBehavior The behavior when the service does not exist
     *
     * @return object The associated service
     *
     * @raise InvalidArgumentException if the service is not defined:
     * @raise ServiceCircularReferenceException When a circular reference is detected
     * @raise ServiceNotFoundException When the service is not defined
     *
     * @see Reference
     *
     * @api

        """

    def has(self, identifier):
        """Returns True if the given service is defined.:
     *
     * @param string identifier The service identifier:
     *
     * @return Boolean True if the service is defined, False otherwise:
     *
     * @api

        """

    def getParameter(self, name):
        """Gets a parameter.
     *
     * @param string name The parameter name
     *
     * @return mixed  The parameter value
     *
     * @raise InvalidArgumentException if the parameter is not defined:
     *
     * @api

        """

    def hasParameter(self, name):
        """Checks if a parameter exists.:
     *
     * @param string name The parameter name
     *
     * @return Boolean The presence of parameter in container
     *
     * @api

        """

    def setParameter(self, name, value):
        """Sets a parameter.
     *
     * @param string name  The parameter name
     * @param mixed  value The parameter value
     *
     * @api

        """

    def enterScope(self, name):
        """Enters the given scope
     *
     * @param string name
     *
     * @api

        """

    def leaveScope(self, name):
        """Leaves the current scope, and re-enters the parent scope
     *
     * @param string name
     *
     * @api

        """

    def addScope(self, scope):
        """Adds a scope to the container
     *
     * @param ScopeInterface scope
     *
     * @api

        """
        assert isinstance(scope, ScopeInterface);

    def hasScope(self, name):
        """Whether this container has the given scope
     *
     * @param string name
     *
     * @return Boolean
     *
     * @api

        """

    def isScopeActive(self, name):
        """Determines whether the given scope is currently active.
     *
     * It does however not check if the scope actually exists.:
     *
     * @param string name
     *
     * @return Boolean
     *
     * @api

        """


@interface
class ContainerAwareInterface(Object):
    def setContainer(self, container):
        """Sets the Container.

        @param container: ContainerInterface A ContainerInterface instance
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
class IntrospectableContainerInterface(ContainerInterface):
    """IntrospectableContainerInterface defines additional introspection functionality
    for containers, allowing logic to be implemented based on a Container's state.

    @author: Evan Villemez <evillemez@gmail.com>


    """

    def initialized(self, identifier):
        """Check for whether or not a service has been initialized.

        @param: string identifier

        @return: Boolean True if the service has been initialized, False otherwise


        """


@interface
class ScopeInterface(Object):
    """Scope Interface.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>
 *
 * @api

    """

    def getName(self):
        """@api

        """

    def getParentName(self):
        """@api

        """


@interface
class CompilerPassInterface(Object):
    """Interface that must be implemented by compilation passes
    """
    def process(self, container):
        """You can modify the container here before it is dumped to PHP code.

        @param container: ContainerBuilder
        """
        pass;


@interface
class RepeatablePassInterface(CompilerPassInterface):
    """Interface that must be implemented by passes that are run as part of an
 * RepeatedPass.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def setRepeatedPass(self, repeatedPass):
        """Sets the RepeatedPass interface.
     *
     * @param RepeatedPass repeatedPass

        """
