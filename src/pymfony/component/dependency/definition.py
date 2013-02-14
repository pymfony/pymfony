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


from pymfony.component.system import Object
from pymfony.component.dependency.exception import OutOfBoundsException
from pymfony.component.dependency.exception import InvalidArgumentException
from pymfony.component.system import Tool
from pymfony.component.dependency.interface import ContainerInterface

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


class Reference(Object):
    """Reference represents a service reference.

    @author: Fabien Potencier <fabien@symfony.com>

    @api

    """


    def __init__(self, identifier, invalidBehavior = ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE, strict = True):
        """Constructor.

        @param: string  id              The service identifier:
        @param int     invalidBehavior The behavior when the service does not exist
        @param Boolean strict          Sets how this reference is validated

        @see Container

        """

        self.__id = None;
        self.__invalidBehavior = None;
        self.__strict = None;

        self.__id = str(identifier).lower();
        self.__invalidBehavior = invalidBehavior;
        self.__strict = strict;


    def __str__(self):
        """__str__.

        @return: string The service identifier:

        """

        return str(self.__id);


    def getInvalidBehavior(self):
        """Returns the behavior to be used when the service does not exist.

        @return: int

        """

        return self.__invalidBehavior;


    def isStrict(self):
        """Returns True when this Reference is strict

        @return: Boolean

        """

        return self.__strict;




