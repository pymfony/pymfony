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

import os.path;
import urlparse;
from pickle import dumps as serialize;
from pickle import loads as unserialize;
import json;

from pymfony.component.system import Object, abstract, interface;
from pymfony.component.system import Array;
from pymfony.component.system import Tool;

__all__ = [
    'FileLocator'
];

@interface
class FileLocatorInterface(Object):
    def locate(self, name, currentPath=None, first=True):
        """Returns a full path for a given file name.
        
        @param name: mixed The file name to locate
        @param currentPath: string The current path
        @param first: boolean Whether to return the first occurrence 
                      or an array of filenames
        """
        pass;

@interface
class LoaderResolverInterface(Object):
    """LoaderResolverInterface selects a loader for a given resource.
    """
    def resolve(self, resource, resourceType=None):
        """Returns a loader able to load the resource.

        @param resource: mixed
        @param resourceType: string The resource type

        @return: LoaderInterface|false A LoaderInterface instance
        """
        pass;

@interface
class LoaderInterface(Object):
    def load(self, resource, resourceType=None):
        """Loads a resource.

        @param resource: mixed
        @param resourceType: string The resource type
        """
        pass;

    def supports(self, resource, resourceType=None):
        """Returns true if this class supports the given resource.

        @param resource: mixed
        @param resourceType: string The resource type

        @return: Boolean
        """
        pass;

    def getResolver(self):
        """Gets the loader resolver.

        @return: LoaderResolverInterface A LoaderResolverInterface instance
        """
        pass;

    def setResolver(self, resolver):
        """Sets the loader resolver.

        @param resolver: LoaderResolverInterface A LoaderResolverInterface
            instance
        """
        pass;

@interface
class ResourceInterface(Object):
    """ResourceInterface is the interface that must be implemented
    by all Resource classes.
    """
    def toString(self):
        """Returns a string representation of the Resource.

        @return: string
        """
        pass;

    def isFresh(self, timestamp):
        """Returns true if the resource has not been updated
        since the given timestamp.

        @param timestamp: int The last time the resource was loaded

        @return: Boolean
        """
        pass;

    def getResource(self):
        """Returns the resource tied to this Resource.

        @return: mixed The resource
        """
        pass;

@interface
class SerializableInterface(Object):
    def serialize(self):
        pass;

    def unserialize(self, serialized):
        pass;

@interface
class ConfigurationInterface(Object):
    def getConfigTreeBuilder(self):
        """Generates the configuration tree builder.

        @return: TreeBuilder The tree builder
        """
        pass;

@interface
class NodeParentInterface(Object):
    pass;

@interface
class NodeInterface(Object):
    def getName(self):
        """Returns the name of the node.

        @return: string
        """
        pass;

    def getPath(self):
        """Returns the path of the node.

        @return: string
        """
        pass;

    def isRequired(self):
        """Returns true when the node is required.

        @return: boolean
        """
        pass;

    def hasDefaultValue(self):
        """Returns true when the node has a default value.

        @return: Boolean
        """
        pass;

    def getDefaultValue(self):
        """Returns the default value of the node.

        @return: mixed

        @raise RuntimeException: if the node has no default value
        """
        pass;

    def normalize(self, value):
        """Normalizes the supplied value.

        @param value: mixed The value to normalize

        @return: mixed The normalized value
        """
        pass;

    def merge(self, leftSide, rightSide):
        """Merges two values together.

        @param leftSide: mixed
        @param rightSide: mixed

        @return: mixed The merged values
        """
        pass;

    def finalize(self, value):
        """Finalizes a value.

        @param value: mixed The value to finalize

        @return: mixed The finalized value
        """
        pass;

@interface
class ParentNodeDefinitionInterface(Object):
    def children(self):
        pass;

    def append(self, node):
        """
        @param node: NodeDefinition
        """
        pass;

    def setBuilder(self, builder):
        """
        @param builder: NodeBuilder
        """
        pass;

@interface
class PrototypeNodeInterface(NodeInterface):
    def setName(self, name):
        """Sets the name of the node.

        @param name: string The name of the node
        """
        pass;

class BaseNode(NodeInterface):
    """The base node class"""
    def __init__(self, name, parent=None):
        """Constructor.

        @param name: string The name of the node
        @param parent: NodeInterface The parent of this node

        @raise InvalidArgumentException: if the name contains a period.
        """
        assert isinstance(name, basestring);
        if parent is not None:
            assert isinstance(parent, NodeInterface);

        self._attributes = dict();

        self._name = name;
        self._parent = parent;
        self._normalizationClosures = list();
        self._finalValidationClosures = list();
        self._allowOverwrite = True;
        self._required = False;
        self._equivalentValues = list();

        if '.' in name:
            raise InvalidArgumentException('The name must not contain ".".');

    def setAttribute(self, key, value):
        self._attributes[key] = value;

    def hasAttribute(self, key):
        return key in self._attributes;

    def getAttribute(self, key, default=None):
        if self.hasAttribute(key):
            return self._attributes[key];
        return default;

    def getAttributes(self, key):
        return self._attributes;

    def setAttributes(self, attributes):
        assert isinstance(attributes, dict);
        self._attributes = attributes;

    def removeAttribute(self, key):
        return self._attributes.pop(key);

    def setInfo(self, info):
        """Sets an info message.

        @param info: string
        """
        self.setAttribute('info', info);

    def getInfo(self):
        """Returns info message.

        @return: string The info message.
        """
        return self.getAttribute('info');

    def setExample(self, example):
        """Sets the example configuration for this node.

        @param example: string|array
        """
        self.setAttribute('example', example);

    def getExample(self):
        """Retrieves the example configuration for this node.

        @return: string|array
        """
        return self.getAttribute('example');

    def addEquivalentValue(self, originalValue, equivalentValue):
        """Adds an equivalent value.

        @param originalValue: mixed
        @param equivalentValue: mixed
        """
        self._equivalentValues.append([originalValue, equivalentValue]);

    def setRequired(self, boolean):
        """Set this node as required.

        @param boolean: Boolean Required node
        """
        self._required = bool(boolean);

    def setAllowOverwrite(self, allow):
        """Sets if this node can be overridden.

        @param allow: Boolean
        """
        self._allowOverwrite = bool(allow);

    def setNormalizationClosures(self, closures):
        """Sets the closures used for normalization.

        @param closures: callable[] An array of Closures used for normalization
        """
        assert isinstance(closures, list);
        self._normalizationClosures = closures;

    def setFinalValidationClosures(self, closures):
        """Sets the closures used for final validation.

        @param closures: callable[] An array of Closures used 
            for final validation
        """
        assert isinstance(closures, list);
        self._finalValidationClosures = closures;

    def isRequired(self):
        return self._required;

    def getName(self):
        return self._name;

    def getPath(self):
        path = self._name;
        if not self._parent is None:
            path = ".".join([self._parent.getPath()]);
        return path;

    def merge(self, leftSide, rightSide):
        """@final:
        """
        if not self._allowOverwrite:
            raise ForbiddenOverwriteException(
                'Configuration path "{0}" cannot be overwritten. You have to '
                'define all options for this path, and any of its sub-paths '
                'in one configuration section.'.format(self.getPath())
            );

        self._validateType(leftSide);
        self._validateType(rightSide);

        return self._mergeValues(leftSide, rightSide);

    def normalize(self, value):
        """Normalizes a value, applying all normalization closures.

        @final:

        @return: mixed The normalized value.
        """
        # pre-normalize value
        value  = self._preNormalize(value);

        # run custom normalization closures
        for closure in self._normalizationClosures:
            value = closure(value);

        # replace value with their equivalent
        for data in self._equivalentValues:
            if data[0] == value:
                value = data[1];

        # validate type
        self._validateType(value);

        # normalize value
        return self._normalizeValue(value);

    def _preNormalize(self, value):
        """Normalizes the value before any other normalization is applied.

        @return: mixed The normalized array value
        """
        return value;

    def finalize(self, value):
        """@final:"""
        self._validateType(value);
        value = self._finalizeValue(value);

        # Perform validation on the final value if a closure has been set.
        # The closure is also allowed to return another value.
        for closure in self._finalValidationClosures:
            try:
                value = closure(value);
            except ConfigException as correctEx:
                raise correctEx;
            except Exception as invalid:
                raise InvalidConfigurationException(
                    'Invalid configuration for path "{0}": {1}'
                    ''.format(self.getPath(), invalid.message)
                );
        return value;

    @abstract
    def _validateType(self, value):
        """Validates the type of a Node.

        @param value: mixed The value to validate

        @raise InvalidTypeException: When the value is invalid
        """
        pass;

    @abstract
    def _normalizeValue(self, value):
        """Normalizes the value.

        @param value: mixed The value to normalize.

        @return: mixed The normalized value
        """
        pass;

    @abstract
    def _mergeValues(self, leftSide, rightSide):
        """Merges two values together.

        @param leftSide: mixed
        @param rightSide: mixed

        @return: mixed
        """
        pass;

    @abstract
    def _finalizeValue(self, value):
        """Finalizes a value.

        @param value: The value to finalize

        @return: mixed The finalized value
        """
        pass;

