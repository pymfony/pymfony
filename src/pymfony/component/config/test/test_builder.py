# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import unittest;

from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import RuntimeException;
from pymfony.component.system.reflection import ReflectionObject;

from pymfony.component.config.definition.builder import ArrayNodeDefinition;
from pymfony.component.config.definition.builder import ScalarNodeDefinition;
from pymfony.component.config.definition.builder import VariableNodeDefinition as BaseVariableNodeDefinition;
from pymfony.component.config.definition.builder import NodeDefinition;
from pymfony.component.config.definition.builder import EnumNodeDefinition;
from pymfony.component.config.definition.builder import NumericNodeDefinition;
from pymfony.component.config.definition.builder import IntegerNodeDefinition;
from pymfony.component.config.definition.builder import FloatNodeDefinition;
from pymfony.component.config.definition.builder import TreeBuilder;
from pymfony.component.config.definition.builder import NodeBuilder;
from pymfony.component.config.definition.exception import InvalidDefinitionException;
from pymfony.component.config.definition.exception import InvalidConfigurationException;

"""
"""

class CustomNodeBuilder(NodeBuilder):

    def barNode(self, name):
        return self.node(name, 'bar');

    def _getNodeClass(self, typeName):
        if  'variable' == typeName:
            return __name__+'.'+typeName.capitalize()+'NodeDefinition';
        elif 'bar' == typeName:
            return __name__+'.'+typeName.capitalize()+'NodeDefinition';
        else:
            return NodeBuilder._getNodeClass(self, typeName);

class BarNodeDefinition(NodeDefinition):
    def _createNode(self):
        pass;

class VariableNodeDefinition(BaseVariableNodeDefinition):
    pass;


class ArrayNodeDefinitionTest(unittest.TestCase):

    def testAppendingSomeNode(self):

        parent = ArrayNodeDefinition('root');
        child = ScalarNodeDefinition('child');

        node = parent.children();
        node =      node.scalarNode('foo').end();
        node =      node.scalarNode('bar').end();
        node = node.end();
        node = node.append(child);

        self.assertEqual(3, len(self._getField(parent, '_children')));
        self.assertTrue(child in self._getField(parent, '_children').values());


    def testPrototypeNodeSpecificOption(self):
        """
        @expectedException Symfony\Component\Config\Definition\Exception\InvalidDefinitionException
        @dataProvider providePrototypeNodeSpecificCalls:

        """
        def test(method, args):
            node = ArrayNodeDefinition('root');

            getattr(node, method)(*args);

            node.getNode();

        for args in self.providePrototypeNodeSpecificCalls():
            self.assertRaises(InvalidDefinitionException, test, *args);


    def providePrototypeNodeSpecificCalls(self):

        return [
            ('defaultValue',[{}]),
            ('addDefaultChildrenIfNoneSet', []),
            ('requiresAtLeastOneElement', []),
            ('useAttributeAsKey', ['foo']),
        ];


    def testConcreteNodeSpecificOption(self):
        """
        @expectedException Symfony\Component\Config\Definition\Exception\InvalidDefinitionException

        """

        def test():
            node = ArrayNodeDefinition('root');
            node.addDefaultsIfNotSet().prototype('array');
            node.getNode();
        self.assertRaises(InvalidDefinitionException, test);

    def testPrototypeNodesCantHaveADefaultValueWhenUsingDefaultChildren(self):
        """
        @expectedException Symfony\Component\Config\Definition\Exception\InvalidDefinitionException

        """

        def test():
            node = ArrayNodeDefinition('root');
            n = node;
            n =    n.defaultValue({});
            n =    n.addDefaultChildrenIfNoneSet('foo');
            n =    n.prototype('array');

            node.getNode();

        self.assertRaises(InvalidDefinitionException, test);



    def testPrototypedArrayNodeDefaultWhenUsingDefaultChildren(self):

        node = ArrayNodeDefinition('root');
        n = node
        n =    n.addDefaultChildrenIfNoneSet();
        n =    n.prototype('array');

        tree = node.getNode();
        self.assertEqual({0:{}}, tree.getDefaultValue());


    def testPrototypedArrayNodeDefault(self):
        """
        @dataProvider providePrototypedArrayNodeDefaults

        """
        def test(args, shouldThrowWhenUsingAttrAsKey, shouldThrowWhenNotUsingAttrAsKey, defaults):
            node = ArrayNodeDefinition('root');
            n = node
            n =    n.addDefaultChildrenIfNoneSet(args)
            n =    n.prototype('array')

            try:
                tree = node.getNode();
                self.assertFalse(shouldThrowWhenNotUsingAttrAsKey);
                self.assertEqual(defaults, tree.getDefaultValue());
            except InvalidDefinitionException:
                self.assertTrue(shouldThrowWhenNotUsingAttrAsKey);


            node = ArrayNodeDefinition('root');
            n = node
            n =    n.useAttributeAsKey('attr')
            n =    n.addDefaultChildrenIfNoneSet(args)
            n =    n.prototype('array')

    
            try:
                tree = node.getNode();
                self.assertFalse(shouldThrowWhenUsingAttrAsKey);
                self.assertEqual(defaults, tree.getDefaultValue());
            except InvalidDefinitionException:
                self.assertTrue(shouldThrowWhenUsingAttrAsKey);

        for args in self.providePrototypedArrayNodeDefaults():
            test(*args);



    def providePrototypedArrayNodeDefaults(self):

        return [
            (None, True, False, {0:{}}),
            (2, True, False, {0:{}, 1:{}}),
            ('2', False, True, {'2': {}}),
            ('foo', False, True, {'foo': {}}),
            ({0:'foo'}, False, True, {'foo': {}}),
            ({0:'foo', 1:'bar'}, False, True, {'foo': {}, 'bar': {}}),
        ];


    def testNestedPrototypedArrayNodes(self):

        node = ArrayNodeDefinition('root');
        n = node
        n =     n.addDefaultChildrenIfNoneSet()
        n =     n.prototype('array')
        n =         n.prototype('array')
        node.getNode();


    def _getField(self, obj, field):

        return getattr(obj, field);


