# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.system.reflection import ReflectionClass;
from pymfony.component.event_dispatcher import Event
from pymfony.component.dependency import Container
from pymfony.component.event_dispatcher import ContainerAwareEventDispatcher
from pymfony.component.dependency import Scope
from pymfony.component.system.exception import InvalidArgumentException
from pymfony.component.system import Object
from pymfony.component.event_dispatcher import EventSubscriberInterface

"""
"""


class ContainerAwareEventDispatcherTest(unittest.TestCase):

    def setUp(self):

        if not ReflectionClass('pymfony.component.dependency.container').exists() :
            self.__skip = True;
        else:
            self.__skip = False;



    def testAddAListenerService(self):
        if self.__skip:
            return;

        event = Event();

        service = Service();

        container = Container();
        container.set('service.listener', service);

        dispatcher = ContainerAwareEventDispatcher(container);
        dispatcher.addListenerService('onEvent', ['service.listener', 'onEvent']);

        dispatcher.dispatch('onEvent', event);


    def testAddASubscriberService(self):

        event = Event();

        service = SubscriberService();

        container = Container();
        container.set('service.subscriber', service);

        dispatcher = ContainerAwareEventDispatcher(container);
        dispatcher.addSubscriberService('service.subscriber', ReflectionClass(SubscriberService).getName());

        dispatcher.dispatch('onEvent', event);


    def testPreventDuplicateListenerService(self):

        event = Event();

        service = Service();

        container = Container();
        container.set('service.listener', service);

        dispatcher = ContainerAwareEventDispatcher(container);
        dispatcher.addListenerService('onEvent', ['service.listener', 'onEvent'], 5);
        dispatcher.addListenerService('onEvent', ['service.listener', 'onEvent'], 10);

        dispatcher.dispatch('onEvent', event);


    def testTriggerAListenerServiceOutOfScope(self):
        """@expectedException InvalidArgumentException

        """

        try:
            service = Service();

            scope = Scope('scope');
            container = Container();
            container.addScope(scope);
            container.enterScope('scope');

            container.set('service.listener', service, 'scope');

            dispatcher = ContainerAwareEventDispatcher(container);
            dispatcher.addListenerService('onEvent', ['service.listener', 'onEvent']);

            container.leaveScope('scope');
            dispatcher.dispatch('onEvent');

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));



    def testReEnteringAScope(self):

        event = Event();

        service1 = Service();

        scope = Scope('scope');
        container = Container();
        container.addScope(scope);
        container.enterScope('scope');

        container.set('service.listener', service1, 'scope');

        dispatcher = ContainerAwareEventDispatcher(container);
        dispatcher.addListenerService('onEvent', ['service.listener', 'onEvent']);
        dispatcher.dispatch('onEvent', event);

        service2 = Service();

        container.enterScope('scope');
        container.set('service.listener', service2, 'scope');

        dispatcher.dispatch('onEvent', event);

        container.leaveScope('scope');

        dispatcher.dispatch('onEvent');


    def testHasListenersOnLazyLoad(self):

        event = Event();

        service = Service();

        container = Container();
        container.set('service.listener', service);

        dispatcher = ContainerAwareEventDispatcher(container);
        dispatcher.addListenerService('onEvent', ['service.listener', 'onEvent']);

        event.setDispatcher(dispatcher);
        event.setName('onEvent');

        self.assertTrue(dispatcher.hasListeners());

        if (dispatcher.hasListeners('onEvent')) :
            dispatcher.dispatch('onEvent');



    def testGetListenersOnLazyLoad(self):

        event = Event();

        service = Service();

        container = Container();
        container.set('service.listener', service);

        dispatcher = ContainerAwareEventDispatcher(container);
        dispatcher.addListenerService('onEvent', ['service.listener', 'onEvent']);

        listeners = dispatcher.getListeners();

        self.assertTrue('onEvent' in listeners);

        self.assertEqual(1, len(dispatcher.getListeners('onEvent')));


    def testRemoveAfterDispatch(self):

        event = Event();

        service = Service();

        container = Container();
        container.set('service.listener', service);

        dispatcher = ContainerAwareEventDispatcher(container);
        dispatcher.addListenerService('onEvent', ['service.listener', 'onEvent']);

        dispatcher.dispatch('onEvent', Event());
        dispatcher.removeListener('onEvent', [container.get('service.listener'), 'onEvent']);
        self.assertFalse(dispatcher.hasListeners('onEvent'));


    def testRemoveBeforeDispatch(self):

        event = Event();

        service = Service();

        container = Container();
        container.set('service.listener', service);

        dispatcher = ContainerAwareEventDispatcher(container);
        dispatcher.addListenerService('onEvent', ['service.listener', 'onEvent']);

        dispatcher.removeListener('onEvent', [container.get('service.listener'), 'onEvent']);
        self.assertFalse(dispatcher.hasListeners('onEvent'));



class Service(Object):

    def onEvent(self, e):
        assert isinstance(e, Event);




class SubscriberService(EventSubscriberInterface):

    @classmethod
    def getSubscribedEvents(cls):

        return {
            'onEvent' : 'onEvent',
            'onEvent' : ['onEvent', 10],
            'onEvent' : ['onEvent'],
        };


    def onEvent(self, e):
        assert isinstance(e, Event);


if __name__ == '__main__':
    unittest.main();
