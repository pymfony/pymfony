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

import unittest

from pymfony.component.system.tool import OrderedDict
from pymfony.component.dependency import ContainerBuilder
from pymfony.component.dependency import Reference
from pymfony.component.dependency import Definition
from pymfony.component.dependency.compiler import RepeatedPass
from pymfony.component.dependency.compilerpass import AnalyzeServiceReferencesPass
from pymfony.component.dependency.exception import RuntimeException
from pymfony.component.dependency.compiler import Compiler
from pymfony.component.dependency.compilerpass import CheckCircularReferencesPass
from pymfony.component.dependency import ContainerInterface
from pymfony.component.dependency.compilerpass import CheckDefinitionValidityPass
from pymfony.component.dependency.exception import ServiceNotFoundException
from pymfony.component.dependency.compilerpass import CheckExceptionOnInvalidReferenceBehaviorPass
from pymfony.component.dependency.compilerpass import CheckReferenceValidityPass
from pymfony.component.dependency.compilerpass import RemoveUnusedDefinitionsPass
from pymfony.component.dependency.exception import InvalidArgumentException
from pymfony.component.dependency.compilerpass import ReplaceAliasByActualDefinitionPass
from pymfony.component.dependency.definition import DefinitionDecorator
from pymfony.component.dependency.compilerpass import ResolveDefinitionTemplatesPass
from pymfony.component.dependency.compilerpass import ResolveInvalidReferencesPass
from pymfony.component.dependency.compilerpass import ResolveReferencesToAliasesPass
from pymfony.component.dependency import Scope

class AnalyzeServiceReferencesPassTest(unittest.TestCase):

    def testProcess(self):

        container = ContainerBuilder();
        container._ContainerBuilder__definitions = OrderedDict();
        ref1 = Reference('b');
        a = container.register('a').addArgument(ref1);

        ref2 = Reference('a');
        b = container.register('b').addMethodCall('setA', [ref2]);


        ref3 = Reference('a');
        ref4 = Reference('b');
        c = container.register('c').addArgument(ref3).addArgument(ref4);

        ref5 = Reference('b');
        d = container.register('d').setProperty('foo', ref5);

        ref6 = Reference('b');
        e = container.register('e').setConfigurator([ref6, 'methodName']);

        graph = self._process(container);

        edges = graph.getNode('b').getInEdges();
        self.assertEqual(4, len(edges));
        # FIXME: order
        self.assertEqual(ref1, edges[0].getValue());
        self.assertEqual(ref4, edges[1].getValue());
        self.assertEqual(ref5, edges[2].getValue());
        self.assertEqual(ref6, edges[3].getValue());


    def testProcessDetectsReferencesFromInlinedDefinitions(self):

        container = ContainerBuilder();

        container.register('a');

        ref = Reference('a');
        container.register('b').addArgument(Definition(None, [ref]));

        graph = self._process(container);

        refs = graph.getNode('a').getInEdges();
        self.assertEqual(1, len(refs));
        self.assertEqual(ref, refs[0].getValue());


    def testProcessDoesNotSaveDuplicateReferences(self):

        container = ContainerBuilder();

        container.register('a');

        ref1 = Reference('a');
        ref2 = Reference('a');
        container.register('b').addArgument(Definition(None, [ref1]))\
            .addArgument(Definition(None, [ref2]));

        graph = self._process(container);

        self.assertEqual(2, len(graph.getNode('a').getInEdges()));


    def _process(self, container):
        assert isinstance(container, ContainerBuilder);

        cPass = RepeatedPass([AnalyzeServiceReferencesPass()]);
        cPass.process(container);

        return container.getCompiler().getServiceReferenceGraph();




class CheckCircularReferencesPassTest(unittest.TestCase):

    def testProcess(self):
        """@expectedException RuntimeException

        """

        try:
            container = ContainerBuilder();
            container.register('a').addArgument(Reference('b'));
            container.register('b').addArgument(Reference('a'));

            self._process(container);
            self.fail("")
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));



    def testProcessWithAliases(self):
        """@expectedException RuntimeException

        """

        try:
            container = ContainerBuilder();
            container.register('a').addArgument(Reference('b'));
            container.setAlias('b', 'c');
            container.setAlias('c', 'a');

            self._process(container);
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));


    def testProcessDetectsIndirectCircularReference(self):
        """@expectedException RuntimeException

        """

        try:
            container = ContainerBuilder();
            container.register('a').addArgument(Reference('b'));
            container.register('b').addArgument(Reference('c'));
            container.register('c').addArgument(Reference('a'));

            self._process(container);
            self.fail("")
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));


    def testProcessIgnoresMethodCalls(self):

        container = ContainerBuilder();
        container.register('a').addArgument(Reference('b'));
        container.register('b').addMethodCall('setA', [Reference('a')]);

        self._process(container);


    def _process(self, container):
        assert isinstance(container, ContainerBuilder);

        compiler = Compiler();
        passConfig = compiler.getPassConfig();
        passConfig.setOptimizationPasses([
            AnalyzeServiceReferencesPass(True),
            CheckCircularReferencesPass(),
        ]);
        passConfig.setRemovingPasses([]);

        compiler.compile(container);