class VariableNode(BaseNode, PrototypeNodeInterface):
    """This node represents a value of variable type in the config tree.

    This node is intended for values of arbitrary type.
    Any PYTHON type is accepted as a value.
    """
    def __init__(self, name, parent=None):
        BaseNode.__init__(self, name, parent=parent);
        self._defaultValueSet = False;
        self._defaultValue = None;
        self._allowEmptyValue = True;

    def setDefaultValue(self, value):
        self._defaultValueSet = True;
        self._defaultValue = value;

    def hasDefaultValue(self):
        return self._defaultValueSet;

    def getDefaultValue(self):
        if Tool.isCallable(self._defaultValue):
            return eval(self._defaultValue)();
        else:
            return self._defaultValue;

    def setAllowEmptyValue(self, boolean):
        """Sets if this node is allowed to have an empty value.

        @param boolean: Boolean
        """
        self._allowEmptyValue = bool(boolean);

    def setName(self, name):
        self._name = name;

    def _validateType(self, value):
        pass;

    def _finalizeValue(self, value):
        if not self._allowEmptyValue and not value:
            ex = InvalidConfigurationException(
                'The path "{0}" cannot contain an empty value, but got {1}.'
                ''.format(self.getPath(), json.dumps(value))
            );
            ex.setPath(self.getPath());
            raise ex;
        return value;

    def _normalizeValue(self, value):
        return value;

    def _mergeValues(self, leftSide, rightSide):
        return rightSide;

class ScalarNode(VariableNode):
    def _validateType(self, value):
        if not isinstance(value,(type(None),basestring,int,float,bool)) and \
            not value is None:
            ex = InvalidTypeException(
                'Invalid type for path "{0}". Expected scalar, but got {1}.'
                ''.format(self.getPath(), type(value).__name__)
            );
            ex.setPath(self.getPath());
            raise ex;

class BooleanNode(ScalarNode):
    def _validateType(self, value):
        if not isinstance(value, bool):
            ex = InvalidTypeException(
                'Invalid type for path "{0}". Expected boolean, but got {1}.'
                ''.format(self.getPath(), type(value).__name__)
            );
            ex.setPath(self.getPath());
            raise ex;

class ArrayNode(BaseNode, PrototypeNodeInterface):
    def __init__(self, name, parent=None):
        BaseNode.__init__(self, name, parent=parent);

        self._xmlRemappings = list();
        self._children = dict();
        self._allowFalse = False;
        self._allowNewKeys = True;
        self._addIfNotSet = False;
        self._performDeepMerging = True;
        self._ignoreExtraKeys = None;
        self._normalizeKeys = True;

    def setNormalizeKeys(self, normalizeKeys):
        self._normalizeKeys = bool(normalizeKeys);

    def _preNormalize(self, value):
        if not self._normalizeKeys or not isinstance(value, dict):
            return value;

        for k, v in value.items():
            if '-' in k:
                if not '_' in k:
                    normalizedKey = str(k).replace('-', '_');
                    if not normalizedKey in value:
                        value[normalizedKey] = v;
                        value.pop(k);

        return value;

    def getChildren(self):
        """Retrieves the children of this node.

        @return: dict The children
        """
        return self._children;

    def setXmlRemappings(self, xmlRemappings):
        """Sets the xml remappings that should be performed.

        @param xmlRemappings: an list of the form list(list(string, string))
        """
        self._xmlRemappings = list(xmlRemappings);

    def setAddIfNotSet(self, boolean):
        """Sets whether to add default values for this array if it has not
        been defined in any of the configuration files.

        @param boolean: Boolean
        """
        self._addIfNotSet = bool(boolean);

    def setAllowFalse(self, allow):
        """Sets whether false is allowed as value indicating that
        the array should be unset.

        @param allow: Boolean
        """
        self._allowFalse = bool(allow);

    def setAllowNewKeys(self, allow):
        """Sets whether new keys can be defined in subsequent configurations.

        @param allow: Boolean
        """
        self._allowNewKeys = bool(allow);

    def setPerformDeepMerging(self, boolean):
        """Sets if deep merging should occur.

        @param boolean: Boolean
        """
        self._performDeepMerging = bool(boolean);

    def setIgnoreExtraKeys(self, boolean):
        """Whether extra keys should just be ignore without an exception.

        @param boolean: Boolean To allow extra keys
        """
        self._ignoreExtraKeys = bool(boolean);

    def setName(self, name):
        """Sets the node Name.

        @param name: string The node's name
        """
        self._name = str(name);

    def hasDefaultValue(self):
        return self._addIfNotSet;

    def getDefaultValue(self):
        """Retrieves the default value.

        @return: dict The default value

        @raise RuntimeException: if the node has no default value
        """
        if not self.hasDefaultValue():
            raise RuntimeException(
                'The node at path "{0}" has no default value.'
                ''.format(self.getPath())
            );

        default = dict();
        for name, child in self._children.items():
            if child.hasDefaultValue():
                default[name] = child.getDefaultValue();

        return default;


    def addChild(self, node):
        """Adds a child node.

        @param child: NodeInterface The child node to add

        @raise InvalidArgumentException: when the child node has no name
        @raise InvalidArgumentException: when the child node's name
            is not unique
        """
        assert isinstance(node, NodeInterface);

        name = node.getName();

        if not name:
            raise InvalidArgumentException('Child nodes must be named.');

        if name in self._children:
            raise InvalidArgumentException(
                'A child node named "{0}" already exists.'
                ''.format(name)
            );

        self._children[name] = node;


    def _finalizeValue(self, value):
        if value is False:
            raise UnsetKeyException(
                'Unsetting key for path "{0}", value: {1}'
                ''.format(self.getPath(), json.dumps(value))
            );

        for name, child in self._children.items():
            assert isinstance(child, NodeInterface);
            if not name in value:
                if child.isRequired():
                    ex = InvalidConfigurationException(
                        'The child node "{0}" at path "{1}" must be '
                        'configured.'.format(name, self.getPath())
                    );
                    ex.setPath(self.getPath());
                    raise ex;

                if child.hasDefaultValue():
                    value[name] = child.getDefaultValue();

                continue;

            try:
                value[name] = child.finalize(value[name]);
            except UnsetKeyException:
                value.pop(name);

        return value;

    def _validateType(self, value):
        if not isinstance(value, dict):
            if not self._allowFalse or value:
                ex = InvalidTypeException(
                    'Invalid type for path "{0}". Expected array, but got {1}'
                    ''.format(self.getPath(), type(value).__name__)
                );
                ex.setPath(self.getPath())
                raise ex;

    def _normalizeValue(self, value):
        if value is False:
            return value;

        assert isinstance(value, dict);

        value = self._remapXml(value);
        normalized = dict();

        for name, child in self._children.items():
            assert isinstance(child, NodeInterface)
            if name in value:
                normalized[name] = child.normalize(value[name]);
                value.pop(name);

        # if extra fields are present, throw exception
        if value and not self._ignoreExtraKeys:
            ex = InvalidConfigurationException(
                'Unrecognized options "{0}" under "{1}"'
                ''.format(", ".join(value.keys()), self.getPath())
            );
            ex.setPath(self.getPath());
            raise ex;

        return normalized;

    def _remapXml(self, value):
        """Remaps multiple singular values to a single plural value.

        @param value: cict The source values

        @return: dict The remapped values
        """
        assert isinstance(value, dict);

        for singular, plural in self._xmlRemappings:
            if not singular in value:
                continue;

            value[plural] = Processor.normalizeConfig(value, singular, plural);
            value.pop(singular);

        return value;


    def _mergeValues(self, leftSide, rightSide):
        """
        @raise InvalidConfigurationException:
        @raise RuntimeException:
        """
        if rightSide is False:
            # if this is still false after the last config has been merged the
            # finalization pass will take care of removing this key entirely
            return False;

        if not leftSide or not self._performDeepMerging:
            return rightSide;

        for k in range(len(rightSide)):
            v = rightSide[k];
            # no conflict
            if k not in leftSide:
                if not self._allowNewKeys:
                    ex = InvalidConfigurationException(
                        'You are not allowed to define new elements for path '
                        '"{0}". Please define all elements for this path in '
                        'one config file. If you are trying to overwrite an '
                        'element, make sure you redefine it with the same '
                        'name.'.format(self.getPath())
                    );
                    ex.setPath(self.getPath());
                    raise ex;

                leftSide[k] = v;
                continue;

            if k not in self._children:
                raise RuntimeException(
                    'merge() expects a normalized config array.'
                );

            leftSide[k] = self._children[k].merge(leftSide[k], v);

        return leftSide;