class Definition(Object):
    """Definition represents a service definition.

    @author: Fabien Potencier <fabien@symfony.com>

    @api

    """
    def __init__(self, className=None, arguments=None):
        """Constructor.

        @param: string class The service class):
        @param array  arguments An array of arguments to pass to the service constructor

        @api

        """
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
        self.__scope = ContainerInterface.SCOPE_CONTAINER;

    def setFactoryClass(self, factoryClass):
        """Sets the name of the class that(, acts as a factory using the factory method,):
        which will be invoked statically.

        @param: string factoryClass The factory class name(Object):

        @return Definition The current instance

        @api

        """
        self.__factoryClass = factoryClass;
        return self;

    def getFactoryClass(self):
        """Gets the factory class.

        @return: string The factory class name(Object):

        @api

        """
        return self.__factoryClass;

    def setFactoryMethod(self, factoryMethod):
        """Sets the factory method able to create an instance of this class.

        @param: string factoryMethod The factory method name

        @return Definition The current instance

        @api

        """
        self.__factoryMethod = factoryMethod;
        return self;

    def getFactoryMethod(self):
        """Gets the factory method.

        @return: string The factory method name

        @api

        """
        return self.__factoryMethod;

    def setFactoryService(self, factoryService):
        """Sets the name of the service that acts as a factory using the factory method.

        @param: string factoryService The factory service id

        @return Definition The current instance

        @api

        """
        self.__factoryService = factoryService;
        return self;

    def getFactoryService(self):
        """Gets the factory service id.

        @return: string The factory service id

        @api

        """
        return self.__factoryService;

    def setClass(self, className):
        """Sets the service class.

        @param: string class The(, service class):

        @return Definition The current instance

        @api

        """
        self.__class = className;
        return self;

    def getClass(self):
        """Gets the service class.

        @return: string The service class

        @api

        """
        return self.__class;

    def setArguments(self, arguments):
        """Sets the arguments to pass to the service constructor/factory method.

        @param: list arguments An array of arguments

        @return Definition The current instance

        @api

        """
        assert isinstance(arguments, list);
        self._arguments = arguments;
        return self;

    def setProperties(self, properties):
        """@api:

        @param: dict properties An array of properties
        """
        assert isinstance(properties, dict)
        self.__properties = properties;
        return self;

    def getProperties(self):
        """@api:

        @return dict
        """
        return self.__properties;

    def setProperty(self, key, value):
        """@api:

        """
        self.__properties[key] = value;
        return self;

    def addArgument(self, argument):
        """Adds an argument to pass to the service constructor/factory method.

        @param: mixed argument An argument

        @return Definition The current instance

        @api

        """
        self._arguments.append(argument);
        return self;

    def replaceArgument(self, index, argument):
        """Sets a specific argument:

        @param: integer index
        @param mixed   argument

        @return Definition The current instance

        @raise OutOfBoundsException When the replaced argument does not exist

        @api

        """
        if index < 0 or index > len(self._arguments) - 1:
            raise OutOfBoundsException(
                'The index "{!d}" is not in the range [0, {!d}].'
                ''.format(index, len(self._arguments) - 1)
            );
        self._arguments[index] = argument;
        return self;

    def getArguments(self):
        """Gets the arguments to pass to the service constructor/factory method.

        @return: array The array of arguments

        @api

        """
        return self._arguments;

    def getArgument(self, index):
        """Gets an argument to pass to the service constructor/factory method.

        @param: integer index

        @return mixed The argument value

        @raise OutOfBoundsException When the argument does not exist

        @api

        """
        if index < 0 or index > len(self._arguments) - 1:
            raise OutOfBoundsException(
                'The index "{!d}" is not in the range [0, {!d}].'
                ''.format(index, len(self._arguments) - 1)
            );
        return self._arguments[index];

    def setMethodCalls(self, calls):
        """Sets the methods to call after service initialization.

        @param: list calls An array of method calls
                     list of [methodName, [arg1, ...]]

        @return Definition The current instance

        @api

        """
        assert isinstance(calls, list);
        self.__calls = list();
        for call in calls:
            assert isinstance(call, list);
            self.addMethodCall(call[0], call[1]);
        return self;

    def addMethodCall(self, method, arguments=[]):
        """Adds a method to call after service initialization.

        @param: string method    The method name to call
        @param array  arguments An array of arguments to pass to the method call

        @return Definition The current instance

        @raise InvalidArgumentException on empty method param

        @api

        """
        arguments = list(arguments);
        method = str(method);
        if not method:
            raise InvalidArgumentException('Method name cannot be empty.');
        self.__calls.append([method, arguments]);
        return self;

    def removeMethodCall(self, method):
        """Removes a method to call after service initialization.

        @param: string method The method name to remove

        @return Definition The current instance

        @api

        """
        i = -1;
        for call in self.__calls:
            i += 1;
            if call[0] == method:
                del self.__calls[i];
                break;
        return self;

    def hasMethodCall(self, method):
        """Check if the current definition has a given method to call after service initialization.:

        @param: string method The method name to search for

        @return Boolean

        @api

        """
        for call in self.__calls:
            if call[0] == method:
                return True;
        return False;

    def getMethodCalls(self):
        """Gets the methods to call after service initialization.

        @return: list An array of method calls

        @api

        """

        return self.__calls;

    def setTags(self, tags):
        """Sets tags for this definition

        @param: dict tags

        @return Definition the current instance

        @api

        """
        assert isinstance(tags, dict);
        self.__tags = tags;
        return self;

    def getTags(self):
        """Returns all tags.

        @return: dict An array of tags

        @api

        """

        return self.__tags;

    def getTag(self, name):
        """Gets a tag by name.

        @param: string name The tag name

        @return list An array of attributes

        @api

        """
        if name in self.__tags:
            return self.__tags[name];
        else:
            return list();

    def addTag(self, name, attributes=[]):
        """Adds a tag for this definition.

        @param: string name       The tag name
        @param list  attributes An array of attributes

        @return Definition The current instance

        @api

        """
        attributes = list(attributes);
        if name not in self.__tags:
            self.__tags[name] = list();
        self.__tags[name].append(attributes);
        return self;

    def hasTag(self, name):
        """Whether this definition has a tag with the given name

        @param: string name

        @return Boolean

        @api

        """
        return name in self.__tags;

    def clearTag(self, name):
        """Clears all tags for a given name.

        @param: string name The tag name

        @return Definition

        """
        if self.hasTag(name):
            del self.__tags[name];
        return self;

    def clearTags(self):
        """Clears the tags for this definition.

        @return: Definition The current instance

        @api

        """
        self.__tags = dict();
        return self;

    def setFile(self, filename):
        """Sets a file to require before creating the service.

        @param: string file A full pathname to include

        @return Definition The current instance

        @api

        """
        self.__file = filename;
        return self;

    def getFile(self):
        """Gets the file to require before creating the service.

        @return: string The full pathname to include

        @api

        """
        return self.__file;

    def setScope(self, scope):
        """Sets the scope of the service

        @param: string scope Whether the service must be shared or not

        @return Definition The current instance

        @api

        """

        self.__scope = scope;

        return self;


    def getScope(self):
        """Returns the scope of the service

        @return: string

        @api

        """

        return self.__scope;

    def setPublic(self, boolean):
        """Sets the visibility of this service.

        @param: Boolean boolean

        @return Definition The current instance

        @api

        """
        self.__public = bool(boolean);
        return self;

    def isPublic(self):
        """Whether this service is public facing

        @return: Boolean

        @api

        """
        return self.__public;
                
    def setSynthetic(self, boolean):
        """Sets whether this definition is synthetic, that is not constructed by the
        container, but dynamically injected.

        @param: Boolean boolean

        @return Definition the current instance

        @api

        """

        self.__synthetic = bool(boolean);
        return self;

    def isSynthetic(self):
        """Whether this definition is synthetic, that is not constructed by the
        container, but dynamically injected.

        @return: Boolean

        @api

        """
        return self.__synthetic;

    def setAbstract(self, boolean):
        """Whether this definition is abstract, that means it merely serves as a
        template for other definitions.

        @param: Boolean boolean

        @return Definition the current instance

        @api

        """

        self.__abstract = bool(boolean);

        return self;

    def isAbstract(self):
        """Whether this definition is abstract, that means it merely serves as a
        template for other definitions.

        @return: Boolean

        @api

        """

        return self.__abstract;


    def setConfigurator(self, closure):
        """Sets a configurator to call after the service is fully initialized.

        @param: callable callable A PYTHON callable

        @return Definition The current instance

        @api

        """
        self.__configurator = closure;
        return self;

    def getConfigurator(self):
        """Gets the configurator to call after the service is fully initialized.

        @return: callable The PHP callable to call

        @api

        """
        return self.__configurator;