class CheckDefinitionValidityPassTest(unittest.TestCase):

    def testProcessDetectsSyntheticNonPublicDefinitions(self):
        """@expectedException RuntimeException

        """

        try:
            container = ContainerBuilder();
            container.register('a').setSynthetic(True).setPublic(False);

            self._process(container);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));




    def testProcessDetectsSyntheticPrototypeDefinitions(self):
        """@expectedException RuntimeException

        """

        try:
            container = ContainerBuilder();
            container.register('a').setSynthetic(True).setScope(ContainerInterface.SCOPE_PROTOTYPE);

            self._process(container);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));




    def testProcessDetectsNonSyntheticNonAbstractDefinitionWithoutClass(self):
        """@expectedException RuntimeException

        """

        try:
            container = ContainerBuilder();
            container.register('a').setSynthetic(False).setAbstract(False);

            self._process(container);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));


    def testProcess(self):

        container = ContainerBuilder();
        container.register('a', 'class');
        container.register('b', 'class').setSynthetic(True).setPublic(True);
        container.register('c', 'class').setAbstract(True);
        container.register('d', 'class').setSynthetic(True);

        self._process(container);


    def _process(self, container):
        assert isinstance(container, ContainerBuilder);

        cPass = CheckDefinitionValidityPass();
        cPass.process(container);



class CheckExceptionOnInvalidReferenceBehaviorPassTest(unittest.TestCase):

    def testProcess(self):

        container = ContainerBuilder();

        container.register('a', 'object').addArgument(Reference('b'));
        container.register('b', 'object');


    def testProcessThrowsExceptionOnInvalidReference(self):
        """@expectedException Symfony\Component\DependencyInjection\Exception\ServiceNotFoundException

        """

        try:
            container = ContainerBuilder();

            container.register('a', 'object').addArgument(Reference('b'));

            self.__process(container);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ServiceNotFoundException));




    def testProcessThrowsExceptionOnInvalidReferenceFromInlinedDefinition(self):
        """@expectedException Symfony\Component\DependencyInjection\Exception\ServiceNotFoundException

        """

        try:
            container = ContainerBuilder();

            definition = Definition();
            definition.addArgument(Reference('b'));

            container.register('a', 'object').addArgument(definition);

            self.__process(container);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ServiceNotFoundException));


    def __process(self, container):
        assert isinstance(container, ContainerBuilder);

        cPass = CheckExceptionOnInvalidReferenceBehaviorPass();
        cPass.process(container);


class CheckReferenceValidityPassTest(unittest.TestCase):

    def testProcessIgnoresScopeWideningIfNonStrictReference(self):

        container = ContainerBuilder();
        container.register('a').addArgument(Reference('b', ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE, False));
        container.register('b').setScope('prototype');

        self._process(container);


    def testProcessDetectsScopeWidening(self):
        """@expectedException RuntimeException

        """

        try:
            container = ContainerBuilder();
            container.register('a').addArgument(Reference('b'));
            container.register('b').setScope('prototype');

            self._process(container);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));


    def testProcessIgnoresCrossScopeHierarchyReferenceIfNotStrict(self):

        container = ContainerBuilder();
        container.addScope(Scope('a'));
        container.addScope(Scope('b'));

        container.register('a').setScope('a').addArgument(Reference('b', ContainerInterface.EXCEPTION_ON_INVALID_REFERENCE, False));
        container.register('b').setScope('b');

        self._process(container);


    def testProcessDetectsCrossScopeHierarchyReference(self):
        """@expectedException RuntimeException

        """
        try:

            container = ContainerBuilder();
            container.addScope(Scope('a'));
            container.addScope(Scope('b'));
    
            container.register('a').setScope('a').addArgument(Reference('b'));
            container.register('b').setScope('b');
    
            self._process(container);
        
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));
        


    def testProcessDetectsReferenceToAbstractDefinition(self):
        """@expectedException RuntimeException

        """

        try:

            container = ContainerBuilder();

            container.register('a').setAbstract(True);
            container.register('b').addArgument(Reference('a'));

            self._process(container);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));


    def testProcess(self):

        container = ContainerBuilder();
        container.register('a').addArgument(Reference('b'));
        container.register('b');

        self._process(container);


    def _process(self, container):
        assert isinstance(container, ContainerBuilder);

        cPass = CheckReferenceValidityPass();
        cPass.process(container);