class PrototypedArrayNode(ArrayNode):
    def __init__(self, name, parent=None):
        ArrayNode.__init__(self, name, parent=parent);
        self._prototype = None;
        self._keyAttribute = None;
        self._removeKeyAttribute = None;
        self._minNumberOfElements = 0;
        self._defaultValue = dict();
        self._defaultChildren = None; # dict

    def setMinNumberOfElements(self, numder):
        """Sets the minimum number of elements that a prototype based node
        must contain. By default this is zero, meaning no elements.

        @param numder: int
        """
        self._minNumberOfElements = int(numder);

    def setKeyAttribute(self, attribute, remove=True):
        """Sets the attribute which value is to be used as key.

        This is useful when you have an indexed array that should be an
        associative array. You can select an item from within the array
        to be the key of the particular item. For example, if "id" is the
        "key", then:

        {
            {'id': "my_name", 'foo': "bar"},
        }

        becomes

        {
            'my_name': {'foo': "bar"},
        };

        If you'd like "'id' => 'my_name'" to still be present in the resulting
        array, then you can set the second argument of this method to false.

        @param attribute: string The name of the attribute which value is
            to be used as a key
        @param remove: boolean Whether or not to remove the key
        """
        self._keyAttribute = str(attribute);
        self._removeKeyAttribute = bool(remove);

    def getKeyAttribute(self):
        """Retrieves the name of the attribute which value should be used as
        key.

        @return: string The name of the attribute
        """
        return self._keyAttribute;

    def setDefaultValue(self, value):
        """Sets the default value of this node.

        @param value: dict

        @raise InvalidArgumentException: if the default value is not an array
        """
        if not isinstance(value, dict):
            raise InvalidArgumentException(
                '{0}: the default value of an array node has to be an array.'
                ''.format(self.getPath())
            );

        self._defaultValue = value;

    def hasDefaultValue(self):
        return True;

    def setAddChildrenIfNoneSet(self, children=None):
        """Adds default children when none are set.

        @param children: integer|string|dict|null The number of
            children|The child name|The children names to be added
        """
        if children is None:
            children = ['default'];
        elif isinstance(children, int) and children > 0:
            children = range(1, children+1);
        elif isinstance(children, basestring):
            children = [children];

        if isinstance(children, list):
            children = Array.toDict(children);

        assert isinstance(children, dict);
        self._defaultChildren = children;

    def getDefaultValue(self):
        if not self._defaultValue is None:
            if self._prototype.hasDefaultValue():
                default = self._prototype.getDefaultValue();
            else:
                default = list();

            defaults = dict();
            values = self._defaultChildren.values();
            for i in range(len(values)):
                if self._keyAttribute is None:
                    key = i;
                else:
                    key = values[i];
                defaults[key] = default;

            return defaults;

        return self._defaultValue;

    def setPrototype(self, node):
        """Sets the node prototype.

        @param node: PrototypeNodeInterface
        """
        assert isinstance(node, PrototypeNodeInterface);
        self._prototype = node;

    def getPrototype(self):
        """Retrieves the prototype

        @return: PrototypeNodeInterface The prototype
        """
        return self._prototype;

    def addChild(self, node):
        """Disable adding concrete children for prototyped nodes.

        @param node: NodeInterface The child node to add

        @raise ConfigException: Always
        """
        assert isinstance(node, NodeInterface);

        raise ConfigException(
            'A prototyped array node can not have concrete children.'
        );

    def _finalizeValue(self, value):
        if value is False:
            raise UnsetKeyException(
                'Unsetting key for path "%s", value: %s'
                ''.format(self.getPath(), json.dumps(value))
            )

        assert isinstance(value, dict);

        for k, v in value.items():
            self._prototype.setName(k);
            try:
                value[k] = self._prototype.finalize(v);
            except UnsetKeyException:
                value.pop(k);

        if len(value) < self._minNumberOfElements:
            ex = InvalidConfigurationException(
                'The path "{0}" should have at least {1} element(s) defined.'
                ''.format(self.getPath(), self._minNumberOfElements)
            );
            ex.setPath(self.getPath());
            raise ex;

        return value;

    def _normalizeValue(self, value):
        if value is False:
            return value;

        assert isinstance(value, dict);

        value = self._remapXml(value);

        isAssoc = value.keys() != range(len(value));
        normalized = dict();

        i = -1;
        for k, v in value.items():
            i += 1;

            if not self._keyAttribute is None and isinstance(v, dict):
                if self._keyAttribute not in v \
                    and isinstance(k, int) \
                    and not isAssoc:
                    ex = InvalidConfigurationException(
                        'The attribute "%s" must be set for path "%s".'
                        ''.format(self._keyAttribute, self.getPath())
                    );
                    ex.setPath(self.getPath());
                    raise ex;
                elif self._keyAttribute in v:
                    k = v[self._keyAttribute];

                    # remove the key attribute when required
                    if self._removeKeyAttribute:
                        del v[self._keyAttribute];

                    # if only "value" is left
                    if 1 == len(v) and 'value' in v:
                        v = v['value'];

                if k in normalized:
                    ex = DuplicateKeyException(
                        'Duplicate key "{0}" for path "{1}".'
                        ''.format(k, self.getPath())
                    );
                    ex.setPath(self.getPath());
                    raise ex;

            self._prototype.setName(k);
            if not self._keyAttribute is None or isAssoc:
                normalized[k] = self._prototype.normalize(v);
            else:
                normalized[i] = self._prototype.normalize(v);

        return normalized;

    def _mergeValues(self, leftSide, rightSide):
        if rightSide is False:
            # if this is still false after the last config has been merged the
            # finalization pass will take care of removing this key entirely
            return False;

        if not leftSide or not self._performDeepMerging:
            return rightSide;

        leftSide = list(leftSide);

        for k in range(len(rightSide)):
            v = rightSide[k];

            # prototype, and key is irrelevant, so simply append the element
            if self._keyAttribute is None:
                leftSide.append(v);
                continue;

            # no conflict
            if k not in leftSide:
                if not self._allowNewKeys:
                    ex = InvalidConfigurationException(
                        'You are not allowed to define new elements for path '
                        '"{0}". Please define all elements for this path in '
                        'one config file. If you are trying to overwrite an '
                        'element, make sure you redefine it with the same '
                        'name.'.format(self.getPath())
                    );
                    ex.setPath(self.getPath());
                    raise ex;

                leftSide[k] = v;
                continue;

            self._prototype.setName(k);
            leftSide[k] = self._prototype.merge(leftSide[k], v);

        return leftSide;