class DefinitionDecorator(Definition):
    """This definition decorates another definition.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>
 *
 * @api

    """

    def __init__(self, parent):
        """Constructor.
     *
     * @param string parent The id of Definition instance to decorate.
     *
     * @api

        """

        Definition.__init__(self);

        self.__parent = None;
        self.__changes = None;
        self.__overwriteArguments = None;

        self.__parent = parent;
        self.__changes = dict();
        self.__overwriteArguments = dict();


    def getParent(self):
        """Returns the Definition being decorated.
     *
     * @return string
     *
     * @api

        """

        return self.__parent;


    def getChanges(self):
        """Returns all changes tracked for the Definition object.
     *
     * @return array An array of changes for this Definition
     *
     * @api

        """

        return self.__changes;

    def getOverwriteArguments(self):
        """Returns all overwrite arguments for the Definition object.
     *
     * @return dict A dict of overwrite arguments for the Definition object.
     *
     * @api

        """

        return self.__overwriteArguments;


    def setClass(self, className):
        """@inheritDoc
     *
     * @api

        """

        self.__changes['class'] = True;

        return Definition.setClass(self, className);


    def setFactoryClass(self, className):
        """@inheritDoc}
     *
     * @api

        """

        self.__changes['factory_class'] = True;

        return Definition.setFactoryClass(self, className);


    def setFactoryMethod(self, method):
        """@inheritDoc}
     *
     * @api

        """

        self.__changes['factory_method'] = True;

        return Definition.setFactoryMethod(self, method);


    def setFactoryService(self, service):
        """@inheritDoc}
     *
     * @api

        """

        self.__changes['factory_service'] = True;

        return Definition.setFactoryService(self, service);


    def setConfigurator(self, closure):
        """@inheritDoc}
     *
     * @api

        """

        self.__changes['configurator'] = True;

        return Definition.setConfigurator(self, closure);


    def setFile(self, filename):
        """@inheritDoc}
     *
     * @api

        """

        self.__changes['file'] = True;

        return Definition.setFile(self, filename);


    def setPublic(self, boolean):
        """@inheritDoc}
     *
     * @api

        """

        self.__changes['public'] = True;

        return Definition.setPublic(self, boolean);


    def getArgument(self, index):
        """Gets an argument to pass to the service constructor/factory method.
     *
     * If replaceArgument() has been used to replace an argument, this method
     * will return the replacement value.
     *
     * @param integer index
     *
     * @return mixed The argument value
     *
     * @raise OutOfBoundsException When the argument does not exist
     *
     * @api

        """
        index = int(index);

        # UPDATED
        try:
            return self.__overwriteArguments[index];
        except IndexError:
            pass;

        lastIndex = len(self._arguments) - 1;

        if (index < 0 or index > lastIndex) :
            raise OutOfBoundsException(
                'The index "{0!d}" is not in the range [0, {1!d}].'.format(
                    index,
                    len(self._arguments) - 1
            ));

        return self._arguments[index];


    def replaceArgument(self, index, value):
        """You should always use this method when overwriting existing arguments
     * of the parent definition.
     *
     * If you directly call setArguments() keep in mind that you must follow
     * certain conventions when you want to overwrite the arguments of the
     * parent definition, otherwise your arguments will only be appended.
     *
     * @param integer index
     * @param mixed   value
     *
     * @return DefinitionDecorator the current instance
     * @raise InvalidArgumentException when index isn't an integer
     *
     * @api

        """

        if not isinstance(index, int) or isinstance(index, bool):
            raise InvalidArgumentException('index must be an integer.');

        # UPDATED
        self.__overwriteArguments[index] = value;

        return self;

