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

from pymfony.component.config.definition import ScalarNode;
from pymfony.component.config.definition import BooleanNode;
from pymfony.component.config.definition import FloatNode;
from pymfony.component.config.definition import IntegerNode;
from pymfony.component.config.definition import EnumNode;
from pymfony.component.config.definition import ArrayNode;
from pymfony.component.config.definition import PrototypedArrayNode;
from pymfony.component.config.definition import NodeInterface;
from pymfony.component.config.definition import Processor;
from pymfony.component.config.definition.builder import TreeBuilder;
from pymfony.component.config.definition.exception import InvalidTypeException;
from pymfony.component.config.definition.exception import InvalidConfigurationException;
from pymfony.component.config.definition.exception import ForbiddenOverwriteException;

"""
"""


class ScalarNodeTest(unittest.TestCase):

    def testNormalize(self):
        """@dataProvider getValidValues

        """
        def test(value):
            node = ScalarNode('test');
            self.assertEqual(value, node.normalize(value));

        for args in self.getValidValues():
            test(*args);

    def getValidValues(self):

        return [
            [False],
            [True],
            [None],
            [''],
            ['foo'],
            [0],
            [1],
            [0.0],
            [0.1],
        ];


    def testNormalizeThrowsExceptionOnInvalidValues(self):
        """@dataProvider getInvalidValues
     * @expectedException Symfony\Component\Config\Definition\Exception\InvalidTypeException

        """

        def test(value):
            node = ScalarNode('test');
            node.normalize(value);

        for args in self.getInvalidValues():
            self.assertRaises(InvalidTypeException, test, *args);


    def getInvalidValues(self):

        return [
            [[]],
            [{'foo': 'bar'}],
            [object()],
        ];




class BooleanNodeTest(unittest.TestCase):

    def testNormalize(self):
        """@dataProvider getValidValues

        """

        def test(value):
            node = BooleanNode('test');
            self.assertEqual(value, node.normalize(value));

        for args in self.getValidValues():
            test(*args);


    def getValidValues(self):

        return [
            [False],
            [True],
        ];


    def testNormalizeThrowsExceptionOnInvalidValues(self):
        """@dataProvider getInvalidValues
     * @expectedException Symfony\Component\Config\Definition\Exception\InvalidTypeException

        """

        def test(value):
            node = BooleanNode('test');
            node.normalize(value);

        for args in self.getInvalidValues():
            self.assertRaises(InvalidTypeException, test, *args);


    def getInvalidValues(self):

        return [
            [None],
            [''],
            ['foo'],
            [0],
            [1],
            [0.0],
            [0.1],
            [[]],
            [{'foo': 'bar'}],
            [object()],
        ];




class FloatNodeTest(unittest.TestCase):

    def testNormalize(self):
        """@dataProvider getValidValues

        """

        def test(value):
            node = FloatNode('test');
            self.assertEqual(value, node.normalize(value));

        for args in self.getValidValues():
            test(*args);


    def getValidValues(self):

        return [
            [1798.0],
            [-678.987],
            [12.56e45],
            [0.0],
            # Integer are accepted too, they will be cast
            [17],
            [-10],
            [0]
        ];


    def testNormalizeThrowsExceptionOnInvalidValues(self):
        """@dataProvider getInvalidValues
     * @expectedException Symfony\Component\Config\Definition\Exception\InvalidTypeException

        """

        def test(value):
            node = FloatNode('test');
            node.normalize(value);

        for args in self.getInvalidValues():
            self.assertRaises(InvalidTypeException, test, *args);


    def getInvalidValues(self):

        return [
            [None],
            [''],
            ['foo'],
            [True],
            [False],
            [[]],
            [{'foo': 'bar'}],
            [object()],
        ];




class IntegerNodeTest(unittest.TestCase):

    def testNormalize(self):
        """@dataProvider getValidValues

        """

        def test(value):
            node = IntegerNode('test');
            self.assertEqual(value, node.normalize(value));

        for args in self.getValidValues():
            test(*args);

    def getValidValues(self):

        return [
            [1798],
            [-678],
            [0],
        ];


    def testNormalizeThrowsExceptionOnInvalidValues(self):
        """@dataProvider getInvalidValues
     * @expectedException Symfony\Component\Config\Definition\Exception\InvalidTypeException

        """

        def test(value):
            node = IntegerNode('test');
            node.normalize(value);

        for args in self.getInvalidValues():
            self.assertRaises(InvalidTypeException, test, *args);


    def getInvalidValues(self):

        return [
            [None],
            [''],
            ['foo'],
            [True],
            [False],
            [0.0],
            [0.1],
            [[]],
            [{'foo': 'bar'}],
            [object()],
        ];