class ExprBuilder(Object):
    """This class builds an if expression."""
    def __init__(self, node):
        assert isinstance(node, NodeDefinition);
        self._node = node;
        self.ifPart = None;
        self.thenPart = None;

    def always(self, then=None):
        """Marks the expression as being always used.

        @param then: callable

        @return: ExprBuilder
        """
        self.ifPart = lambda v: True;

        if not then is None:
            assert Tool.isCallable(then);
            self.thenPart = then;
        return self;

    def ifTrue(self, closure=None):
        """Sets a closure to use as tests.

        The default one tests if the value is true.

        @param closure: callable

        @return: ExprBuilder
        """
        if closure is None:
            closure = lambda v: v is True;
        assert Tool.isCallable(closure);
        self.ifPart = closure;
        return self;

    def ifString(self):
        """Tests if the value is a string

        @return: ExprBuilder
        """
        self.ifPart = lambda v: isinstance(v, basestring);
        return self;

    def ifNull(self):
        """Tests if the value is a Null

        @return: ExprBuilder
        """
        self.ifPart = lambda v: v is None;
        return self;

    def ifArray(self):
        """Tests if the value is a array

        @return: ExprBuilder
        """
        self.ifPart = lambda v: isinstance(v, dict);
        return self;

    def ifInArray(self, target):
        """Tests if the value is in an array

        @param target: dict

        @return: ExprBuilder
        """
        self.ifPart = lambda v: v in dict(target).values();
        return self;

    def ifNotInArray(self, target):
        """Tests if the value is not in an array

        @param target: dict

        @return: ExprBuilder
        """
        self.ifPart = lambda v: v not in dict(target).values();
        return self;

    def then(self, closure):
        """Sets the closure to run if the test pass.

        @param closure: callable

        @return: ExprBuilder
        """
        assert Tool.isCallable(closure);
        self.thenPart = closure;
        return self;

    def ThenEmptyArray(self):
        """Sets a closure returning an empty array.

        @return: ExprBuilder
        """
        self.thenPart = lambda v: dict();
        return self;

    def thenInvalid(self, message):
        """Sets a closure marking the value as invalid at validation time.

        if you want to add the value of the node in your message
        just use a {0} placeholder.

        @param message: string

        @return: ExprBuilder

        @raise InvalidArgumentException:
        """
        def closure(v):
            raise InvalidArgumentException(message.format(v));
        self.thenPart = closure;
        return self;

    def thenUnset(self):
        """Sets a closure unsetting this key of the array at validation time.

        @return: ExprBuilder

        @raise UnsetKeyException:
        """
        def closure(v):
            raise UnsetKeyException("Unsetting key");
        self.thenPart = closure;
        return self;

    def end(self):
        """Returns the related node

        @return: NodeDefinition

        @raise RuntimeException:
        """
        if self.ifPart is None:
            raise RuntimeException('You must specify an if part.');
        if self.thenPart is None:
            raise RuntimeException('You must specify a then part.');
        return self._node;

    @classmethod
    def buildExpressions(cls, expressions):
        """Builds the expressions.

        @param expressions: ExprBuilder[] An array of ExprBuilder instances
            to build

        @return: callable[]
        """
        expressions = list(expressions);
        for i in range(len(expressions)):
            if isinstance(expressions[i], ExprBuilder):
                def closure(v):
                    if expressions[i].ifPart(v):
                        return expressions[i].thenPart(v);
                    else:
                        return v;
                expressions[i] = closure;
        return expressions;
        