class EnumNodeDefinitionTest(unittest.TestCase):

    def testNoDistinctValues(self):
        """
        @expectedException InvalidArgumentException
        @expectedExceptionMessage .values() must be called with at least two distinct values.

        """

        try:
            node = EnumNodeDefinition('foo');
            node.values(['foo', 'foo']);
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));
            self.assertEqual(e.getMessage(), ".values() must be called with at least two distinct values.");



    def testNoValuesPassed(self):
        """
        @expectedException RuntimeException
        @expectedExceptionMessage You must call .values() on enum nodes.

        """

        try:
            node = EnumNodeDefinition('foo');
            node.getNode();
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));
            self.assertEqual(e.getMessage(), "You must call .values() on enum nodes.");



    def testGetNode(self):

        enum = EnumNodeDefinition('foo');
        enum.values(['foo', 'bar']);

        node = enum.getNode();
        self.assertEqual(['foo', 'bar'], node.getValues());



class ExprBuilderTest(unittest.TestCase):


    def testAlwaysExpression(self):

        test = self._getTestBuilder()
        test =     test.always(self._returnClosure('new_value'))
        test = test.end();

        self._assertFinalizedValueIs('new_value', test);


    def testIfTrueExpression(self):

        test = self._getTestBuilder()
        test =     test.ifTrue();
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('new_value', test, {'key': True});

        test = self._getTestBuilder()
        test =     test.ifTrue(lambda v: True);
        test =     test.then(self._returnClosure('new_value'));
        test = test.end();
        self._assertFinalizedValueIs('new_value', test);

        test = self._getTestBuilder()
        test =     test.ifTrue(lambda v: False);
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('value',test);


    def testIfStringExpression(self):

        test = self._getTestBuilder()
        test =     test.ifString();
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('new_value', test);

        test = self._getTestBuilder()
        test =     test.ifString();
        test =     test.then(self._returnClosure('new_value'));
        test = test.end();
        self._assertFinalizedValueIs(45, test, {'key': 45});



    def testIfNullExpression(self):

        test = self._getTestBuilder()
        test =     test.ifNull();
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('new_value', test, {'key':None});

        test = self._getTestBuilder()
        test =     test.ifNull();
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('value', test);


    def testIfArrayExpression(self):

        test = self._getTestBuilder()
        test =     test.ifArray();
        test =     test.then(self._returnClosure('new_value'));
        test = test.end();
        self._assertFinalizedValueIs('new_value', test, {'key':{}});

        test = self._getTestBuilder()
        test =     test.ifArray();
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('value', test);


    def testIfInArrayExpression(self):

        test = self._getTestBuilder()
        test =     test.ifInArray(['foo', 'bar', 'value']);
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('new_value', test);

        test = self._getTestBuilder()
        test =     test.ifInArray(['foo', 'bar']);
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('value', test);


    def testIfNotInArrayExpression(self):

        test = self._getTestBuilder()
        test =     test.ifNotInArray(['foo', 'bar']);
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('new_value', test);

        test = self._getTestBuilder()
        test =     test.ifNotInArray(['foo', 'bar', 'value_from_config']);
        test =     test.then(self._returnClosure('new_value'))
        test = test.end();
        self._assertFinalizedValueIs('new_value', test);


    def testThenEmptyArrayExpression(self):

        test = self._getTestBuilder()
        test =     test.ifString();
        test =     test.thenEmptyArray()
        test = test.end();
        self._assertFinalizedValueIs({}, test);


    def testThenInvalid(self):
        """
        @expectedException Symfony\Component\Config\Definition\Exception\InvalidConfigurationException

        """

        def test():
            test = self._getTestBuilder()
            test =     test.ifString();
            test =     test.thenInvalid('Invalid value')
            test = test.end();
            self._finalizeTestBuilder(test);

        self.assertRaises(InvalidConfigurationException, test);


    def testThenUnsetExpression(self):

        test = self._getTestBuilder()
        test =     test.ifString();
        test =     test.thenUnset()
        test = test.end();
        self.assertEqual({}, self._finalizeTestBuilder(test));


    def _getTestBuilder(self):
        """Create a test treebuilder with a variable node, and init the validation

        @return TreeBuilder

        """

        builder = TreeBuilder();

        builder = builder.root('test')
        builder = builder.children()
        builder = builder.variableNode('key')
        builder = builder.validate()

        return builder;


    def _finalizeTestBuilder(self, testBuilder, config = None):
        """Close the validation process and finalize with the given config

        @param TreeBuilder testBuilder The tree builder to finalize
        @param array       config      The config you want to use for the finalization, if nothing provided:
                               a simple array('key'=>'value') will be used

        @return array The finalized config values

        """

        v = testBuilder.end().end().end().buildTree();

        if config is None:
            config = {'key':'value'}

        return v.finalize(config);

    def _returnClosure(self, val):
        """Return a closure that will return the given value

        @param val The value that the closure must return

        @return Closure

        """

        return lambda v: val;


    def _assertFinalizedValueIs(self, value, treeBuilder, config = None):
        """Assert that the given test builder, will return the given value

        @param mixed       value       The value to test
        @param TreeBuilder treeBuilder The tree builder to finalize
        @param mixed       config      The config values that new to be finalized

        """

        self.assertEqual({'key':value}, self._finalizeTestBuilder(treeBuilder, config));