class EnumNodeTest(unittest.TestCase):

    def testFinalizeValue(self):

        node = EnumNode('foo', None, ['foo', 'bar']);
        self.assertEqual('foo', node.finalize('foo'));


    def testConstructionWithOneValue(self):
        """@expectedException InvalidArgumentException

        """

        self.assertRaises(InvalidArgumentException, EnumNode, 'foo', None, ['foo', 'foo']);


    def testFinalizeWithInvalidValue(self):
        """@expectedException Symfony\Component\Config\Definition\Exception\InvalidConfigurationException
     * @expectedExceptionMessage The value "foobar" is not allowed for path "foo". Permissible values: "foo", "bar"

        """

        try:
            node = EnumNode('foo', None, ['foo', 'bar']);
            node.finalize('foobar');
            self.fail('The value "foobar" is not allowed for path "foo". Permissible values: "foo", "bar"')
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidConfigurationException));
            self.assertEqual(e.getMessage(), 'The value "foobar" is not allowed for path "foo". Permissible values: "foo", "bar"');




class ArrayNodeTest(unittest.TestCase):

    def testNormalizeThrowsExceptionWhenFalseIsNotAllowed(self):
        """@expectedException Symfony\Component\Config\Definition\Exception\InvalidTypeException

        """


        try:
            node = ArrayNode('root');
            node.normalize(False);
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidTypeException));




    def testExceptionThrownOnUnrecognizedChild(self):
        """normalize() should protect against child values with no corresponding node

        """

        node = ArrayNode('root');

        try:
            node.normalize({'foo': 'bar'});
            self.fail('An exception should have been raise for a bad child node');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidConfigurationException));
            self.assertEqual('Unrecognized options "foo" under "root"', e.getMessage());



    def testIgnoreExtraKeysNoException(self):
        """Tests that no exception is thrown for an unrecognized child if the:
     * ignoreExtraKeys option is set to True.
     *
     * Related to testExceptionThrownOnUnrecognizedChild

        """

        node = ArrayNode('roo');
        node.setIgnoreExtraKeys(True);

        node.normalize({'foo': 'bar'});
        self.assertTrue(True, 'No exception was thrown when setIgnoreExtraKeys is True');


    def testPreNormalize(self):
        """@dataProvider getPreNormalizationTests

        """

        def test(denormalized, normalized):
            node = ArrayNode('foo');

            self.assertEqual(normalized, node._preNormalize(denormalized));

        for data in self.getPreNormalizationTests():
            test(*data);




    def getPreNormalizationTests(self):

        return [
            [
                {'foo-bar': 'foo'},
                {'foo_bar': 'foo'},
            ],
            [
                {'foo-bar_moo': 'foo'},
                {'foo-bar_moo': 'foo'},
            ],
            [
                {'foo-bar': None, 'foo_bar': 'foo'},
                {'foo-bar': None, 'foo_bar': 'foo'},
            ]
        ];