class NodeDefinition(NodeParentInterface):
    def __init__(self, name, parent=None):
        if not parent is None:
            assert isinstance(parent, NodeParentInterface);
        self._name = str(name);
        self._normalization = None;
        self._validation = None;
        self._defaultValue = None;
        self._default = False;
        self._required = False;
        self._merge = None;
        self._allowEmptyValue = None;
        self._nullEquivalent = None;
        self._trueEquivalent = True;
        self._falseEquivalent = False;
        self._parent = parent;
        self._attributes = dict();

    @abstract
    def _createNode(self):
        """Instantiate and configure the node according to this definition

        @return: NodeInterface The node instance

        @raise InvalidDefinitionException: When the definition is invalid 
        """
        pass;

    def getName(self):
        return self._name;

    def setParent(self, parent):
        """Sets the parent node.

        @param parent: NodeParentInterface The parent

        @return: NodeDefinition
        """
        assert isinstance(parent, NodeParentInterface);
        self._parent = parent;
        return self;

    def attribute(self, key, value):
        """Sets an attribute on the node.

        @param key: string
        @param value: mixed

        @return: NodeDefinition
        """
        self._attributes[key] = value;
        return self;

    def end(self):
        """Returns the parent node.

        @return: NodeParentInterface The builder of the parent node
        """
        return self._parent;

    def getNode(self, forceRootNode=False):
        """Creates the node.

        @param forceRootNode: boolean
            Whether to force this node as the root node

        @return: NodeInterface
        """
        if forceRootNode:
            self._parent = None;

        if not self._normalization is None:
            self._normalization.befores = ExprBuilder.buildExpressions(
                self._normalization.befores
            );
        if not self._validation is None:
            self._validation.rules = ExprBuilder.buildExpressions(
                self._validation.rules
            );
        node = self._createNode();
        node.setAttributes(self._attributes);
        return node;

    def defaultValue(self, value):
        """Sets the default value.

        @param value: mixed The default value

        @return: NodeDefinition
        """
        self._default = True;
        self._defaultValue = value;
        return self;

    def isRequired(self):
        """Sets the node as required.

        @return: NodeDefinition
        """
        self._required = True;
        return self;

    def treatNullLike(self, value):
        """Sets the equivalent value used when the node contains null.

        @param value: mixed

        @return: NodeDefinition
        """
        self._nullEquivalent = value;
        return self;

    def treatTrueLike(self, value):
        """Sets the equivalent value used when the node contains true.

        @param value: mixed

        @return: NodeDefinition
        """
        self._trueEquivalent = value;
        return self;

    def treatFalseLike(self, value):
        """Sets the equivalent value used when the node contains false.

        @param value: mixed

        @return: NodeDefinition
        """
        self._falseEquivalent = value;
        return self;

    def defaultNull(self):
        """Sets null as the default value.

        @return: NodeDefinition
        """
        self.defaultValue(None);
        return self;

    def defaultTrue(self):
        """Sets true as the default value.

        @return: NodeDefinition
        """
        self.defaultValue(True);
        return self;

    def defaultFalse(self):
        """Sets false as the default value.

        @return: NodeDefinition
        """
        self.defaultValue(False);
        return self;

    def beforeNormalization(self):
        """Sets an expression to run before the normalization.

        @return: ExprBuilder
        """
        return self.normalization().before();

    def cannotBeEmpty(self):
        """Denies the node value being empty.

        @return: NodeDefinition
        """
        self._allowEmptyValue = False;
        return self;

    def validate(self):
        """Sets an expression to run for the validation.

        The expression receives the value of the node and must return it.
        It can modify it.

        An exception should be thrown when the node is not valid.

        @return: ExprBuilder
        """
        return self.validation().rule();

    def cannotBeOverwritten(self, deny=True):
        """Sets whether the node can be overwritten.

        @param deny: Boolean Whether the overwriting is forbidden or not

        @return: NodeDefinition
        """
        self.merge().denyOverwrite(deny);
        return self;

    def validation(self):
        """Gets the builder for validation rules.

        @return: ValidationBuilder
        """
        if self._validation is None:
            self._validation = ValidationBuilder(self);
        return self._validation;

    def merge(self):
        """Gets the builder for merging rules.

        @return: MergeBuilder
        """
        if self._merge is None:
            self._merge = MergeBuilder(self);
        return self._merge;

    def normalization(self):
        """Gets the builder for normalization rules.

        @return: NormalizationBuilder
        """
        if self._normalization is None:
            self._normalization = NormalizationBuilder(self);
        return self._normalization;

class VariableNodeDefinition(NodeDefinition):
    def _instantiateNode(self):
        """Instantiate a Node

        @return: VariableNode The node
        """
        return VariableNode(self._name, self._parent);

    def _createNode(self):
        node = self._instantiateNode();

        if not self._normalization is None:
            node.setNormalizationClosures(self._normalization.befores);

        if not self._merge is None:
            node.setAllowOverwrite(self.merge().allowOverwrite);

        if self._default:
            node.setDefaultValue(self._defaultValue);

        if not self._allowEmptyValue is None:
            node.setAllowEmptyValue(self._allowEmptyValue);

        node.addEquivalentValue(None, self._nullEquivalent);
        node.addEquivalentValue(True, self._trueEquivalent);
        node.addEquivalentValue(False, self._falseEquivalent);
        node.setRequired(self._required);

        if not self._validation is None:
            node.setFinalValidationClosures(self._validation.rules);

        return node;

class ScalarNodeDefinition(VariableNodeDefinition):
    def _instantiateNode(self):
        return ScalarNode(self._name, self._parent);

class BooleanNodeDefinition(ScalarNodeDefinition):
    def __init__(self, name, parent=None):
        ScalarNodeDefinition.__init__(self, name, parent=parent);
        self._nullEquivalent = True;

    def _instantiateNode(self):
        return BooleanNode(self._name, self._parent);


class Processor(Object):
    """This class is the entry point for config
    normalization/merging/finalization.
    """
    def process(self, configTree, configs):
        """Processes an array of configurations.

        @param configTree: NodeInterface The node tree describing
            the configuration
        @param configs: list An array of configuration items to process
        """
        assert isinstance(configTree, NodeInterface);
        assert isinstance(configs, list);

        currentConfig = dict();
        for config in configs:
            config = configTree.normalize(config);
            currentConfig = configTree.merge(currentConfig, config);

        return configTree.finalize(currentConfig);

    def processConfiguration(self, configuration, configs):
        """Processes an array of configurations.

        @param configuration: ConfigurationInterface The configuration class
        @param configs: dict An array of configuration items to process
        """
        assert isinstance(configuration, ConfigurationInterface);
        assert isinstance(configs, list);

        return self.process(
            configuration.getConfigTreeBuilder().buildTree(),
            configs
        );

    @classmethod
    def normalizeConfig(cls, config, key, plural=None):
        """Normalizes a configuration entry.

        This method returns a normalize configuration array for
        a given key to remove the differences due to the original format
        (YAML and XML mainly).

        Here is an example.

        The configuration in XML:

        <twig:extension>twig.extension.foo</twig:extension>
        <twig:extension>twig.extension.bar</twig:extension>

        And the same configuration in YAML:

        extensions: ['twig.extension.foo', 'twig.extension.bar']

        @param config: dict A config array
        @param key: string The key to normalize
        @param plural: string The plural form of the key if it is irregular

        @return: list
        """
        assert isinstance(config, dict);
        key = str(key);
        plural = str(plural);

        if plural is None:
            plural = "{0}s".format(key);

        values = list();
        if plural in config:
            values = config[plural];
        elif key in config:
            if isinstance(config[key], list):
                values = config[key];
            else:
                # only one
                values = [config[key]];

        return list(values);




class ValidationBuilder(Object):
    """This class builds validation conditions."""
    def __init__(self, node):
        """
        @param node: NodeDefinition
        """
        assert isinstance(node, NodeDefinition);
        self._node = node;
        self.rules = list();

    def rule(self, closure=None):
        """Registers a closure to run as normalization
        or an expression builder to build it if null is provided.

        @param closure: callable

        @return: ExprBuilder|ValidationBuilder
        """
        if not closure is None:
            assert Tool.isCallable(closure);
            self.rules.append(closure);
            return self;
        self.rules.append(ExprBuilder(self._node));
        return self.rules[-1];

class MergeBuilder(Object):
    """This class builds merge conditions."""
    def __init__(self, node):
        """
        @param node: NodeDefinition
        """
        assert isinstance(node, NodeDefinition);
        self._node = node;
        self.allowFalse = False;
        self.allowOverwrite = True;

    def allowUnset(self, allow=True):
        """Sets whether the node can be unset.

        @param allow: Boolean

        @return: MergeBuilder
        """
        self.allowFalse = allow;
        return self;

    def denyOverwrite(self, deny=True):
        """Sets whether the node can be overwritten.

        @param deny: Boolean

        @return: MergeBuilder
        """
        self.allowOverwrite = not deny;
        return self;

    def end(self):
        """Returns the related node.

        @return: NodeDefinition
        """
        return self._node;

