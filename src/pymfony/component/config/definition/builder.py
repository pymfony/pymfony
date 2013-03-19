# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

from pymfony.component.system import clone;
from pymfony.component.system import ClassLoader
from pymfony.component.system import Object;
from pymfony.component.system import Tool;
from pymfony.component.system.types import String;
from pymfony.component.system.types import Array;
from pymfony.component.system.reflection import ReflectionClass;
from pymfony.component.system.oop import abstract;
from pymfony.component.system.oop import interface;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import RuntimeException;

from pymfony.component.config.definition import FloatNode;
from pymfony.component.config.definition import IntegerNode
from pymfony.component.config.definition import EnumNode;
from pymfony.component.config.definition import ArrayNode;
from pymfony.component.config.definition import PrototypedArrayNode;
from pymfony.component.config.definition import VariableNode;
from pymfony.component.config.definition import ScalarNode;
from pymfony.component.config.definition import BooleanNode;
from pymfony.component.config.definition.exception import UnsetKeyException;
from pymfony.component.config.definition.exception import InvalidDefinitionException;

"""
"""

@interface
class NodeParentInterface(Object):
    """An interface that must be implemented by all node parents

    @author Victor Berchet <victor@suumit.com>

    """
    pass;

@interface
class ParentNodeDefinitionInterface(Object):
    """An interface that must be implemented by nodes which can have children

    @author Victor Berchet <victor@suumit.com>

    """
    def children(self):
        pass;

    def append(self, node):
        assert isinstance(node, NodeDefinition);

    def setBuilder(self, builder):
        assert isinstance(builder, NodeBuilder);


@abstract
class NodeDefinition(NodeParentInterface):
    """This class provides a fluent interface for defining a node.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    def __init__(self, name, parent=None):
        """Constructor

        @param name:   string               The name of the node
        @param parent: NodeParentInterface  The parent

        """
        if not parent is None:
            assert isinstance(parent, NodeParentInterface);
        self._name = str(name);
        self._normalizationBuilder = None;
        self._validationBuilder = None;
        self._defaultValue = None;
        self._default = False;
        self._required = False;
        self._mergeBuilder = None;
        self._allowEmptyValue = None;
        self._nullEquivalent = None;
        self._trueEquivalent = True;
        self._falseEquivalent = False;
        self._parent = parent;
        self._attributes = dict();


    def setParent(self, parent):
        """Sets the parent node.

        @param parent: NodeParentInterface The parent

        @return: NodeDefinition
        """
        assert isinstance(parent, NodeParentInterface);
        self._parent = parent;
        return self;



    def info(self, info):
        """Sets info message.

        @param string info The info text

        @return NodeDefinition

        """

        return self.attribute('info', info);


    def example(self, example):
        """Sets example configuration.

        @param string|array example

        @return NodeDefinition

        """

        return self.attribute('example', example);


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

        if not self._normalizationBuilder is None:
            self._normalizationBuilder.befores = ExprBuilder.buildExpressions(
                self._normalizationBuilder.befores
            );
        if not self._validationBuilder is None:
            self._validationBuilder.rules = ExprBuilder.buildExpressions(
                self._validationBuilder.rules
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
        return self._normalization().before();

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
        return self._validation().rule();

    def cannotBeOverwritten(self, deny=True):
        """Sets whether the node can be overwritten.

        @param deny: Boolean Whether the overwriting is forbidden or not

        @return: NodeDefinition
        """
        self._merge().denyOverwrite(deny);
        return self;

    def _validation(self):
        """Gets the builder for validation rules.

        @return: ValidationBuilder
        """
        if self._validationBuilder is None:
            self._validationBuilder = ValidationBuilder(self);
        return self._validationBuilder;

    def _merge(self):
        """Gets the builder for merging rules.

        @return: MergeBuilder
        """
        if self._mergeBuilder is None:
            self._mergeBuilder = MergeBuilder(self);
        return self._mergeBuilder;

    def _normalization(self):
        """Gets the builder for normalization rules.

        @return: NormalizationBuilder
        """
        if self._normalizationBuilder is None:
            self._normalizationBuilder = NormalizationBuilder(self);
        return self._normalizationBuilder;


    @abstract
    def _createNode(self):
        """Instantiate and configure the node according to this definition

        @return: NodeInterface The node instance

        @raise InvalidDefinitionException: When the definition is invalid
        """
        pass;


class ArrayNodeDefinition(NodeDefinition, ParentNodeDefinitionInterface):
    """This class provides a fluent interface for defining an array node.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    def __init__(self, name, parent=None):
        NodeDefinition.__init__(self, name, parent=parent);
        self._performDeepMerging = True;
        self._ignoreExtraKeys = None;
        self._children = dict();
        self._prototype = None;
        self._atLeastOne = False;
        self._allowNewKeys = True;
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
        self._addDefaultChildren = children;
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
        self._normalization().remap(singular, plural);
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
        self._merge().allowUnset(allow);
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
        self._children[node._name] = node.setParent(self);
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
            self._validateConcreteNode(node);

            node.setAddIfNotSet(self._addDefaults);

            for child in self._children.values():
                child._parent = node;
                node.addChild(child.getNode());
        else:
            node = PrototypedArrayNode(self._name, self._parent);

            self._validatePrototypeNode(node);

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

        if not self._normalizationBuilder is None:
            node.setNormalizationClosures(self._normalizationBuilder.befores);
            node.setXmlRemappings(self._normalizationBuilder.remappings);

        if not self._mergeBuilder is None:
            node.setAllowOverwrite(self._mergeBuilder.allowOverwrite);
            node.setAllowFalse(self._mergeBuilder.allowFalse);

        if not self._validationBuilder is None:
            node.setFinalValidationClosures(self._validationBuilder.rules);

        return node;

    def _validateConcreteNode(self, node):
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

    def _validatePrototypeNode(self, node):
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
                isinstance(self._addDefaultChildren, String) or \
                isinstance(self._addDefaultChildren, dict)
                ):
                raise InvalidDefinitionException(
                    '->addDefaultChildrenIfNoneSet() might not set default '
                    'children names as ->useAttributeAsKey() is not used '
                    'at path "{0}"'.format(path)
                );