class PrototypedArrayNodeTest(unittest.TestCase):

    def testGetDefaultValueReturnsAnEmptyArrayForPrototypes(self):

        node = PrototypedArrayNode('root');
        prototype = ArrayNode("", node);
        node.setPrototype(prototype);
        self.assertFalse(node.getDefaultValue());


    def testGetDefaultValueReturnsDefaultValueForPrototypes(self):

        node = PrototypedArrayNode('root');
        prototype = ArrayNode("", node);
        node.setPrototype(prototype);
        node.setDefaultValue(['test']);
        self.assertEqual({0: 'test'}, node.getDefaultValue());


    # a remapped key (e.g. "mapping" -> "mappings") should be unset after being used
    def testRemappedKeysAreUnset(self):

        node = ArrayNode('root');
        mappingsNode = PrototypedArrayNode('mappings');
        node.addChild(mappingsNode);

        # each item under mappings is just a scalar
        prototype = ScalarNode("", mappingsNode);
        mappingsNode.setPrototype(prototype);

        remappings = [];
        remappings.append(['mapping', 'mappings']);
        node.setXmlRemappings(remappings);

        normalized = node.normalize({'mapping': ['foo', 'bar']});
        self.assertEqual({'mappings': {0: 'foo', 1: 'bar'}}, normalized);


    def testMappedAttributeKeyIsRemoved(self):
        """Tests that when a key attribute is mapped, that key is removed from the array:
     *
     *     <things>
     *         <option id="option1" value="foo">
     *         <option id="option2" value="bar">
     *     </things>
     *
     * The above should finally be mapped to an array that looks like this
     * (because "id" is the key attribute).
     *
     *     array(
     *         'things' => array(
     *             'option1' => 'foo',
     *             'option2' => 'bar',
     *         )
     *     )

        """

        node = PrototypedArrayNode('root');
        node.setKeyAttribute('id', True);

        # each item under the root is an array, with one scalar item
        prototype = ArrayNode("", node);
        prototype.addChild(ScalarNode('foo'));
        node.setPrototype(prototype);

        children = [];
        children.append({'id': 'item_name', 'foo': 'bar'});
        normalized = node.normalize(children);

        expected = dict();
        expected['item_name'] = {'foo': 'bar'};
        self.assertEqual(expected, normalized);


    def testMappedAttributeKeyNotRemoved(self):
        """Tests the opposite of the testMappedAttributeKeyIsRemoved because
     * the removal can be toggled with an option.

        """

        node = PrototypedArrayNode('root');
        node.setKeyAttribute('id', False);

        # each item under the root is an array, with two scalar items
        prototype = ArrayNode("", node);
        prototype.addChild(ScalarNode('foo'));
        prototype.addChild(ScalarNode('id')); # the key attribute will remain
        node.setPrototype(prototype);

        children = list();
        children.append({'id': 'item_name', 'foo': 'bar'});
        normalized = node.normalize(children);

        expected = dict();
        expected['item_name'] = {'id': 'item_name', 'foo': 'bar'};
        self.assertEqual(expected, normalized);


    def testAddDefaultChildren(self):

        node = self._getPrototypeNodeWithDefaultChildren();
        node.setAddChildrenIfNoneSet();
        self.assertTrue(node.hasDefaultValue());
        self.assertEqual({0: {'foo': 'bar'}}, node.getDefaultValue());

        node = self._getPrototypeNodeWithDefaultChildren();
        node.setKeyAttribute('foobar');
        node.setAddChildrenIfNoneSet();
        self.assertTrue(node.hasDefaultValue());
        self.assertEqual({'defaults': {'foo': 'bar'}}, node.getDefaultValue());

        node = self._getPrototypeNodeWithDefaultChildren();
        node.setKeyAttribute('foobar');
        node.setAddChildrenIfNoneSet('defaultkey');
        self.assertTrue(node.hasDefaultValue());
        self.assertEqual({'defaultkey': {'foo': 'bar'}}, node.getDefaultValue());

        node = self._getPrototypeNodeWithDefaultChildren();
        node.setKeyAttribute('foobar');
        node.setAddChildrenIfNoneSet(['defaultkey']);
        self.assertTrue(node.hasDefaultValue());
        self.assertEqual({'defaultkey': {'foo': 'bar'}}, node.getDefaultValue());

        node = self._getPrototypeNodeWithDefaultChildren();
        node.setKeyAttribute('foobar');
        node.setAddChildrenIfNoneSet(['dk1', 'dk2']);
        self.assertTrue(node.hasDefaultValue());
        self.assertEqual({'dk1': {'foo': 'bar'}, 'dk2' : {'foo' : 'bar'}}, node.getDefaultValue());

        node = self._getPrototypeNodeWithDefaultChildren();
        node.setAddChildrenIfNoneSet([5, 6]);
        self.assertTrue(node.hasDefaultValue());
        self.assertEqual({0: {'foo' : 'bar'}, 1: {'foo' : 'bar'}}, node.getDefaultValue());

        node = self._getPrototypeNodeWithDefaultChildren();
        node.setAddChildrenIfNoneSet(2);
        self.assertTrue(node.hasDefaultValue());
        self.assertEqual({0: {'foo': 'bar'}, 1: {'foo': 'bar'}}, node.getDefaultValue());


    def testDefaultChildrenWinsOverDefaultValue(self):

        node = self._getPrototypeNodeWithDefaultChildren();
        node.setAddChildrenIfNoneSet();
        node.setDefaultValue({'bar': 'foo'});
        self.assertTrue(node.hasDefaultValue());
        self.assertEqual({0: {'foo': 'bar'}}, node.getDefaultValue());


    def _getPrototypeNodeWithDefaultChildren(self):

        node = PrototypedArrayNode('root');
        prototype = ArrayNode("", node);
        child = ScalarNode('foo');
        child.setDefaultValue('bar');
        prototype.addChild(child);
        prototype.setAddIfNotSet(True);
        node.setPrototype(prototype);

        return node;




