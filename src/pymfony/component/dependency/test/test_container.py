# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.system.exception import LogicException;
from pymfony.component.system.exception import StandardException;
from pymfony.component.system.exception import RuntimeException;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system import Object;

from pymfony.component.dependency import Container;
from pymfony.component.dependency import Scope;
from pymfony.component.dependency.parameterbag import ParameterBag;
from pymfony.component.dependency.parameterbag import FrozenParameterBag;
from pymfony.component.dependency.interface import ContainerInterface;
from pymfony.component.dependency.exception import ServiceCircularReferenceException;
from pymfony.component.dependency.exception import ServiceNotFoundException;

"""
"""


class ContainerTest(unittest.TestCase):

    def testConstructor(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.__construct

        """

        sc = Container();
        self.assertEqual(sc, sc.get('service_container'), '__init__() automatically registers itself as a service');

        sc = Container(ParameterBag({'foo': 'bar'}));
        self.assertEqual({'foo': 'bar'}, sc.getParameterBag().all(), '__init__() takes an array of parameters as its first argument');


    def testCompile(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.compile

        """

        sc = Container(ParameterBag({'foo': 'bar'}));
        sc.compile();
        self.assertTrue(isinstance(sc.getParameterBag(), FrozenParameterBag), '->compile() changes the parameter bag to a FrozenParameterBag instance');
        self.assertEqual({'foo': 'bar'}, sc.getParameterBag().all(), '->compile() copies the current parameters to the new parameter bag');


    def testIsFrozen(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.isFrozen

        """

        sc = Container(ParameterBag({'foo': 'bar'}));
        self.assertFalse(sc.isFrozen(), '->isFrozen() returns False if the parameters are not frozen');
        sc.compile();
        self.assertTrue(sc.isFrozen(), '->isFrozen() returns True if the parameters are frozen');


    def testGetParameterBag(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.getParameterBag

        """

        sc = Container();
        self.assertEqual({}, sc.getParameterBag().all(), '->getParameterBag() returns an empty array if no parameter has been defined');


    def testGetSetParameter(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.setParameter
        @covers Symfony\Component\DependencyInjection\Container.getParameter

        """

        sc = Container(ParameterBag({'foo': 'bar'}));
        sc.setParameter('bar', 'foo');
        self.assertEqual('foo', sc.getParameter('bar'), '->setParameter() sets the value of a new parameter');

        sc.setParameter('foo', 'baz');
        self.assertEqual('baz', sc.getParameter('foo'), '->setParameter() overrides previously set parameter');

        sc.setParameter('Foo', 'baz1');
        self.assertEqual('baz1', sc.getParameter('foo'), '->setParameter() converts the key to lowercase');
        self.assertEqual('baz1', sc.getParameter('FOO'), '->getParameter() converts the key to lowercase');

        try:
            sc.getParameter('baba');
            self.fail('->getParameter() thrown an InvalidArgumentException if the key does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->getParameter() thrown an InvalidArgumentException if the key does not exist');
            self.assertEqual('You have requested a non-existent parameter "baba".', e.getMessage(), '->getParameter() thrown an InvalidArgumentException if the key does not exist');



    def testGetServiceIds(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.getServiceIds

        """

        sc = Container();
        sc.set('foo', Object());
        sc.set('bar', Object());
        self.assertTrue('service_container' in sc.getServiceIds(), '->getServiceIds() returns all defined service ids');
        self.assertTrue('foo' in sc.getServiceIds(), '->getServiceIds() returns all defined service ids');
        self.assertTrue('bar' in sc.getServiceIds(), '->getServiceIds() returns all defined service ids');

        sc = ProjectServiceContainer();
        ids = sc.getServiceIds();
        message = '->getServiceIds() returns defined service ids by getXXXService() methods';
        self.assertTrue('scoped' in ids, message);
        self.assertTrue('scoped_foo' in ids, message);
        self.assertTrue('bar' in ids, message);
        self.assertTrue('foo_bar' in ids, message);
        self.assertTrue('foo_baz' in ids, message);
        self.assertTrue('circular' in ids, message);
        self.assertTrue('throw_exception' in ids, message);
        self.assertTrue('throws_exception_on_service_configuration' in ids, message);
        self.assertTrue('service_container' in ids, message);


    def testSet(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.set

        """

        sc = Container();
        foo = Object();
        sc.set('foo', foo);
        self.assertEqual(foo, sc.get('foo'), '->set() sets a service');


    def testSetDoesNotAllowPrototypeScope(self):
        """
        @expectedException InvalidArgumentException

        """

        try:
            c = Container();
            c.set('foo', Object(), 'prototype');

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));


    def testSetDoesNotAllowInactiveScope(self):
        """
        @expectedException RuntimeException

        """

        try:
            c = Container();
            c.addScope(Scope('foo'));
            c.set('foo', Object(), 'foo');

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, RuntimeException));


    def testSetAlsoSetsScopedService(self):

        c = Container();
        c.addScope(Scope('foo'));
        c.enterScope('foo');
        foo = Object();
        c.set('foo', foo, 'foo');

        services = self._getField(c, '_scopedServices');
        self.assertTrue('foo' in services['foo']);
        self.assertEqual(foo, services['foo']['foo']);


    def testGet(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.get

        """

        sc = ProjectServiceContainer();
        foo = Object();
        sc.set('foo', foo);
        self.assertEqual(foo, sc.get('foo'), '->get() returns the service for the given id');
        self.assertEqual(sc.bar, sc.get('bar'), '->get() returns the service for the given id');
        self.assertEqual(sc.foo_bar, sc.get('foo_bar'), '->get() returns the service if a get*Method() is defined');
        self.assertEqual(sc.foo_baz, sc.get('foo.baz'), '->get() returns the service if a get*Method() is defined');

        bar = Object();
        sc.set('bar', bar);
        self.assertEqual(bar, sc.get('bar'), '->get() prefers to return a service defined with set() than one defined with a getXXXMethod()');

        try:
            sc.get('');
            self.fail('->get() raise a InvalidArgumentException exception if the service is empty');
        except Exception as e:
            self.assertTrue(isinstance(e, ServiceNotFoundException), '->get() raise a ServiceNotFoundException exception if the service is empty');

        self.assertTrue(None is sc.get('', ContainerInterface.NULL_ON_INVALID_REFERENCE));


    def testGetCircularReference(self):


        sc = ProjectServiceContainer();
        try:
            sc.get('circular');
            self.fail('->get() raise a ServiceCircularReferenceException if it contains circular reference');
        except Exception as e:
            self.assertTrue(isinstance(e, ServiceCircularReferenceException), '->get() raise a ServiceCircularReferenceException if it contains circular reference');
            self.assertTrue(e.getMessage().startswith('Circular reference detected for service "circular"'), '->get() raise a LogicException if it contains circular reference');



    def testHas(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.has

        """

        sc = ProjectServiceContainer();
        sc.set('foo', Object());
        self.assertFalse(sc.has('foo1'), '->has() returns False if the service does not exist');
        self.assertTrue(sc.has('foo'), '->has() returns True if the service exists');
        self.assertTrue(sc.has('bar'), '->has() returns True if a get*Method() is defined');
        self.assertTrue(sc.has('foo_bar'), '->has() returns True if a get*Method() is defined');
        self.assertTrue(sc.has('foo.baz'), '->has() returns True if a get*Method() is defined');


    def testInitialized(self):
        """
        @covers Symfony\Component\DependencyInjection\Container.initialized

        """

        sc = ProjectServiceContainer();
        sc.set('foo', Object());
        self.assertTrue(sc.initialized('foo'), '->initialized() returns True if service is loaded');
        self.assertFalse(sc.initialized('foo1'), '->initialized() returns False if service is not loaded');
        self.assertFalse(sc.initialized('bar'), '->initialized() returns False if a service is defined, but not currently loaded');


    def testEnterLeaveCurrentScope(self):

        container = ProjectServiceContainer();
        container.addScope(Scope('foo'));

        container.enterScope('foo');
        scoped1 = container.get('scoped');
        scopedFoo1 = container.get('scoped_foo');

        container.enterScope('foo');
        scoped2 = container.get('scoped');
        scoped3 = container.get('scoped');
        scopedFoo2 = container.get('scoped_foo');

        container.leaveScope('foo');
        scoped4 = container.get('scoped');
        scopedFoo3 = container.get('scoped_foo');

        self.assertNotEqual(scoped1, scoped2);
        self.assertEqual(scoped2, scoped3);
        self.assertEqual(scoped1, scoped4);
        self.assertNotEqual(scopedFoo1, scopedFoo2);
        self.assertEqual(scopedFoo1, scopedFoo3);


    def testEnterLeaveScopeWithChildScopes(self):

        container = Container();
        container.addScope(Scope('foo'));
        container.addScope(Scope('bar', 'foo'));

        self.assertFalse(container.isScopeActive('foo'));

        container.enterScope('foo');
        container.enterScope('bar');

        self.assertTrue(container.isScopeActive('foo'));
        self.assertFalse(container.has('a'));

        a = Object();
        container.set('a', a, 'bar');

        services = self._getField(container, '_scopedServices');
        self.assertTrue('a' in services['bar']);
        self.assertEqual(a, services['bar']['a']);

        self.assertTrue(container.has('a'));
        container.leaveScope('foo');

        services = self._getField(container, '_scopedServices');
        self.assertFalse('bar' in services);

        self.assertFalse(container.isScopeActive('foo'));
        self.assertFalse(container.has('a'));


    def testEnterScopeRecursivelyWithInactiveChildScopes(self):

        container = Container();
        container.addScope(Scope('foo'));
        container.addScope(Scope('bar', 'foo'));

        self.assertFalse(container.isScopeActive('foo'));

        container.enterScope('foo');

        self.assertTrue(container.isScopeActive('foo'));
        self.assertFalse(container.isScopeActive('bar'));
        self.assertFalse(container.has('a'));

        a = Object();
        container.set('a', a, 'foo');

        services = self._getField(container, '_scopedServices');
        self.assertTrue('a' in services['foo']);
        self.assertEqual(a, services['foo']['a']);

        self.assertTrue(container.has('a'));
        container.enterScope('foo');

        services = self._getField(container, '_scopedServices');
        self.assertFalse('a' in services);

        self.assertTrue(container.isScopeActive('foo'));
        self.assertFalse(container.isScopeActive('bar'));
        self.assertFalse(container.has('a'));


    def testLeaveScopeNotActive(self):

        container = Container();
        container.addScope(Scope('foo'));

        try:
            container.leaveScope('foo');
            self.fail('->leaveScope() raise a LogicException if the scope is not active yet');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->leaveScope() raise a LogicException if the scope is not active yet');
            self.assertEqual('The scope "foo" is not active.', e.getMessage(), '->leaveScope() raise a LogicException if the scope is not active yet');


        try:
            container.leaveScope('bar');
            self.fail('->leaveScope() raise a LogicException if the scope does not exist');
        except Exception as e:
            self.assertTrue(isinstance(e, LogicException), '->leaveScope() raise a LogicException if the scope does not exist');
            self.assertEqual('The scope "bar" is not active.', e.getMessage(), '->leaveScope() raise a LogicException if the scope does not exist');



    def testAddScopeDoesNotAllowBuiltInScopes(self):
        """
        @expectedException InvalidArgumentException
        @dataProvider getBuiltInScopes

        """

        def test(scope):
            try:
                container = Container();
                container.addScope(Scope(scope));

                self.fail()
            except Exception as e:
                self.assertTrue(isinstance(e, InvalidArgumentException));


        for data in self.getBuiltInScopes():
            test(*data);




    def testAddScopeDoesNotAllowExistingScope(self):
        """
        @expectedException InvalidArgumentException

        """

        try:
            container = Container();
            container.addScope(Scope('foo'));
            container.addScope(Scope('foo'));

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));





    def testAddScopeDoesNotAllowInvalidParentScope(self):
        """
        @expectedException InvalidArgumentException
        @dataProvider getInvalidParentScopes

        """

        def test(scope):
            try:
                c = Container();
                c.addScope(Scope('foo', scope));

                self.fail()
            except Exception as e:
                self.assertTrue(isinstance(e, InvalidArgumentException));


        for data in self.getInvalidParentScopes():
            test(*data);



    def testAddScope(self):

        c = Container();
        c.addScope(Scope('foo'));
        c.addScope(Scope('bar', 'foo'));

        self.assertEqual({'foo': 'container', 'bar': 'foo'}, self._getField(c, '_scopes'));
        self.assertEqual({'foo': ['bar'], 'bar': []}, self._getField(c, '_scopeChildren'));


    def testHasScope(self):

        c = Container();

        self.assertFalse(c.hasScope('foo'));
        c.addScope(Scope('foo'));
        self.assertTrue(c.hasScope('foo'));


    def testIsScopeActive(self):

        c = Container();

        self.assertFalse(c.isScopeActive('foo'));
        c.addScope(Scope('foo'));

        self.assertFalse(c.isScopeActive('foo'));
        c.enterScope('foo');

        self.assertTrue(c.isScopeActive('foo'));
        c.leaveScope('foo');

        self.assertFalse(c.isScopeActive('foo'));


    def testGetThrowsException(self):

        c = ProjectServiceContainer();

        try:
            c.get('throw_exception');
            self.fail();
        except StandardException as e:
            self.assertEqual('Something went terribly wrong!', e.getMessage());


        try:
            c.get('throw_exception');
            self.fail();
        except StandardException as e:
            self.assertEqual('Something went terribly wrong!', e.getMessage());


    def testGetThrowsExceptionOnServiceConfiguration(self):

        c = ProjectServiceContainer();

        try:
            c.get('throws_exception_on_service_configuration');
            self.fail('The container can not contain invalid service!');
        except StandardException as e:
            self.assertEqual('Something was terribly wrong while trying to configure the service!', e.getMessage());

        self.assertFalse(c.initialized('throws_exception_on_service_configuration'));

        try:
            c.get('throws_exception_on_service_configuration');
            self.fail('The container can not contain invalid service!');
        except StandardException as e:
            self.assertEqual('Something was terribly wrong while trying to configure the service!', e.getMessage());

        self.assertFalse(c.initialized('throws_exception_on_service_configuration'));


    def getInvalidParentScopes(self):

        return [
            [ContainerInterface.SCOPE_PROTOTYPE],
            ['bar'],
        ];


    def getBuiltInScopes(self):

        return [
            [ContainerInterface.SCOPE_CONTAINER],
            [ContainerInterface.SCOPE_PROTOTYPE],
        ];


    def _getField(self, obj, field):

        if field.startswith('__'):
            field = '_' + type(obj).__name__ + field;

        return getattr(obj, field);



class ProjectServiceContainer(Container):

    def __init__(self):

        Container.__init__(self);

        self.bar = Object();
        self.foo_bar = Object();
        self.foo_baz = Object();


    def getScopedService(self):

        if 'foo' not in self._scopedServices :
            raise RuntimeException('Invalid call');

        self._services['scoped'] = self._scopedServices['foo']['scoped'] = Object();

        return self._services['scoped'];


    def getScopedFooService(self):

        if 'foo' not in self._scopedServices :
            raise RuntimeException('Invalid call');


        self._services['scoped_foo'] = self._scopedServices['foo']['scoped_foo'] = Object();
        return self._services['scoped_foo'];


    def getBarService(self):

        return self.bar;


    def getFooBarService(self):

        return self.foo_bar;


    def getFoo_BazService(self):

        return self.foo_baz;


    def getCircularService(self):

        return self.get('circular');


    def getThrowExceptionService(self):

        raise StandardException('Something went terribly wrong!');


    def getThrowsExceptionOnServiceConfigurationService(self):

        self._services['throws_exception_on_service_configuration'] = instance = Object();

        raise StandardException('Something was terribly wrong while trying to configure the service!');


if __name__ == '__main__':
    unittest.main();