class ExprBuilder(Object):
    """This class builds an if expression.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>
    @author: Christophe Coevoet <stof@notk.org>

    """
    def __init__(self, node):
        """Constructor

        @param node: NodeDefinition The related node

        """
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
        self.ifPart = lambda v: isinstance(v, String);
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
        self.ifPart = lambda v: v in Array.toDict(target).values();
        return self;

    def ifNotInArray(self, target):
        """Tests if the value is not in an array

        @param target: dict

        @return: ExprBuilder
        """
        self.ifPart = lambda v: v not in Array.toDict(target).values();
        return self;

    def then(self, closure):
        """Sets the closure to run if the test pass.

        @param closure: callable

        @return: ExprBuilder
        """
        assert Tool.isCallable(closure);
        self.thenPart = closure;
        return self;

    def thenEmptyArray(self):
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
            call = expressions[i];
            if isinstance(call, ExprBuilder):
                def closure(v):
                    if call.ifPart(v):
                        return call.thenPart(v);
                    else:
                        return v;
                expressions[i] = closure;
        return expressions;

class MergeBuilder(Object):
    """This class builds merge conditions.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    def __init__(self, node):
        """Constructor

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



class NodeBuilder(NodeParentInterface):
    """This class provides a fluent interface for building a node.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    def __init__(self):
        """Constructor

        """
        self._parent = None;
        self._nodeMapping = {
            'variable'  : __name__ + '.VariableNodeDefinition',
            'scalar'    : __name__ + '.ScalarNodeDefinition',
            'boolean'   : __name__ + '.BooleanNodeDefinition',
            'integer'   : __name__ + '.IntegerNodeDefinition',
            'float'   : __name__ + '.FloatNodeDefinition',
            'array'     : __name__ + '.ArrayNodeDefinition',
            'enum'   : __name__ + '.EnumNodeDefinition',
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

    def integerNode(self, name):
        """Creates a child integer node.

        @param string name the name of the node

        @return IntegerNodeDefinition The child node

        """

        return self.node(name, 'integer');


    def floatNode(self, name):
        """Creates a child float node.

        @param string name the name of the node

        @return FloatNodeDefinition The child node

        """

        return self.node(name, 'float');


    def enumNode(self, name):
        """Creates a child EnumNode.

        @param string name

        @return EnumNodeDefinition

        """

        return self.node(name, 'enum');


    def variableNode(self, name):
        """Creates a child variable node.

        @param string name The name of the node

        @return VariableNodeDefinition The builder of the child node

        """

        return self.node(name, 'variable');

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
        qualClassName = self._getNodeClass(nodeType);

        node = ClassLoader.load(qualClassName)(name);

        self.append(node);

        return node;

    def append(self, node):
        """Appends a node definition.

        @param node: NodeDefinition

        @return: NodeDefinition
        """
        assert isinstance(node, NodeDefinition);

        if isinstance(node, ParentNodeDefinitionInterface):
            builder = clone(self);
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

    def _getNodeClass(self, nodeType):
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

        if not ReflectionClass(nodeClass).exists():
            raise RuntimeException(
                'The node class "{0}" does not exist.'.format(nodeClass)
            );

        return nodeClass;




class NormalizationBuilder(Object):
    """This class builds normalization conditions.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    def __init__(self, node):
        """Constructor

        @param node: NodeDefinition The related node

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



class TreeBuilder(NodeParentInterface):
    """This is the entry class for building a config tree.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
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