class NormalizerTest(unittest.TestCase):

    def testNormalizeEncoders(self):
        """@dataProvider getEncoderTests

        """

        def test(denormalized):
            tb = TreeBuilder();
            tree = tb
            tree =     tree.root('root_name', 'array')
            tree =         tree.fixXmlConfig('encoder')
            tree =         tree.children()
            tree =             tree.node('encoders', 'array')
            tree =                 tree.useAttributeAsKey('class')
            tree =                 tree.prototype('array')
            tree =                     tree.beforeNormalization().ifString().then(lambda v: {'algorithm': v}).end()
            tree =                     tree.children()
            tree =                         tree.node('algorithm', 'scalar').end()
            tree =                     tree.end()
            tree =                 tree.end()
            tree =             tree.end()
            tree =         tree.end()
            tree =     tree.end()
            tree =     tree.buildTree();

            normalized = {
                'encoders': {
                    'foo': {'algorithm': 'plaintext'},
                },
            };

            self.assertNormalized(tree, denormalized, normalized);

        for data in self.getEncoderTests():
            test(*data);




    def getEncoderTests(self):

        configs = list();

        # XML
        configs.append({
            'encoder': [
                {'class': 'foo', 'algorithm': 'plaintext'},
            ],
        });

        # XML when only one element of this type
        configs.append({
            'encoder': {'class': 'foo', 'algorithm': 'plaintext'},
        });

        # YAML/PHP
        configs.append({
            'encoders': [
                {'class': 'foo', 'algorithm': 'plaintext'},
            ],
        });

        # YAML/PHP
        configs.append({
            'encoders': {
                'foo': 'plaintext',
            },
        });

        # YAML/PHP
        configs.append({
            'encoders': {
                'foo': {'algorithm': 'plaintext'},
            },
        });

        return list(map(lambda v: [v], configs));


    def testAnonymousKeysArray(self):
        """@dataProvider getAnonymousKeysTests

        """

        def test(denormalized):
            tb = TreeBuilder();
            tree = tb
            tree =     tree.root('root', 'array')
            tree =         tree.children()
            tree =             tree.node('logout', 'array')
            tree =                 tree.fixXmlConfig('handler')
            tree =                 tree.children()
            tree =                     tree.node('handlers', 'array')
            tree =                         tree.prototype('scalar').end()
            tree =                     tree.end()
            tree =                 tree.end()
            tree =             tree.end()
            tree =         tree.end()
            tree =     tree.end()
            tree =     tree.buildTree();

            normalized = {'logout': {'handlers': {0: 'a', 1: 'b', 2: 'c'}}};

            self.assertNormalized(tree, denormalized, normalized);

        for data in self.getAnonymousKeysTests():
            test(*data);



    def getAnonymousKeysTests(self):

        configs = list();

        configs.append({
            'logout': {
                'handlers': ['a', 'b', 'c'],
            },
        });

        configs.append({
            'logout': {
                'handler': ['a', 'b', 'c'],
            },
        });

        return list(map(lambda v: [v], configs));


    def testNumericKeysAsAttributes(self):
        """@dataProvider getNumericKeysTests

        """
        def test(denormalized):
            normalized = {
                'thing': {42: {0: 'foo', 1: 'bar'}, 1337: {0: 'baz', 1: 'qux'}},
            };

            self.assertNormalized(self.__getNumericKeysTestTree(), denormalized, normalized);

        for data in self.getNumericKeysTests():
            test(*data);



    def getNumericKeysTests(self):

        configs = list();

        configs.append({
            'thing': {
                42: ['foo', 'bar'], 1337: ['baz', 'qux'],
            },
        });

        configs.append({
            'thing': [
                {0: 'foo', 1: 'bar', 'id': 42}, {0: 'baz', 1: 'qux', 'id': 1337},
            ],
        });

        return list(map(lambda v: [v], configs));


    def testNonAssociativeArrayThrowsExceptionIfAttributeNotSet(self):
        """@expectedException Symfony\Component\Config\Definition\Exception\InvalidConfigurationException
     * @expectedExceptionMessage The attribute "id" must be set for path "root.thing".

        """

        try:
            denormalized = {
                'thing': [
                    ['foo', 'bar'], ['baz', 'qux']
                ]
            };
            self.assertNormalized(self.__getNumericKeysTestTree(), denormalized, list());

            self.fail('The attribute "id" must be set for path "root.thing".')
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidConfigurationException));
            self.assertEqual(e.getMessage(), 'The attribute "id" must be set for path "root.thing".');






    def testAssociativeArrayPreserveKeys(self):

        tb = TreeBuilder();
        tree = tb
        tree =     tree.root('root', 'array')
        tree =         tree.prototype('array')
        tree =             tree.children()
        tree =                 tree.node('foo', 'scalar').end()
        tree =             tree.end()
        tree =         tree.end()
        tree =     tree.end()
        tree =     tree.buildTree();

        data = {'first': {'foo': 'bar'}};

        self.assertNormalized(tree, data, data);


    def assertNormalized(self, tree, denormalized, normalized):
        assert isinstance(tree, NodeInterface);

        self.assertEqual(normalized, tree.normalize(denormalized));


    def __getNumericKeysTestTree(self):

        tb = TreeBuilder();
        tree = tb
        tree =     tree.root('root', 'array')
        tree =         tree.children()
        tree =             tree.node('thing', 'array')
        tree =                 tree.useAttributeAsKey('id')
        tree =                 tree.prototype('array')
        tree =                     tree.prototype('scalar').end()
        tree =                 tree.end()
        tree =             tree.end()
        tree =         tree.end()
        tree =     tree.end()
        tree =     tree.buildTree();

        return tree;




