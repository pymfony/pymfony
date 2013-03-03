# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest

from pymfony.component.console_kernel.controller import ControllerResolver
from pymfony.component.system.exception import InvalidArgumentException
from pymfony.component.system.exception import RuntimeException
from pymfony.component.system import Object

try:
    from pymfony.component.console import Request
except ImportError:
    SKIP_TEST = True;
else:
    SKIP_TEST = False;

"""
"""

class ControllerResolverTest(unittest.TestCase):

    def setUp(self):
        module = __package__ + '.' if __package__ else '' + __name__;

        self._className = module + '.' + self.__class__.__name__;
        self._controller = TestController();
        self._controllerClassName = module + '.' + self._controller.__class__.__name__;
        self._controllerFunctionName = module + '.' + 'some_controller_function';

    def testGetController(self):
        if SKIP_TEST:
            return;

        resolver = ControllerResolver();

        request = Request.create(['script']);
        self.assertFalse(resolver.getController(request), '->getController() returns False when the request has no _controller attribute');

        request.attributes.set('_controller', self._controllerClassName + '::_controllerMethod1');
        controller = resolver.getController(request);
        self.assertEqual(controller.__name__, '_controllerMethod1', '->getController() returns a PHP callable');

        def lbda():
            pass;
        request.attributes.set('_controller', lbda);
        controller = resolver.getController(request);
        self.assertEqual(lbda, controller);

        request.attributes.set('_controller', self._controller);
        controller = resolver.getController(request);
        self.assertEqual(self._controller, controller);

        request.attributes.set('_controller', self._controllerClassName);
        controller = resolver.getController(request);
        self.assertTrue(isinstance(controller, self._controller.__class__));

        request.attributes.set('_controller', self._controller._controllerMethod1);
        controller = resolver.getController(request);
        self.assertEqual(self._controller._controllerMethod1, controller);

        request.attributes.set('_controller', some_controller_function);
        controller = resolver.getController(request);
        self.assertEqual(some_controller_function, controller);

        request.attributes.set('_controller', 'foo');
        try:
            resolver.getController(request);
            self.fail('->getController() raise an InvalidArgumentException if the _controller attribute is not well-formatted');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->getController() raise an InvalidArgumentException if the _controller attribute is not well-formatted');


        request.attributes.set('_controller', 'foo.bar');
        try:
            resolver.getController(request);
            self.fail('->getController() raise an InvalidArgumentException if the _controller attribute contains a non-existent class');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->getController() raise an InvalidArgumentException if the _controller attribute contains a non-existent class');


        request.attributes.set('_controller', self._controllerClassName + '::bar');
        try:
            resolver.getController(request);
            self.fail('->getController() raise an InvalidArgumentException if the _controller attribute contains a non-existent method');
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException), '->getController() raise an InvalidArgumentException if the _controller attribute contains a non-existent method');



    def testGetArguments(self):
        if SKIP_TEST:
            return;

        resolver = ControllerResolver();

        request = Request.create(['script']);
        controller = self.testGetArguments;
        self.assertEqual([], resolver.getArguments(request, controller), '->getArguments() returns an empty array if the method takes no arguments');

        request = Request.create(['script']);
        request.attributes.set('foo', 'foo');
        controller = self._controller._controllerMethod1;
        self.assertEqual(['foo'], resolver.getArguments(request, controller), '->getArguments() returns an array of arguments for the controller method');

        request = Request.create(['script']);
        request.attributes.set('foo', 'foo');
        controller = self._controller._controllerMethod2;
        self.assertEqual(['foo', None], resolver.getArguments(request, controller), '->getArguments() uses default values if present');

        request.attributes.set('bar', 'bar');
        self.assertEqual(['foo', 'bar'], resolver.getArguments(request, controller), '->getArguments() overrides default values if provided in the request attributes');

        request = Request.create(['script']);
        request.attributes.set('foo', 'foo');
        controller = lambda foo: None;
        self.assertEqual(['foo'], resolver.getArguments(request, controller));

        request = Request.create(['script']);
        request.attributes.set('foo', 'foo');
        controller = lambda foo, bar = 'bar': None;
        self.assertEqual(['foo', 'bar'], resolver.getArguments(request, controller));

        request = Request.create(['script']);
        request.attributes.set('foo', 'foo');
        controller = self._controller;
        self.assertEqual(['foo', None], resolver.getArguments(request, controller));
        request.attributes.set('bar', 'bar');
        self.assertEqual(['foo', 'bar'], resolver.getArguments(request, controller));

        request = Request.create(['script']);
        request.attributes.set('foo', 'foo');
        request.attributes.set('foobar', 'foobar');
        controller = self._controllerFunctionName;
        self.assertEqual(['foo', 'foobar'], resolver.getArguments(request, controller));

        request = Request.create(['script']);
        request.attributes.set('foo', 'foo');
        controller = self._controller._controllerMethod3;

        try:
            resolver.getArguments(request, controller);
            self.fail('->getArguments() raise a RuntimeException exception if it cannot determine the argument value');
        except Exception  as e:
            self.assertTrue(isinstance(e, RuntimeException), '->getArguments() raise a RuntimeException exception if it cannot determine the argument value');

        request = Request.create(['script']);
        controller = self._controller._controllerMethod5;
        self.assertEqual([request], resolver.getArguments(request, controller), '->getArguments() injects the request');

class TestController(Object):

    def __call__(self, foo, bar = None):
        pass;

    def _controllerMethod1(self, foo):
        pass;

    def _controllerMethod2(self, foo, bar = None):
        pass;


    def _controllerMethod3(self, foo, foobar, bar = None):
        pass;

    @classmethod
    def _controllerMethod4(cls):
        pass;


    def _controllerMethod5(self, request):
        pass;


def some_controller_function(foo, foobar):
    pass;

if __name__ == '__main__':
    unittest.main();