class NumericNodeDefinitionTest(unittest.TestCase):

    def testIncoherentMinAssertion(self):
        """
        @expectedException InvalidArgumentException
        @expectedExceptionMessage You cannot define a min(4) as you already have a max(3)

        """

        try:
            node = NumericNodeDefinition('foo');
            node.max(3).min(4);
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));
            self.assertEqual(e.getMessage(), "You cannot define a min(4) as you already have a max(3)");

    def testIncoherentMaxAssertion(self):
        """
        @expectedException InvalidArgumentException
        @expectedExceptionMessage You cannot define a max(2) as you already have a min(3)

        """
        try:
            node = NumericNodeDefinition('foo');
            node.min(3).max(2);
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));
            self.assertEqual(e.getMessage(), "You cannot define a max(2) as you already have a min(3)");



    def testIntegerMinAssertion(self):
        """
        @expectedException Symfony\Component\Config\Definition\Exception\InvalidConfigurationException
        @expectedExceptionMessage The value 4 is too small for path "foo". Should be greater than: 5

        """

        try:
            node = IntegerNodeDefinition('foo');
            node.min(5).getNode().finalize(4);
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidConfigurationException));
            self.assertEqual(e.getMessage(), 'The value 4 is too small for path "foo". Should be greater than: 5');



    def testIntegerMaxAssertion(self):
        """
        @expectedException Symfony\Component\Config\Definition\Exception\InvalidConfigurationException
        @expectedExceptionMessage The value 4 is too big for path "foo". Should be less than: 3

        """
        try:
            node = IntegerNodeDefinition('foo');
            node.max(3).getNode().finalize(4);
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidConfigurationException));
            self.assertEqual(e.getMessage(), 'The value 4 is too big for path "foo". Should be less than: 3');



    def testIntegerValidMinMaxAssertion(self):

        node = IntegerNodeDefinition('foo');
        node = node.min(3).max(7).getNode();
        self.assertEqual(4, node.finalize(4));


    def testFloatMinAssertion(self):
        """
        @expectedException Symfony\Component\Config\Definition\Exception\InvalidConfigurationException
        @expectedExceptionMessage The value 400 is too small for path "foo". Should be greater than: 500

        """
        try:
            node = FloatNodeDefinition('foo');
            node.min(5e2).getNode().finalize(4e2);
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidConfigurationException));
            self.assertEqual(e.getMessage(), 'The value 400.0 is too small for path "foo". Should be greater than: 500.0');



    def testFloatMaxAssertion(self):
        """
        @expectedException Symfony\Component\Config\Definition\Exception\InvalidConfigurationException
        @expectedExceptionMessage The value 4.3 is too big for path "foo". Should be less than: 0.3

        """
        try:
            node = FloatNodeDefinition('foo');
            node.max(0.3).getNode().finalize(4.3);
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidConfigurationException));
            self.assertEqual(e.getMessage(), 'The value 4.3 is too big for path "foo". Should be less than: 0.3');



    def testFloatValidMinMaxAssertion(self):

        node = FloatNodeDefinition('foo');
        node = node.min(3.0).max(7e2).getNode();
        self.assertEqual(4.5, node.finalize(4.5));