class FinalizationTest(unittest.TestCase):

    def testUnsetKeyWithDeepHierarchy(self):

        tb = TreeBuilder();
        tree = tb
        tree =     tree.root('config', 'array')
        tree =         tree.children()
        tree =             tree.node('level1', 'array')
        tree =                 tree.canBeUnset()
        tree =                 tree.children()
        tree =                     tree.node('level2', 'array')
        tree =                         tree.canBeUnset()
        tree =                         tree.children()
        tree =                             tree.node('somevalue', 'scalar').end()
        tree =                             tree.node('anothervalue', 'scalar').end()
        tree =                         tree.end()
        tree =                     tree.end()
        tree =                     tree.node('level1_scalar', 'scalar').end()
        tree =                 tree.end()
        tree =             tree.end()
        tree =         tree.end()
        tree =     tree.end()
        tree =     tree.buildTree();

        a = {
            'level1': {
                'level2': {
                    'somevalue': 'foo',
                    'anothervalue': 'bar',
                },
                'level1_scalar': 'foo',
            },
        };

        b = {
            'level1': {
                'level2': False,
            },
        };

        self.assertEqual({
            'level1': {
                'level1_scalar': 'foo',
            },
        }, self._process(tree, [a, b]));


    def _process(self, tree, configs):
        assert isinstance(configs, list);
        assert isinstance(tree, NodeInterface);

        processor = Processor();

        return processor.process(tree, configs);