class NormalizationBuilder(Object):
    """This class builds normalization conditions."""
    def __init__(self, node):
        """
        @param node: NodeDefinition
        """
        assert isinstance(node, NodeDefinition);
        self._node = node;
        self.befores = list();
        self.remappings = list();

    def remap(self, key, plural=None):
        """Registers a key to remap to its plural form.

        @param key: string The key to remap
        @param plural: string The plural of the key in case of irregular plural

        @return: NormalizationBuilder
        """
        if plural is None:
            plural = "{0}s".format(key);
        self.remappings.append([key, plural]);
        return self;

    def before(self, closure=None):
        """Registers a closure to run before the normalization
        or an expression builder to build it if null is provided.

        @param closure: callable

        @return: ExprBuilder|NormalizationBuilder
        """
        if not closure is None:
            assert Tool.isCallable(closure);
            self.befores.append(closure);
            return self;
        self.befores.append(ExprBuilder(self._node));
        return self.befores[-1];

class ArrayNodeDefinition(NodeDefinition, ParentNodeDefinitionInterface):
    def __init__(self, name, parent=None):
        NodeDefinition.__init__(self, name, parent=parent);
        self._performDeepMerging = True;
        self._ignoreExtraKeys = None;
        self._children = dict();
        self._prototype = None;
        self._atLeastOne = False;
        self._allowNewKeys = None;
        self._key = None;
        self._removeKeyItem = None;
        self._addDefaults = False;
        self._addDefaultChildren = False;
        self._nodeBuilder = None;
        self._normalizeKeys = True;

        self._allowEmptyValue = True;
        self._nullEquivalent = dict();
        self._trueEquivalent = dict();

    def setBuilder(self, builder):
        """Sets a custom children builder.

        @param builder: NodeBuilder A custom NodeBuilder
        """
        assert isinstance(builder, NodeBuilder);
        self._nodeBuilder = builder;

    def children(self):
        """Returns a builder to add children nodes.

        @return: NodeBuilder
        """
        return self._getNodeBuilder();

    def prototype(self, nodeType):
        """Sets a prototype for child nodes.

        @param nodeType: string the type of node

        @return: NodeDefinition
        """
        self._prototype = \
            self._getNodeBuilder().node(None, nodeType).setParent(self);
        return self._prototype;

    def addDefaultsIfNotSet(self):
        """Adds the default value if the node is not set in the configuration.

        This method is applicable to concrete nodes only
        (not to prototype nodes). If this function has been called
        and the node is not set during the finalization phase,
        it's default value will be derived from its children default values.

        @return: ArrayNodeDefinition
        """
        self._addDefaults = True;
        return self;

    def addDefaultChildrenIfNoneSet(self, children=None):
        """Adds children with a default value when none are defined.

        This method is applicable to prototype nodes only.

        @param children: integer|string|dict|None The number of
            children|The child name|The children names to be added

        @return: ArrayNodeDefinition
        """
        self._addDefaultChildren = True;
        return self;

    def requiresAtLeastOneElement(self):
        """Requires the node to have at least one element.

        This method is applicable to prototype nodes only.

        @return: ArrayNodeDefinition
        """
        self._atLeastOne = True;
        return self;

    def disallowNewKeysInSubsequentConfigs(self):
        """Disallows adding news keys in a subsequent configuration.

        If used all keys have to be defined in the same configuration file.

        @return: ArrayNodeDefinition
        """
        self._allowNewKeys = False;
        return self;

    def fixXmlConfig(self, singular, plural=None):
        """Sets a normalization rule for XML configurations.

        @param singular: string The key to remap
        @param plural: string The plural of the key for irregular plurals

        @return: ArrayNodeDefinition
        """
        self.normalization().remap(singular, plural);
        return self;

    def useAttributeAsKey(self, name, removeKeyItem=True):
        """Sets the attribute which value is to be used as key.

        This method is applicable to prototype nodes only.

        This is useful when you have an indexed array that should be an
        associative array. You can select an item from within the array
        to be the key of the particular item. For example, if "id" is the
        "key", then:
            {
                {'id': 'my_name', 'foo': 'bar'},
            }
        becomes
            {
                my_name', {'foo': 'bar'},
            }

        If you'd like "'id' => 'my_name'" to still be present in the resulting
        array, then you can set the second argument of this method to false.

        @param name: string The name of the key
        @param removeKeyItem: Boolean Whether
            or not the key item should be removed.

        @return: ArrayNodeDefinition
        """
        self._key = name;
        self._removeKeyItem = removeKeyItem;
        return self;

    def canBeUnset(self, allow=True):
        """Sets whether the node can be unset.

        @param allow: Boolean

        @return: ArrayNodeDefinition
        """
        self.merge().allowUnset(allow);
        return self;

    def canBeEnabled(self):
        """Adds an "enabled" boolean to enable the current section.

        By default, the section is disabled.

        @return: ArrayNodeDefinition
        """
        self.treatFalseLike({'enabled': False});
        self.treatTrueLike({'enabled': True});
        self.treatNullLike({'enabled': True});
        self.children().booleanNode('enabled').defaultFalse();
        return self;

    def canBeDisabled(self):
        """Adds an "enabled" boolean to enable the current section.

        By default, the section is enabled.

        @return: ArrayNodeDefinition
        """
        self.treatFalseLike({'enabled': False});
        self.treatTrueLike({'enabled': True});
        self.treatNullLike({'enabled': True});
        self.children().booleanNode('enabled').defaultFalse();
        return self;

    def performNoDeepMerging(self):
        """Disables the deep merging of the node.

        @return: ArrayNodeDefinition
        """
        self._performDeepMerging = False;
        return self;

    def ignoreExtraKeys(self):
        """Allows extra config keys to be specified under an array without
        throwing an exception.

        Those config values are simply ignored. This should be used only
        in special cases where you want to send an entire configuration
        array through a special tree that processes only part of the array.

        @return: ArrayNodeDefinition
        """
        self._ignoreExtraKeys = True;
        return self;

    def normalizeKeys(self, boolean):
        """Sets key normalization.

        @param boolean: boolean Whether to enable key normalization

        @return: ArrayNodeDefinition
        """
        self._normalizeKeys = bool(boolean);
        return self;

    def append(self, node):
        """Appends a node definition.

        $node = ArrayNodeDefinition()
            ->children()
            ->scalarNode('foo')->end()
            ->scalarNode('baz')->end()
            ->end()
            ->append($this->getBarNodeDefinition())
        ;

        @param node: NodeDefinition A NodeDefinition instance

        @return: ArrayNodeDefinition
        """
        assert isinstance(node, NodeDefinition);
        self._children[node.getName()] = node.setParent(self);
        return self;

    def _getNodeBuilder(self):
        """Returns a node builder to be used to add children and prototype

        @return: NodeBuilder The node builder
        """
        if self._nodeBuilder is None:
            self._nodeBuilder = NodeBuilder();
        return self._nodeBuilder.setParent(self);

    def _createNode(self):
        if self._prototype is None:
            node = ArrayNode(self._name, self._parent);
            self.validateConcreteNode(node);

            node.setAddIfNotSet(self._addDefaults);

            for child in self._children.values():
                child._parent = node;
                node.addChild(child.getNode());
        else:
            node = PrototypedArrayNode(self._name, self._parent);

            self.validatePrototypeNode(node);

            if not self._key is None:
                node.setKeyAttribute(self._key, self._removeKeyItem);

            if self._atLeastOne:
                node.setMinNumberOfElements(1);

            if self._default:
                node.setDefaultValue(self._defaultValue);

            if not self._addDefaultChildren is False:
                node.setAddChildrenIfNoneSet(self._addDefaultChildren);
                if isinstance(self._prototype, type(self)):
                    if self._prototype._prototype is None:
                        self._prototype.addDefaultsIfNotSet();

            self._prototype._parent = node;
            node.setPrototype(self._prototype.getNode());

        node.setAllowNewKeys(self._allowNewKeys);
        node.addEquivalentValue(None, self._nullEquivalent);
        node.addEquivalentValue(True, self._trueEquivalent);
        node.addEquivalentValue(False, self._falseEquivalent);
        node.setPerformDeepMerging(self._performDeepMerging);
        node.setRequired(self._required);
        node.setIgnoreExtraKeys(self._ignoreExtraKeys);
        node.setNormalizeKeys(self._normalizeKeys);

        if not self._normalization is None:
            node.setNormalizationClosures(self._normalization.befores);
            node.setXmlRemappings(self._normalization.remappings);

        if not self._merge is None:
            node.setAllowOverwrite(self._merge.allowOverwrite);
            node.setAllowFalse(self._merge.allowFalse);

        if not self._validation is None:
            node.setFinalValidationClosures(self._validation.rules);

        return node;

    def validateConcreteNode(self, node):
        """Validate the configuration of a concrete node.

        @param node: ArrayNode  The related node

        @raise InvalidDefinitionException:
        """
        assert isinstance(node, ArrayNode);
        path = node.getPath();

        if not self._key is None:
            raise InvalidDefinitionException(
                '.useAttributeAsKey() is not applicable to concrete '
                'nodes at path "{0}"'.format(path)
            );

        if self._atLeastOne:
            raise InvalidDefinitionException(
                '.requiresAtLeastOneElement() is not applicable '
                'to concrete nodes at path "{0}"'.format(path)
            );

        if self._default:
            raise InvalidDefinitionException(
                '.defaultValue() is not applicable to concrete nodes '
                'at path "{0}"'.format(path)
            );

        if not self._addDefaultChildren is False:
            raise InvalidDefinitionException(
                '.addDefaultChildrenIfNoneSet() is not applicable '
                'to concrete nodes at path "{0}"'.format(path)
            );

    def validatePrototypeNode(self, node):
        """Validate the configuration of a prototype node.

        @param node: PrototypedArrayNode The related node

        @raise InvalidDefinitionException:
        """
        assert isinstance(node, PrototypedArrayNode);
        path = node.getPath();

        if self._addDefaults:
            raise InvalidDefinitionException(
                '.addDefaultsIfNotSet() is not applicable to prototype '
                'nodes at path "{0}"'.format(path)
            );

        if not self._addDefaultChildren is False:
            if self._default:
                raise InvalidDefinitionException(
                    'A default value and default children might not be '
                    'used together at path "{0}"'.format(path)
                );

            if not self._key is None and (
                self._addDefaultChildren is None or \
                isinstance(self._addDefaultChildren, int) and \
                self._addDefaultChildren > 0
                ):
                raise InvalidDefinitionException(
                    '.addDefaultChildrenIfNoneSet() should set default '
                    'children names as ->useAttributeAsKey() is used '
                    'at path "{0}"'.format(path)
                );

            if self._key is None and (
                isinstance(self._addDefaultChildren, basestring) or \
                isinstance(self._addDefaultChildren, dict)
                ):
                raise InvalidDefinitionException(
                    '->addDefaultChildrenIfNoneSet() might not set default '
                    'children names as ->useAttributeAsKey() is not used '
                    'at path "{0}"'.format(path)
                );


