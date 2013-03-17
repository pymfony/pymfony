# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.event_dispatcher import EventDispatcherInterface;
from pymfony.component.event_dispatcher import ImmutableEventDispatcher;
from pymfony.component.event_dispatcher import Event;
from pymfony.component.system.exception import BadMethodCallException;
from pymfony.component.event_dispatcher import EventSubscriberInterface;

"""
"""

EVENT = Event();

class ImmutableEventDispatcherTest(unittest.TestCase):
    """@author Bernhard Schussek <bschussek@gmail.com>

    """

    def setUp(self):

        self._innerDispatcher = EventDispatcherInterfaceMock();
        self._dispatcher = ImmutableEventDispatcher(self._innerDispatcher);


    def testDispatchDelegates(self):

        self.assertEqual('result', self._dispatcher.dispatch('event', EVENT));


    def testGetListenersDelegates(self):

        self.assertEqual('result', self._dispatcher.getListeners('event'));


    def testHasListenersDelegates(self):

        self.assertEqual('result', self._dispatcher.hasListeners('event'));


    def testAddListenerDisallowed(self):
        """@expectedException BadMethodCallException

        """

        try:
            self._dispatcher.addListener('event', lambda: 'foo');

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, BadMethodCallException));


    def testAddSubscriberDisallowed(self):
        """@expectedException BadMethodCallException

        """

        subscriber = EventSubscriberInterfaceMock();

        try:
            self._dispatcher.addSubscriber(subscriber);
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, BadMethodCallException));



    def testRemoveListenerDisallowed(self):
        """@expectedException BadMethodCallException

        """

        try:
            self._dispatcher.removeListener('event', lambda: 'foo');
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, BadMethodCallException));



    def testRemoveSubscriberDisallowed(self):
        """@expectedException BadMethodCallException

        """

        subscriber = EventSubscriberInterfaceMock();

        try:
            self._dispatcher.removeSubscriber(subscriber);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, BadMethodCallException));



class EventDispatcherInterfaceMock(EventDispatcherInterface):
    def addListener(self, eventName, listener, priority=0):
        pass;

    def addSubscriber(self, subscriber):
        pass;

    def dispatch(self, eventName, event=None):
        if eventName == 'event' and event is EVENT:
            return 'result';

    def getListeners(self, eventName=None):
        if eventName == 'event':
            return 'result';

    def hasListeners(self, eventName=None):
        if eventName == 'event':
            return 'result';

    def removeListener(self, eventName, listener):
        pass;

    def removeSubscriber(self, subscriber):
        pass;

class EventSubscriberInterfaceMock(EventSubscriberInterface):
    @classmethod
    def getSubscribedEvents(cls):
        pass;

if __name__ == '__main__':
    unittest.main();
