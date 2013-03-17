# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import unittest;

from pymfony.component.event_dispatcher import Event;
from pymfony.component.event_dispatcher import EventDispatcher;
from pymfony.component.event_dispatcher import EventSubscriberInterface;

"""
"""

class TestEventDispatcher(unittest.TestCase):

    # Some pseudo events
    preFoo = 'pre.foo';
    postFoo = 'post.foo';
    preBar = 'pre.bar';
    postBar = 'post.bar';

    def setUp(self):
        self.dispatcher = EventDispatcher();
        self.listener = TestEventListener();

    def tearDown(self):
        self.dispatcher = None;
        self.listener = None;

    def testInitialState(self):
        self.assertEqual(dict(), self.dispatcher.getListeners());
        self.assertFalse(self.dispatcher.hasListeners(self.preFoo));
        self.assertFalse(self.dispatcher.hasListeners(self.postFoo));

    def testAddListener(self):
        self.dispatcher.addListener('pre.foo', [self.listener, 'preFoo']);
        self.dispatcher.addListener('post.foo', [self.listener, 'postFoo']);
        self.assertTrue(self.dispatcher.hasListeners(self.preFoo));
        self.assertTrue(self.dispatcher.hasListeners(self.postFoo));
        self.assertEqual(1, len(self.dispatcher.getListeners(self.preFoo)));
        self.assertEqual(1, len(self.dispatcher.getListeners(self.postFoo)));
        self.assertEqual(2, len(self.dispatcher.getListeners()));

    def testGetListenersSortsByPriority(self):
        listener1 = TestEventListener();
        listener2 = TestEventListener();
        listener3 = TestEventListener();
        listener1.name = '1';
        listener2.name = '2';
        listener3.name = '3';

        self.dispatcher.addListener('pre.foo', [listener1, 'preFoo'], -10);
        self.dispatcher.addListener('pre.foo', [listener2, 'preFoo'], 10);
        self.dispatcher.addListener('pre.foo', [listener3, 'preFoo']);

        expected = [
            [listener2, 'preFoo'],
            [listener3, 'preFoo'],
            [listener1, 'preFoo'],
        ];

        self.assertEqual(expected, self.dispatcher.getListeners('pre.foo'));

    def testGetAllListenersSortsByPriority(self):
        listener1 = TestEventListener();
        listener2 = TestEventListener();
        listener3 = TestEventListener();
        listener4 = TestEventListener();
        listener5 = TestEventListener();
        listener6 = TestEventListener();

        self.dispatcher.addListener('pre.foo', listener1, -10);
        self.dispatcher.addListener('pre.foo', listener2);
        self.dispatcher.addListener('pre.foo', listener3, 10);
        self.dispatcher.addListener('post.foo', listener4, -10);
        self.dispatcher.addListener('post.foo', listener5);
        self.dispatcher.addListener('post.foo', listener6, 10);

        expected = {
            'pre.foo': [listener3, listener2, listener1],
            'post.foo': [listener6, listener5, listener4],
        };

        self.assertEqual(expected, self.dispatcher.getListeners());

    def testDispatch(self):
        self.dispatcher.addListener('pre.foo', [self.listener, 'preFoo']);
        self.dispatcher.addListener('post.foo', [self.listener, 'postFoo']);
        self.dispatcher.dispatch(self.preFoo);
        self.assertTrue(self.listener.preFooInvoked);
        self.assertFalse(self.listener.postFooInvoked);
        self.assertTrue(isinstance(self.dispatcher.dispatch('noevent'), Event));
        self.assertTrue(isinstance(self.dispatcher.dispatch(self.preFoo), Event));
        event = Event();
        ret = self.dispatcher.dispatch(self.preFoo, event);
        self.assertEqual('pre.foo', event.getName());
        self.assertTrue(event is ret);

    def testDispatchForClosure(self):
        self.invoked = 0;
        def listener(e):
            self.invoked += 1;

        self.dispatcher.addListener('pre.foo', listener);
        self.dispatcher.addListener('post.foo', listener);
        self.dispatcher.dispatch(self.preFoo);
        self.assertEqual(1, self.invoked);

    def testStopEventPropagation(self):
        otherListener = TestEventListener();

        # postFoo() stops the propagation, so only one listener should
        # be executed
        # Manually set priority to enforce self.listener to be called first
        self.dispatcher.addListener('post.foo', [self.listener, 'postFoo'], 10);
        self.dispatcher.addListener('post.foo', [otherListener, 'preFoo']);
        self.dispatcher.dispatch(self.postFoo);
        self.assertTrue(self.listener.postFooInvoked);
        self.assertFalse(otherListener.postFooInvoked);

    def testDispatchByPriority(self):
        invoked = list();
        def listener1(e):
            invoked.append('1');
        def listener2(e):
            invoked.append('2');
        def listener3(e):
            invoked.append('3');

        self.dispatcher.addListener('pre.foo', listener1, -10);
        self.dispatcher.addListener('pre.foo', listener2);
        self.dispatcher.addListener('pre.foo', listener3, 10);
        self.dispatcher.dispatch(self.preFoo);
        self.assertEqual(['3', '2', '1'], invoked);

    def testRemoveListener(self):
        self.dispatcher.addListener('pre.bar', self.listener);
        self.assertTrue(self.dispatcher.hasListeners(self.preBar));
        self.dispatcher.removeListener('pre.bar', self.listener);
        self.assertFalse(self.dispatcher.hasListeners(self.preBar));
        self.dispatcher.removeListener('notExists', self.listener);

    def testAddSubscriber(self):
        eventSubscriber = TestEventSubscriber();
        self.dispatcher.addSubscriber(eventSubscriber);
        self.assertTrue(self.dispatcher.hasListeners(self.preFoo));
        self.assertTrue(self.dispatcher.hasListeners(self.postFoo));

    def testAddSubscriberWithPriorities(self):
        eventSubscriber = TestEventSubscriber();
        self.dispatcher.addSubscriber(eventSubscriber);

        eventSubscriber = TestEventSubscriberWithPriorities();
        self.dispatcher.addSubscriber(eventSubscriber);

        listeners = self.dispatcher.getListeners('pre.foo');
        self.assertTrue(self.dispatcher.hasListeners(self.preFoo));
        self.assertEqual(2, len(listeners));
        self.assertTrue(isinstance(listeners[0][0], TestEventSubscriberWithPriorities));

    def testAddSubscriberWithMultipleListeners(self):
        eventSubscriber = TestEventSubscriberWithMultipleListeners();
        self.dispatcher.addSubscriber(eventSubscriber);

        listeners = self.dispatcher.getListeners('pre.foo');
        self.assertTrue(self.dispatcher.hasListeners(self.preFoo));
        self.assertEqual(2, len(listeners));
        self.assertEqual('preFoo2', listeners[0][1]);

    def testRemoveSubscriber(self):
        eventSubscriber = TestEventSubscriber();
        self.dispatcher.addSubscriber(eventSubscriber);
        self.assertTrue(self.dispatcher.hasListeners(self.preFoo));
        self.assertTrue(self.dispatcher.hasListeners(self.postFoo));
        self.dispatcher.removeSubscriber(eventSubscriber);
        self.assertFalse(self.dispatcher.hasListeners(self.preFoo));
        self.assertFalse(self.dispatcher.hasListeners(self.postFoo));

    def testRemoveSubscriberWithPriorities(self):
        eventSubscriber = TestEventSubscriberWithPriorities();
        self.dispatcher.addSubscriber(eventSubscriber);
        self.assertTrue(self.dispatcher.hasListeners(self.preFoo));
        self.dispatcher.removeSubscriber(eventSubscriber);
        self.assertFalse(self.dispatcher.hasListeners(self.preFoo));

    def testRemoveSubscriberWithMultipleListeners(self):
        eventSubscriber = TestEventSubscriberWithMultipleListeners();
        self.dispatcher.addSubscriber(eventSubscriber);
        self.assertTrue(self.dispatcher.hasListeners(self.preFoo));
        self.assertEqual(2, len(self.dispatcher.getListeners(self.preFoo)));
        self.dispatcher.removeSubscriber(eventSubscriber);
        self.assertFalse(self.dispatcher.hasListeners(self.preFoo));

    def testEventReceivesTheDispatcherInstance(self):
        test = self;
        dispatcher = list();

        def callback(event):
            dispatcher.append(event.getDispatcher());

        self.dispatcher.addListener('test', callback);
        self.dispatcher.dispatch('test');
        self.assertTrue(self.dispatcher is dispatcher[0]);

class TestEventListener():
    preFooInvoked = False;
    postFooInvoked = False;

    # Listener methods

    def preFoo(self, e):
        assert isinstance(e, Event);
        self.preFooInvoked = True;

    def postFoo(self, e):
        assert isinstance(e, Event);
        self.postFooInvoked = True;

        e.stopPropagation();

class TestEventSubscriber(EventSubscriberInterface):
    @classmethod
    def getSubscribedEvents(cls):
        return {'pre.foo': 'preFoo', 'post.foo': 'postFoo'};

class TestEventSubscriberWithPriorities(EventSubscriberInterface):
    @classmethod
    def getSubscribedEvents(cls):
        return {
            'pre.foo': ['preFoo', 10],
            'post.foo': ['postFoo'],
        };

class TestEventSubscriberWithMultipleListeners(EventSubscriberInterface):
    @classmethod
    def getSubscribedEvents(cls):
        return {'pre.foo': [
            ['preFoo1'],
            ['preFoo2', 10],
        ]};


if __name__ == '__main__':
    unittest.main();