class NodeBuilder(NodeParentInterface):
    def __init__(self):
        self._parent = None;
        self._nodeMapping = {
            'variable'  : __name__ + '.VariableNodeDefinition',
            'array'     : __name__ + '.ArrayNodeDefinition',
            'scalar'    : __name__ + '.ScalarNodeDefinition',
            'boolean'   : __name__ + '.BooleanNodeDefinition',
        };

    def setParent(self, parent=None):
        """Set the parent node.

        @param parent: ParentNodeDefinitionInterface The parent node

        @return: NodeBuilder This node builder
        """
        if parent is not None:
            assert isinstance(parent, ParentNodeDefinitionInterface);
        self._parent = parent;
        return self;

    def arrayNode(self, name):
        """Creates a child array node.

        @param name: string The name of the node

        @return: ArrayNodeDefinition The child node
        """
        return self.node(name, 'array');

    def scalarNode(self, name):
        """Creates a child scalar node.

        @param name: string The name of the node

        @return: ScalarNodeDefinition The child node
        """
        return self.node(name, 'scalar');

    def booleanNode(self, name):
        """Creates a child boolean node.

        @param name: string The name of the node

        @return: BooleanNodeDefinition The child node
        """
        return self.node(name, 'boolean');


    def end(self):
        """Returns the parent node.

        @return: ParentNodeDefinitionInterface The parent node
        """
        return self._parent;

    def node(self, name, nodeType):
        """Creates a child node.

        @param name: string
        @param nodeType: string

        @return: NodeDefinition

        @raise RuntimeException: When the node type is not registered
        @raise RuntimeException: When the node class is not found
        """
        qualClassName = self.getNodeClass(nodeType);

        moduleName, className = Tool.split(qualClassName);
        try:
            module = __import__(moduleName, globals(), {}, [className], 0);
        except TypeError:
            module = __import__(moduleName, globals(), {}, ["__init__"], 0);
        node = getattr(module, className)(name);

        self.append(node);

        return node;

    def append(self, node):
        """Appends a node definition.

        @param node: NodeDefinition

        @return: NodeDefinition
        """
        assert isinstance(node, NodeDefinition);

        if isinstance(node, ParentNodeDefinitionInterface):
            builder = self.__copy__();
            builder.setParent(None);
            node.setBuilder(builder);

        if not self._parent is None:
            self._parent.append(node);
            # Make this builder the node parent to allow for a fluid interface
            node.setParent(self);

        return self;

    def setNodeClass(self, nodeType, nodeClass):
        """Adds or overrides a node Type.

        @param nodeType: string The name of the type
        @param nodeClass: The fully qualified name the node definition class

        @return: NodeDefinition
        """
        self._nodeMapping[str(nodeType).lower()] = nodeClass;

        return self;

    def getNodeClass(self, nodeType):
        """Returns the class name of the node definition.

        @param nodeType: string The node type

        @return: string The node definition class name

        @raise RuntimeException: When the node type is not registered
        @raise RuntimeException: When the node class is not found
        """
        nodeType = str(nodeType).lower();

        if nodeType not in self._nodeMapping:
            raise RuntimeException(
                'The node type "{0}" is not registered.'
                ''.format(nodeType)
            );

        nodeClass = self._nodeMapping[nodeType];
        moduleName, className = Tool.split(nodeClass);
        try:
            module = __import__(moduleName, globals(), {}, [className], 0);
        except TypeError:
            module = __import__(moduleName, globals(), {}, ["__init__"], 0);
        if not hasattr(module, className):
            raise RuntimeException(
                'The node class "{0}" does not exist.'.format(nodeClass)
            );

        return nodeClass;

