# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.config.definition import ConfigurationInterface;
from pymfony.component.config.definition.builder import TreeBuilder;

"""
"""


class ExampleConfiguration(ConfigurationInterface):

    def getConfigTreeBuilder(self):

        treeBuilder = TreeBuilder();
        rootNode = treeBuilder.root('root');

        n = rootNode;
        n =    n.children();
        n =    n.booleanNode('boolean').defaultTrue().end();
        n =    n.scalarNode('scalar_empty').end();
        n =    n.scalarNode('scalar_null').defaultNull().end();
        n =    n.scalarNode('scalar_true').defaultTrue().end();
        n =    n.scalarNode('scalar_false').defaultFalse().end();
        n =    n.scalarNode('scalar_default').defaultValue('default').end();
        n =    n.scalarNode('scalar_array_empty').defaultValue([]).end();
        n =    n.scalarNode('scalar_array_defaults').defaultValue(['elem1', 'elem2']).end();
        n =    n.arrayNode('array');
        n =        n.info('some info');
        n =        n.canBeUnset();
        n =        n.children();
        n =            n.scalarNode('child1').end();
        n =            n.scalarNode('child2').end();
        n =            n.scalarNode('child3');
        n =                n.info(
                                "this is a long\n"
                                "multi-line info text\n"
                                "which should be indented"
                            );
        n =                n.example('example setting');
        n =            n.end();
        n =        n.end();
        n =    n.end();
        n =    n.arrayNode('array_prototype');
        n =        n.children();
        n =            n.arrayNode('parameters');
        n =                n.useAttributeAsKey('name');
        n =                n.prototype('array');
        n =                    n.children();
        n =                        n.scalarNode('value').isRequired().end();
        n =                    n.end();
        n =                n.end();
        n =            n.end();
        n =        n.end();
        n =    n.end();
        n = n.end();


        return treeBuilder;