class NodeBuilderTest(unittest.TestCase):

    def testThrowsAnExceptionWhenTryingToCreateANonRegisteredNodeType(self):
        """
        @expectedException RuntimeException

        """

        def test():
            builder = NodeBuilder();
            builder.node('', 'foobar');
        self.assertRaises(RuntimeException, test);


    def testThrowsAnExceptionWhenTheNodeClassIsNotFound(self):
        """
        @expectedException RuntimeException

        """

        def test():
            builder = NodeBuilder();
            builder =    builder.setNodeClass('noclasstype', 'foo.bar.noclass')
            builder =    builder.node('', 'noclasstype');

        self.assertRaises(RuntimeException, test);

    def testAddingANewNodeType(self):

        className = __name__ + '.SomeNodeDefinition';

        builder = NodeBuilder();
        node = builder
        node =     node.setNodeClass('newtype', className)
        node =     node.node('', 'newtype');

        self.assertEqual(ReflectionObject(node).getName(), className);


    def testOverridingAnExistingNodeType(self):

        className = __name__ + '.SomeNodeDefinition';

        builder = NodeBuilder();
        node = builder
        node =     node.setNodeClass('variable', className)
        node =     node.node('', 'variable');

        self.assertEqual(ReflectionObject(node).getName(), className);


    def testNodeTypesAreNotCaseSensitive(self):

        builder = NodeBuilder();

        node1 = builder.node('', 'VaRiAbLe');
        node2 = builder.node('', 'variable');

        self.assertEqual(ReflectionObject(node1).getName(), ReflectionObject(node2).getName());

        builder.setNodeClass('CuStOm', __name__ + '.SomeNodeDefinition');

        node1 = builder.node('', 'CUSTOM');
        node2 = builder.node('', 'custom');

        self.assertEqual(ReflectionObject(node1).getName(), ReflectionObject(node2).getName());


    def testNumericNodeCreation(self):

        builder = NodeBuilder();

        node = builder.integerNode('foo').min(3).max(5);
        self.assertEqual('pymfony.component.config.definition.builder.IntegerNodeDefinition', ReflectionObject(node).getName());

        node = builder.floatNode('bar').min(3.0).max(5.0);
        self.assertEqual('pymfony.component.config.definition.builder.FloatNodeDefinition', ReflectionObject(node).getName());