class TreeBuilder(NodeParentInterface):
    def __init__(self):
        self._tree = None;
        self._root = None;
        self._builder = None;

    def root(self, name, nodeType='array', builder=None):
        """Creates the root node.

        @param name: string The name of the root node
        @param nodeType: string The type of the root node
        @param builder: NodeBuilder A custom node builder instance

        @return: ArrayNodeDefinition|NodeDefinition
            The root node (as an ArrayNodeDefinition when the type is 'array')

        @raise RuntimeException: When the node type is not supported
        """
        if builder is None:
            builder = NodeBuilder();
        assert isinstance(builder, NodeBuilder);

        self._root = builder.node(name, nodeType).setParent(self);
        return self._root;

    def buildTree(self):
        """Builds the tree.

        @return: NodeInterface

        @raise RuntimeException: When the configuration tree has no root node.
        """
        if self._root is None:
            raise RuntimeException('The configuration tree has no root node.');
        if not self._tree is None:
            return self._tree;

        self._tree = self._root.getNode(True);
        return self._tree;


class FileResource(ResourceInterface, SerializableInterface):
    def __init__(self, resource):
        self.__resource = os.path.realpath(str(resource));

    def __str__(self):
        return str(self.__resource);

    def getResource(self):
        return self.__resource;

    def isFresh(self, timestamp):
        if not os.path.exists(self.__resource):
            return False;
        return os.path.getmtime(self.__resource) < timestamp;

    def serialize(self):
        return serialize(self.__resource);

    def unserialize(self, serialized):
        self.__resource = unserialize(serialized);


class LoaderResolver(LoaderResolverInterface):
    def __init__(self, loaders=None):
        self.__loaders = list();
        for loader in list(loaders):
            self.addLoader(loader);

    def resolve(self, resource, resourceType=None):
        for loader in self.__loaders:
            if loader.supports(resource, resourceType):
                return loader;

        return False;

    def addLoader(self, loader):
        """Add a Loader

        @param loader: LoaderInterface A LoaderInterface instance
        """
        assert isinstance(loader, LoaderInterface);
        self.__loaders.append(loader);
        loader.setResolver(self); 

    def getLoaders(self):
        """Returns the registered loaders.

        @return: LoaderInterface[] An array of LoaderInterface instances
        """
        return self.__loaders;

class Loader(LoaderInterface):
    def __init__(self):
        self._resolver = None;

    def getResolver(self):
        return self._resolver;

    def setResolver(self, resolver):
        assert isinstance(resolver, LoaderResolverInterface);
        self._resolver = resolver;

    def imports(self, resource, resourceType=None):
        """Imports a resource.

        @param resource: mixed
        @param resourceType: string The resource type

        @return: mixed
        """
        return self.resolve(resource).load(resource, resourceType);

    def resolve(self, resource, resourceType=None):
        """Finds a loader able to load an imported resource.

        @param resource: mixed
        @param resourceType: string The resource type

        @return: LoaderInterface A LoaderInterface instance

        @raise FileLoaderLoadException: if no loader is found
        """
        if self.supports(resource, resourceType):
            return self;

        if self._resolver is None:
            loader = False;
        else:
            loader = self._resolver.resolve(resource, resourceType);

        if loader is False:
            raise FileLoaderLoadException(resource);

        return loader;

class DelegatingLoader(Loader):
    """DelegatingLoader delegates loading to other loaders using
    a loader resolver.
    """
    def __init__(self, resolver):
        """
        @param resolver: LoaderResolverInterface
        """
        assert isinstance(resolver, LoaderResolverInterface);
        self._resolver = resolver;

    def load(self, resource, resourceType=None):
        """Loads a resource.
        
        @param resource: mixed
        @param resourceType: string The resource type

        @return: mixed

        @raise FileLoaderLoadException: if no loader is found.
        """
        loader = self._resolver.resolve(resource, resourceType);
        if loader is False:
            raise FileLoaderLoadException(resource);
        return loader.load(resource, resourceType);

    def supports(self, resource, resourceType=None):
        if False is self._resolver.resolve(resource, resourceType):
            return False;
        else:
            return True;

class FileLoader(Loader):
    """FileLoader is the abstract class used
    by all built-in loaders that are file based.
    """
    _loading = dict();

    def __init__(self, locator):
        assert isinstance(locator, FileLocatorInterface);
        self.__currentDir = None;

        self._locator = locator;

    def setCurrentDir(self, directory):
        self.__currentDir = directory;

    def getLocator(self):
        return self._locator;

    def imports(self, resource, resourceType=None, 
                ignoreErrors=False, sourceResource=None):
        """Imports a resource.

        @param resource: mixed
        @param resourceType: string The resource type
        @param ignoreErrors: Boolean Whether to ignore import errors or not
        @param sourceResource: string The original resource
            importing the new resource

        @return: mixed
        """
        try:
            loader = self.resolve(resource, resourceType);
            if isinstance(loader, FileLoader) and \
                not self.__currentDir is None:
                resource = self._locator.locate(resource, self.__currentDir);
            if resource in self._loading:
                raise FileLoaderImportCircularReferenceException(
                    self._loading.keys()
                );

            self._loading[resource] = True;
            ret = loader.load(resource, resourceType);
            del self._loading[resource];

            return ret;
        except FileLoaderImportCircularReferenceException as e:
            raise e;
        except Exception as e:
            if not ignoreErrors:
                # prevent embedded imports from nesting multiple exceptions
                if isinstance(e, FileLoaderLoadException):
                    raise e;
                raise FileLoaderLoadException(resource, sourceResource, None, e);

class FileLocator(FileLocatorInterface):
    def __init__(self, paths=None):
        """
        @param paths: string|list A path or an array of paths 
            where to look for resources
        """
        if paths is None:
            self._paths = list();
        elif isinstance(paths, basestring):
            self._paths = [paths];
        else:
            self._paths = list(paths);

    def locate(self, name, currentPath=None, first=True):
        if self.__isAbsolutePath(name):
            if not os.path.exists(name):
                raise InvalidArgumentException(
                    'The file "{0}" does not exist.'.format(name)
                );
            return name;

        filepaths = list();

        paths = [""];
        if currentPath:
            paths.append(currentPath);
        paths.extend(self._paths);

        for path in paths:
            filename = os.path.join(path, name);
            if os.path.exists(filename):
                if first:
                    return filename;
                filepaths.append(filename);

        if not filepaths:
            raise InvalidArgumentException(
                'The file "{0}" does not exist (in: {1}).'
                ''.format(name, ", ".join(paths))
            );

        return Array.uniq(filepaths);


    def __isAbsolutePath(self, name):
        if os.path.isabs(name) and urlparse.urlparse(name).scheme:
            return True;

class ConfigException(Exception):
    pass;

class InvalidConfigurationException(ConfigException):
    __path = None;
    def setPath(self, path):
        self.__path = path;
    def getPath(self):
        return self.__path;

class InvalidTypeException(InvalidConfigurationException):
    pass;

class FileLoaderLoadException(Exception):
    # TODO: code
    pass;

class FileLoaderImportCircularReferenceException(FileLoaderLoadException):
    # TODO: code
    pass;

class InvalidDefinitionException(ConfigException):
    pass;

class UnsetKeyException(ConfigException):
    pass;

class ForbiddenOverwriteException(InvalidConfigurationException):
    pass;

class DuplicateKeyException(InvalidConfigurationException):
    pass;

class LogicException(Exception):
    pass;

class InvalidArgumentException(LogicException):
    pass;

class RuntimeException(Exception):
    pass;