class MergeTest(unittest.TestCase):

    def testForbiddenOverwrite(self):
        """@expectedException Symfony\Component\Config\Definition\Exception\ForbiddenOverwriteException

        """
        try:
            tb = TreeBuilder();
            tree = tb
            tree =     tree.root('root', 'array')
            tree =         tree.children()
            tree =             tree.node('foo', 'scalar')
            tree =                 tree.cannotBeOverwritten()
            tree =             tree.end()
            tree =         tree.end()
            tree =     tree.end()
            tree =     tree.buildTree();

            a = {
                'foo': 'bar',
            };

            b = {
                'foo': 'moo',
            };

            tree.merge(a, b);
            self.fail();
        except Exception as e:
            self.assertTrue(isinstance(e, ForbiddenOverwriteException));





    def testUnsetKey(self):

        tb = TreeBuilder();
        tree = tb
        tree =     tree.root('root', 'array')
        tree =         tree.children()
        tree =             tree.node('foo', 'scalar').end()
        tree =             tree.node('bar', 'scalar').end()
        tree =             tree.node('unsettable', 'array')
        tree =                 tree.canBeUnset()
        tree =                 tree.children()
        tree =                     tree.node('foo', 'scalar').end()
        tree =                     tree.node('bar', 'scalar').end()
        tree =                 tree.end()
        tree =             tree.end()
        tree =             tree.node('unsetted', 'array')
        tree =                 tree.canBeUnset()
        tree =                 tree.prototype('scalar').end()
        tree =             tree.end()
        tree =         tree.end()
        tree =     tree.end()
        tree =     tree.buildTree();

        a = {
            'foo': 'bar',
            'unsettable': {
                'foo': 'a',
                'bar': 'b',
            },
            'unsetted': False,
        };

        b = {
            'foo': 'moo',
            'bar': 'b',
            'unsettable': False,
            'unsetted': ['a', 'b'],
        };

        self.assertEqual({
            'foo': 'moo',
            'bar': 'b',
            'unsettable': False,
            'unsetted': ['a', 'b'],
        }, tree.merge(a, b));


    def testDoesNotAllowNewKeysInSubsequentConfigs(self):
        """@expectedException Symfony\Component\Config\Definition\Exception\InvalidConfigurationException

        """

        try:
            tb = TreeBuilder();
            tree = tb
            tree =     tree.root('config', 'array')
            tree =         tree.children()
            tree =             tree.node('test', 'array')
            tree =                 tree.disallowNewKeysInSubsequentConfigs()
            tree =                 tree.useAttributeAsKey('key')
            tree =                 tree.prototype('array')
            tree =                     tree.children()
            tree =                         tree.node('value', 'scalar').end()
            tree =                     tree.end()
            tree =                 tree.end()
            tree =             tree.end()
            tree =         tree.end()
            tree =     tree.end()
            tree =     tree.buildTree();

            a = {
                'test': {
                    'a': {'value': 'foo'}
                }
            };

            b = {
                'test': {
                    'b': {'value': 'foo'}
                }
            };

            tree.merge(a, b);
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidConfigurationException));



    def testPerformsNoDeepMerging(self):

        tb = TreeBuilder();

        tree = tb
        tree =     tree.root('config', 'array')
        tree =         tree.children()
        tree =             tree.node('no_deep_merging', 'array')
        tree =                 tree.performNoDeepMerging()
        tree =                 tree.children()
        tree =                     tree.node('foo', 'scalar').end()
        tree =                     tree.node('bar', 'scalar').end()
        tree =                 tree.end()
        tree =             tree.end()
        tree =         tree.end()
        tree =     tree.end()
        tree =     tree.buildTree();

        a = {
            'no_deep_merging': {
                'foo': 'a',
                'bar': 'b',
            },
        };

        b = {
            'no_deep_merging': {
                'c': 'd',
            }
        };

        self.assertEqual({
            'no_deep_merging': {
                'c': 'd',
            }
        }, tree.merge(a, b));


    def testPrototypeWithoutAKeyAttribute(self):

        tb = TreeBuilder();

        tree = tb
        tree =     tree.root('config', 'array')
        tree =         tree.children()
        tree =             tree.arrayNode('append_elements')
        tree =                 tree.prototype('scalar').end()
        tree =             tree.end()
        tree =         tree.end()
        tree =     tree.end()
        tree =     tree.buildTree();

        a = {
            'append_elements': ['a', 'b'],
        };

        b = {
            'append_elements': ['c', 'd'],
        };

        self.assertEqual({'append_elements': {0: 'a', 1: 'b', 2: 'c', 3: 'd'}}, tree.merge(a, b));





if __name__ == '__main__':
    unittest.main();