class SomeNodeDefinition(BaseVariableNodeDefinition):
    pass;

class TreeBuilderTest(unittest.TestCase):

    def testUsingACustomNodeBuilder(self):

        builder = TreeBuilder();
        root = builder.root('custom', 'array', CustomNodeBuilder());

        nodeBuilder = root.children();

        self.assertEqual(ReflectionObject(nodeBuilder).getName(), __name__ + '.CustomNodeBuilder');

        nodeBuilder = nodeBuilder.arrayNode('deeper').children();

        self.assertEqual(ReflectionObject(nodeBuilder).getName(), __name__ + '.CustomNodeBuilder');


    def testOverrideABuiltInNodeType(self):

        builder = TreeBuilder();
        root = builder.root('override', 'array', CustomNodeBuilder());

        definition = root.children().variableNode('variable');

        self.assertEqual(ReflectionObject(definition).getName(), __name__ + '.VariableNodeDefinition');


    def testAddANodeType(self):

        builder = TreeBuilder();
        root = builder.root('override', 'array', CustomNodeBuilder());

        definition = root.children().barNode('variable');

        self.assertEqual(ReflectionObject(definition).getName(), __name__ + '.BarNodeDefinition');


    def testCreateABuiltInNodeTypeWithACustomNodeBuilder(self):

        builder = TreeBuilder();
        root = builder.root('builtin', 'array', CustomNodeBuilder());

        definition = root.children().booleanNode('boolean');

        self.assertEqual(ReflectionObject(definition).getName(), 'pymfony.component.config.definition.builder.BooleanNodeDefinition');


    def testPrototypedArrayNodeUseTheCustomNodeBuilder(self):

        builder = TreeBuilder();
        root = builder.root('override', 'array', CustomNodeBuilder());

        root.prototype('bar').end();


    def testAnExtendedNodeBuilderGetsPropagatedToTheChildren(self):

        builder = TreeBuilder();

        n = builder.root('propagation')
        n =     n.children()
        n =         n.setNodeClass('extended', __name__ + '.VariableNodeDefinition')
        n =         n.node('foo', 'extended').end()
        n =         n.arrayNode('child')
        n =             n.children()
        n =                 n.node('foo', 'extended')
        n =             n.end()
        n =         n.end()
        n =     n.end();


    def testDefinitionInfoGetsTransferredToNode(self):

        builder = TreeBuilder();

        n = builder.root('test').info('root info')
        n =     n.children()
        n =         n.node('child', 'variable').info('child info').defaultValue('default')
        n =     n.end()
        n = n.end();

        tree = builder.buildTree();
        children = tree.getChildren();

        self.assertEqual('root info', tree.getInfo());
        self.assertEqual('child info', children['child'].getInfo());


    def testDefinitionExampleGetsTransferredToNode(self):

        builder = TreeBuilder();

        n = builder.root('test')
        n =     n.example({'key': 'value'})
        n =     n.children()
        n =         n.node('child', 'variable').info('child info').defaultValue('default').example('example')
        n =     n.end()
        n = n.end();

        tree = builder.buildTree();
        children = tree.getChildren();

        self.assertTrue(isinstance(tree.getExample(), dict));
        self.assertEqual('example', children['child'].getExample());


if __name__ == '__main__':
    unittest.main();