class RemoveUnusedDefinitionsPassTest(unittest.TestCase):

    def testProcess(self):

        container = ContainerBuilder();
        container.register('foo').setPublic(False);
        container.register('bar').setPublic(False);
        container.register('moo').setArguments([Reference('bar')]);

        self._process(container);

        self.assertFalse(container.hasDefinition('foo'));
        self.assertTrue(container.hasDefinition('bar'));
        self.assertTrue(container.hasDefinition('moo'));


    def testProcessRemovesUnusedDefinitionsRecursively(self):

        container = ContainerBuilder();
        container.register('foo').setPublic(False);
        container.register('bar').setArguments([Reference('foo')])\
            .setPublic(False);

        self._process(container);

        self.assertFalse(container.hasDefinition('foo'));
        self.assertFalse(container.hasDefinition('bar'));


    def testProcessWorksWithInlinedDefinitions(self):

        container = ContainerBuilder();
        container\
            .register('foo')\
            .setPublic(False)\
        ;
        container\
            .register('bar')\
            .setArguments([Definition(None, [Reference('foo')])])\
        ;

        self._process(container);

        self.assertTrue(container.hasDefinition('foo'));
        self.assertTrue(container.hasDefinition('bar'));


    def _process(self, container):
        assert isinstance(container, ContainerBuilder);

        repeatedPass = RepeatedPass([
            AnalyzeServiceReferencesPass(),
            RemoveUnusedDefinitionsPass()
        ]);
        repeatedPass.process(container);



class ReplaceAliasByActualDefinitionPassTest(unittest.TestCase):

    def testProcess(self):

        container = ContainerBuilder();

        container.register('a', 'object');

        bDefinition = Definition('object');
        bDefinition.setPublic(False);
        container.setDefinition('b', bDefinition);

        container.setAlias('a_alias', 'a');
        container.setAlias('b_alias', 'b');

        self._process(container);

        self.assertTrue(container.has('a'), '->process() does nothing to public definitions.');
        self.assertTrue(container.hasAlias('a_alias'));
        self.assertFalse(container.has('b'), '->process() removes non-public definitions.');
        self.assertTrue(
            container.has('b_alias') and not container.hasAlias('b_alias'),
            '->process() replaces alias to actual.'
        );


    def testProcessWithInvalidAlias(self):
        """@expectedException InvalidArgumentException

        """

        try:
            container = ContainerBuilder();
            container.setAlias('a_alias', 'a');
            self._process(container);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));




    def _process(self, container):
        assert isinstance(container, ContainerBuilder);

        cPass = ReplaceAliasByActualDefinitionPass();
        cPass.process(container);