class VariableNodeDefinition(NodeDefinition):
    """This class provides a fluent interface for defining a node.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    def _instantiateNode(self):
        """Instantiate a Node

        @return: VariableNode The node
        """
        return VariableNode(self._name, self._parent);

    def _createNode(self):
        node = self._instantiateNode();

        if not self._normalizationBuilder is None:
            node.setNormalizationClosures(self._normalizationBuilder.befores);

        if not self._mergeBuilder is None:
            node.setAllowOverwrite(self._merge().allowOverwrite);

        if self._default:
            node.setDefaultValue(self._defaultValue);

        if not self._allowEmptyValue is None:
            node.setAllowEmptyValue(self._allowEmptyValue);

        node.addEquivalentValue(None, self._nullEquivalent);
        node.addEquivalentValue(True, self._trueEquivalent);
        node.addEquivalentValue(False, self._falseEquivalent);
        node.setRequired(self._required);

        if not self._validationBuilder is None:
            node.setFinalValidationClosures(self._validationBuilder.rules);

        return node;


class ScalarNodeDefinition(VariableNodeDefinition):
    """This class provides a fluent interface for defining a node.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    def _instantiateNode(self):
        """Instantiate a Node

        @return ScalarNode The node

        """
        return ScalarNode(self._name, self._parent);


class BooleanNodeDefinition(ScalarNodeDefinition):
    """This class provides a fluent interface for defining a node.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    def __init__(self, name, parent=None):
        ScalarNodeDefinition.__init__(self, name, parent=parent);
        self._nullEquivalent = True;

    def _instantiateNode(self):
        """Instantiate a Node

        @return: BooleanNode The node

        """
        return BooleanNode(self._name, self._parent);

class ValidationBuilder(Object):
    """This class builds validation conditions.

    @author Christophe Coevoet <stof@notk.org>

    """
    def __init__(self, node):
        """Constructor

        @param node: NodeDefinition The related node

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



class EnumNodeDefinition(ScalarNodeDefinition):
    """Enum Node Definition.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self, name, parent=None):
        ScalarNodeDefinition.__init__(self, name, parent=parent);
        self.__values = None;

    def values(self, values):
        assert isinstance(values, list);

        values = Array.uniq(values);

        if (len(values) <= 1) :
            raise InvalidArgumentException('.values() must be called with at least two distinct values.');


        self.__values = values;

        return self;


    def _instantiateNode(self):
        """Instantiate a Node

        @return EnumNode The node

        @raise RuntimeException

        """

        if (None is self.__values) :
            raise RuntimeException('You must call .values() on enum nodes.');


        return EnumNode(self._name, self._parent, self.__values);




@abstract
class NumericNodeDefinition(ScalarNodeDefinition):
    """Abstract class that contain common code of integer and float node definition.

    @author David Jeanmonod <david.jeanmonod@gmail.com>

    """
    def __init__(self, name, parent=None):
        ScalarNodeDefinition.__init__(self, name, parent=parent)
        self._min = None;
        self._max = None;

    def max(self, maxValue):
        """Ensures that the value is smaller than the given reference.

        @param mixed maxValue

        @return NumericNodeDefinition

        @raise InvalidArgumentException when the constraint is inconsistent

        """

        if (self._min and self._min > maxValue) :
            raise InvalidArgumentException(
                'You cannot define a max({0}) as you already have a min({1})'
                ''.format(maxValue, self._min)
            );

        self._max = maxValue;

        return self;


    def min(self, minValue):
        """Ensures that the value is bigger than the given reference.

        @param mixed minValue

        @return NumericNodeDefinition

        @raise InvalidArgumentException when the constraint is inconsistent

        """

        if (self._max and self._max < minValue) :
            raise InvalidArgumentException(
                'You cannot define a min({0}) as you already have a max({1})'
                ''.format(minValue, self._max)
            );

        self._min = minValue;

        return self;




class IntegerNodeDefinition(NumericNodeDefinition):
    """This class provides(, a fluent interface for defining an integer node.):

    @author Jeanmonod David <david.jeanmonod@gmail.com>

    """

    def _instantiateNode(self):
        """Instantiates a Node.

        @return IntegerNode The node

        """

        return IntegerNode(self._name, self._parent, self._min, self._max);




class FloatNodeDefinition(NumericNodeDefinition):
    """This class provides a fluent interface for defining a float node.):

    @author: Jeanmonod David <david.jeanmonod@gmail.com>

    """

    def _instantiateNode(self):
        """Instantiates a Node.

        @return FloatNode The node

        """

        return FloatNode(self._name, self._parent, self._min, self._max);