class ResolveDefinitionTemplatesPassTest(unittest.TestCase):

    def testProcess(self):

        container = ContainerBuilder();
        container.register('parent', 'foo').setArguments(['moo', 'b']).setProperty('foo', 'moo');
        container.setDefinition('child', DefinitionDecorator('parent'))\
            .replaceArgument(0, 'a')\
            .setProperty('foo', 'bar')\
            .setClass('bar')\
        ;

        self._process(container);

        definition = container.getDefinition('child');
        self.assertFalse(isinstance(object, DefinitionDecorator));
        self.assertEqual('bar', definition.getClass());
        self.assertEqual(['a', 'b'], definition.getArguments());
        self.assertEqual({'foo': 'bar'}, definition.getProperties());


    def testProcessAppendsMethodCallsAlways(self):

        container = ContainerBuilder();

        container\
            .register('parent')\
            .addMethodCall('foo', ['bar'])\
        ;

        container\
            .setDefinition('child', DefinitionDecorator('parent'))\
            .addMethodCall('bar', ['foo'])\
        ;

        self._process(container);

        definition = container.getDefinition('child');
        self.assertEqual([
            ['foo', ['bar']],
            ['bar', ['foo']],
            ], definition.getMethodCalls()
        );


    def testProcessDoesNotCopyAbstract(self):

        container = ContainerBuilder();

        container\
            .register('parent')\
            .setAbstract(True)\
        ;

        container\
            .setDefinition('child', DefinitionDecorator('parent'))\
        ;

        self._process(container);

        defi = container.getDefinition('child');
        self.assertFalse(defi.isAbstract());


    def testProcessDoesNotCopyScope(self):

        container = ContainerBuilder();

        container\
            .register('parent')\
            .setScope('foo')\
        ;

        container\
            .setDefinition('child', DefinitionDecorator('parent'))\
        ;

        self._process(container);

        defi = container.getDefinition('child');
        self.assertEqual(ContainerInterface.SCOPE_CONTAINER, defi.getScope());


    def testProcessDoesNotCopyTags(self):

        container = ContainerBuilder();

        container\
            .register('parent')\
            .addTag('foo')\
        ;

        container\
            .setDefinition('child', DefinitionDecorator('parent'))\
        ;

        self._process(container);

        defi = container.getDefinition('child');
        self.assertEqual({}, defi.getTags());


    def testProcessHandlesMultipleInheritance(self):

        container = ContainerBuilder();

        container\
            .register('parent', 'foo')\
            .setArguments(['foo', 'bar', 'c'])\
        ;

        container\
            .setDefinition('child2', DefinitionDecorator('child1'))\
            .replaceArgument(1, 'b')\
        ;

        container\
            .setDefinition('child1', DefinitionDecorator('parent'))\
            .replaceArgument(0, 'a')\
        ;

        self._process(container);

        defi = container.getDefinition('child2');
        self.assertEqual(['a', 'b', 'c'], defi.getArguments());
        self.assertEqual('foo', defi.getClass());


    def _process(self, container):
        assert isinstance(container, ContainerBuilder);

        cPass = ResolveDefinitionTemplatesPass();
        cPass.process(container);


class ResolveInvalidReferencesPassTest(unittest.TestCase):

    def testProcess(self):

        container = ContainerBuilder();
        defi = container\
            .register('foo')\
            .setArguments([Reference('bar', ContainerInterface.NULL_ON_INVALID_REFERENCE)])\
            .addMethodCall('foo', [Reference('moo', ContainerInterface.IGNORE_ON_INVALID_REFERENCE)])\
        ;

        self._process(container);

        arguments = defi.getArguments();
        self.assertTrue(arguments[0] is None);
        self.assertEqual(0, len(defi.getMethodCalls()));


    def testProcessIgnoreNonExistentServices(self):

        container = ContainerBuilder();
        defi = container\
            .register('foo')\
            .setArguments([Reference('bar')])\
        ;

        self._process(container);

        arguments = defi.getArguments();
        self.assertEqual('bar', str(arguments[0]));


    def testProcessRemovesPropertiesOnInvalid(self):

        container = ContainerBuilder();
        defi = container\
            .register('foo')\
            .setProperty('foo', Reference('bar', ContainerInterface.IGNORE_ON_INVALID_REFERENCE))\
        ;

        self._process(container);

        self.assertEqual(dict(), defi.getProperties());


    def testStrictFlagIsPreserved(self):

        container = ContainerBuilder();
        container.register('bar');
        defi = container\
            .register('foo')\
            .addArgument(Reference('bar', ContainerInterface.NULL_ON_INVALID_REFERENCE, False))\
        ;

        self._process(container);

        self.assertFalse(defi.getArgument(0).isStrict());


    def _process(self, container):
        assert isinstance(container, ContainerBuilder);

        cPass = ResolveInvalidReferencesPass();
        cPass.process(container);


class ResolveReferencesToAliasesPassTest(unittest.TestCase):

    def testProcess(self):

        container = ContainerBuilder();
        container.setAlias('bar', 'foo');
        defi = container\
            .register('moo')\
            .setArguments([Reference('bar')])\
        ;

        self._process(container);

        arguments = defi.getArguments();
        self.assertEqual('foo', str(arguments[0]));


    def testProcessRecursively(self):

        container = ContainerBuilder();
        container.setAlias('bar', 'foo');
        container.setAlias('moo', 'bar');
        defi = container\
            .register('foobar')\
            .setArguments([Reference('moo')])\
        ;

        self._process(container);

        arguments = defi.getArguments();
        self.assertEqual('foo', str(arguments[0]));


    def _process(self, container):
        assert isinstance(container, ContainerBuilder);

        cPass = ResolveReferencesToAliasesPass();
        cPass.process(container);


if __name__ == '__main__':
    unittest.main();
