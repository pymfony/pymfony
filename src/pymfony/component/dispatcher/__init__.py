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

import sys;
if sys.version_info[0] >= 3:
    basestring = str;

from pymfony.component.system import Object;
from pymfony.component.system import interface;
from pymfony.component.system import Tool;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import BadMethodCallException;
from pymfony.component.system import ArrayAccessInterface;
from pymfony.component.system import IteratorAggregateInterface;

from pymfony.component.dependency import ContainerInterface;

@interface
class EventDispatcherInterface(Object):
    """The EventDispatcherInterface is the central point of Symfony's event
    listener system. Listeners are registered on the manager and events are
    dispatched through the manager.
    """

    def dispatch(self, eventName, event=None):
        """Dispatches an event to all registered listeners.

        @param eventName: string The name of the event to dispatch. The name of
                                 the event is the name of the method that is
                                 invoked on listeners.
        @param event: Event The event to pass to the event handlers/listeners.
                            If not supplied, an empty Event instance is created.

        @return: Event
        """
        pass;

    def addListener(self, eventName, listener, priority=0):
        """Adds an event listener that listens on the specified events.

        @param eventName: string The event to listen on
        @param listener: callable The listener
        @param priority: int The higher this value, the earlier an event
                             listener will be triggered in the chain
                             (defaults to 0)
        """
        pass;

    def addSubscriber(self, subscriber):
        """Adds an event subscriber.

        The subscriber is asked for all the events he is
        interested in and added as a listener for these events.

        @param subscriber: EventSubscriberInterface The subscriber.
        """
        pass;

    def removeListener(self, eventName, listener):
        """Removes an event listener from the specified events.

        @param eventName: string|list The event(s) to remove a listener from
        @param listener: callable The listener to remove
        """
        pass;

    def removeSubscriber(self, subscriber):
        """Removes an event subscriber.

        @param subscriber: EventSubscriberInterface The subscriber.
        """
        pass;

    def getListeners(self, eventName=None):
        """Gets the listeners of a specific event or all listeners.

        @param eventName: string The name of the event

        @return: list|dict The event listeners for the specified event, or all
                 event listeners by event name
        """
        pass;

    def hasListeners(self, eventName=None):
        """Checks whether an event has any registered listeners.

        @param eventName: string The name of the event

        @return: Boolean true if the specified event has any listeners,
                 false otherwise
        """
        pass;

@interface
class EventSubscriberInterface(Object):
    """An EventSubscriber knows himself what events he is interested in.

    If an EventSubscriber is added to an EventDispatcherInterface, the manager
    invokes {@link: getSubscribedEvents} and registers the subscriber as a
    listener for all returned events.
    """
    @classmethod
    def getSubscribedEvents(cls):
        """Returns an array of event names this subscriber wants to listen to.

        The array keys are event names and the value can be:

         * The method name to call (priority defaults to 0)
         * An array composed of the method name to call and the priority
         * An array of arrays composed of the method names to call and
           respective priorities, or 0 if unset

        For instance:

         * {'eventName': 'methodName'}
         * {'eventName': ('methodName', priority)}
         * {'eventName': [('methodName1', priority), ('methodName2')]}

        @return: dict The event names to listen to
        """
        pass;


class Event(Object):
    """Event is the base class for classes containing event data.

    This class contains no event data. It is used by events that do not pass
    state information to an event handler when an event is raised.

    You can call the method stopPropagation() to abort the execution of
    further listeners in your event listener.
    """

    def __init__(self):
        self.__propagationStopped = False;
        self.__dispatcher = None;
        self.__name = None;

    def isPropagationStopped(self):
        """Returns whether further event listeners should be triggered.

        @see: Event.stopPropagation
        @return: Boolean Whether propagation was already stopped for this event.
        """
        return self.__propagationStopped;

    def stopPropagation(self):
        """Stops the propagation of the event to further event listeners.

        If multiple event listeners are connected to the same event, no
        further event listener will be triggered once any trigger calls
        stopPropagation().
        """
        self.__propagationStopped = True;

    def setDispatcher(self, dispatcher):
        """Stores the EventDispatcher that dispatches this Event

        @param dispatcher: EventDispatcherInterface
        """
        assert isinstance(dispatcher, EventDispatcherInterface);

        self.__dispatcher = dispatcher;

    def getDispatcher(self):
        """Returns the EventDispatcher that dispatches this Event

        @return: EventDispatcherInterface
        """
        return self.__dispatcher;

    def getName(self):
        """Gets the event's name.

        @return: string
        """
        return self.__name;

    def setName(self, name):
        """Sets the event's name property.

        @param name: string The event name.
        """
        self.__name = str(name);

class GenericEvent(Event, ArrayAccessInterface, IteratorAggregateInterface):
    """Event encapsulation class.

    Encapsulates events thus decoupling the observer from the subject they
    encapsulate.
    """

    def __init__(self, subject=None, arguments={}):
        """Encapsulate an event with subject and arguments.

        @param subject: mixed The subject of the event, usually an object.
        @param arguments: dict Arguments to store in the event.
        """
        assert isinstance(arguments, list);

        Event.__init__(self);
        self._subject = subject;
        self._arguments = arguments;

    def getSubject(self):
        """Getter for subject property.

        @return: mixed The observer subject.
        """
        return self._subject;

    def getArgument(self, key):
        """Get argument by key.

        @param key: string Key

        @return: mixed Contents of array key.

        @raise InvalidArgumentException: If key is not found.
        """
        if self.hasArgument(key):
            return self._arguments[key];

        raise InvalidArgumentException('{0} not found in {1}'.format(
            key, self.getName()
        ));

    def addArgument(self, key, value):
        """Add argument to event.

        @param key: string the argument name.
        @param value: mixed Value.

        @return: GenericEvent The current instance.
        """
        self._arguments[key] = value;

        return self;

    def getArguments(self):
        """Getter for all arguments.

        @return: dict All arguments
        """
        return self._arguments;

    def setArguments(self, arguments={}):
        """Set arguments property.

        @param arguments: dict Arguments.

        @return: GenericEvent The current instance.
        """
        assert isinstance(arguments, dict);

        self._arguments = arguments;

        return self;

    def setArgument(self, key, value):
        """Sets argument to event.

        @param key: string the argument name.
        @param value: mixed Value.

        @return: GenericEvent The current instance.
        """
        self._arguments[str(key)] = value;

        return self;

    def hasArgument(self, key):
        """Has argument.

        @param key: string Key of arguments array.

        @return: Boolean
        """
        return key in self._arguments;

    def __getitem__(self, item):
        return self.getArgument(item);

    def __setitem__(self, item, value):
        return self.setArgument(item, value);

    def __delitem__(self, item):
        if self.hasArgument(item):
            del self._arguments[item];

    def __contains__(self, item):
        return self.hasArgument(item);

    def __iter__(self):
        return self._arguments.__iter__();


class EventDispatcher(EventDispatcherInterface):
    def __init__(self):
        self.__listeners = dict();
        self.__sorted = dict();

    def dispatch(self, eventName, event=None):
        if event is None:
            event = Event();
        else:
            assert isinstance(event, Event);

        event.setDispatcher(self);
        event.setName(eventName);

        if eventName not in self.__listeners:
            return event;

        self._doDispatch(self.getListeners(eventName), eventName, event);

        return event;

    def getListeners(self, eventName=None):
        if eventName:
            if eventName not in self.__sorted:
                self.__sortListeners(eventName);

            return self.__sorted[eventName];

        for eventName in self.__listeners.keys():
            if eventName not in self.__sorted:
                self.__sortListeners(eventName);

        return self.__sorted;

    def hasListeners(self, eventName=None):
        return bool(len(self.getListeners(eventName)));

    def addListener(self, eventName, listener, priority=0):
        if eventName not in self.__listeners:
            self.__listeners[eventName] = dict();

        if priority not in self.__listeners[eventName].keys():
            self.__listeners[eventName][priority] = list();

        self.__listeners[eventName][priority].append(listener);

        if eventName in self.__sorted.keys():
            del self.__sorted[eventName];

    def removeListener(self, eventName, listener):
        if eventName not in self.__listeners:
            return;

        for priority, listeners in self.__listeners[eventName].items():
            try:
                key = listeners.index(listener);
            except ValueError:
                pass;
            else:
                del self.__listeners[eventName][priority][key];
                try:
                    del self.__sorted[eventName];
                except KeyError:
                    pass;

    def addSubscriber(self, subscriber):
        assert isinstance(subscriber, EventSubscriberInterface);

        for eventName, params in subscriber.getSubscribedEvents().items():
            if isinstance(params, basestring):
                self.addListener(eventName, [subscriber, params]);
            elif isinstance(params[0], basestring):
                priority = 0;
                if len(params) > 1:
                    priority = params[1];
                self.addListener(
                    eventName,
                    [subscriber, params[0]],
                    priority
                );
            else:
                for listener in params:
                    priority = 0;
                    if len(listener) > 1:
                        priority = listener[1];
                    self.addListener(
                        eventName,
                        [subscriber, listener[0]],
                        priority
                    );

    def removeSubscriber(self, subscriber):
        assert isinstance(subscriber, EventSubscriberInterface);

        for eventName, params in subscriber.getSubscribedEvents().items():
            if isinstance(params, list) and isinstance(params[0], list):
                for listener in params:
                    self.removeListener(eventName, [subscriber, listener[0]]);
            else:
                if isinstance(params, basestring):
                    method = params;
                else:
                    method = params[0];
                self.removeListener(eventName, [subscriber, method]);


    def _doDispatch(self, listeners, eventName, event):
        """Triggers the listeners of an event.

        This method can be overridden to add functionality that is executed
        for each listener.

        @param listeners: list[callable] The event listeners.
        @param eventName: string The name of the event to dispatch.
        @param event: Event The event object to pass to the event
                      handlers/listeners.
        """
        assert isinstance(event, Event);

        for listener in listeners:
            if isinstance(listener, list):
                getattr(listener[0], listener[1])(event);
            else:
                listener(event);
            if event.isPropagationStopped():
                break;

    def __sortListeners(self, eventName):
        """Sorts the internal list of listeners for the given event by priority.

        @param eventName: string The name of the event.
        """
        self.__sorted[eventName] = list();

        if eventName in self.__listeners.keys():
            sortedList = self.__krsort(self.__listeners[eventName]);
            for l in sortedList:
                self.__sorted[eventName].extend(l);

    def __krsort(self, d):
        """Sort an dict by key in reverse order.

        @return: list The reverse list of value ([value, ...]).
        """
        l = list();
        for k in sorted(d.keys(), reverse=True):
            l.append(d[k]);
        return l;

class ImmutableEventDispatcher(EventDispatcherInterface):
    """A read-only proxy for an event dispatcher.
    """
    def __init__(self, dispatcher):
        """Creates an unmodifiable proxy for an event dispatcher.

        @param dispatcher: EventDispatcherInterface The proxied event
                           dispatcher.
        """
        assert isinstance(dispatcher, EventDispatcherInterface);

        self.__dispatcher = dispatcher;

    def dispatch(self, eventName, event=None):
        assert isinstance(event, Event);
        self.__dispatcher.dispatch(eventName, event);

    def addListener(self, eventName, listener, priority=0):
        raise BadMethodCallException(
            'Unmodifiable event dispatchers must not be modified.'
        );

    def addSubscriber(self, subscriber):
        raise BadMethodCallException(
            'Unmodifiable event dispatchers must not be modified.'
        );

    def removeListener(self, eventName, listener):
        raise BadMethodCallException(
            'Unmodifiable event dispatchers must not be modified.'
        );

    def removeSubscriber(self, subscriber):
        raise BadMethodCallException(
            'Unmodifiable event dispatchers must not be modified.'
        );

    def getListeners(self, eventName=None):
        return self.__dispatcher.getListeners(eventName);

    def hasListeners(self, eventName=None):
        return self.__dispatcher.hasListeners(eventName);

class ContainerAwareEventDispatcher(EventDispatcher):
    """Lazily loads listeners and subscribers from the dependency injection
    container.
    """
    def __init__(self, container):
        """Constructor.

        @param container: ContainerInterface A ContainerInterface instance
        """
        assert isinstance(container, ContainerInterface);

        self.__container = container;
        self.__listenerIds = dict();
        self.__listeners = dict();

        EventDispatcher.__init__(self);

    def addListenerService(self, eventName, callback, priority=0):
        """Adds a service as event listener

        @param eventName: string Event for which the listener is added.
        @param callback: list The service ID of the listener service &
                         the method name that has to be called
        @param priority: integer The higher this value, the earlier an event
                         listener will be triggered in the chain.
                         Defaults to 0.

        @raise InvalidArgumentException: When the callback is not valid.
        """
        if not isinstance(callback, list) or len(callback) != 2:
            raise InvalidArgumentException(
                'Expected an array("service", "method") argument'
            );

        if eventName not in self.__listenerIds:
            self.__listenerIds[eventName] = list();

        self.__listenerIds[eventName].append([
            callback[0],
            callback[1],
            priority,
        ]);

    def removeListener(self, eventName, listener):
        self._lazyLoad(eventName);

        if eventName in self.__listeners:
            for key, l in self.__listeners.items():
                i = -1;
                for args in self.__listenerIds[eventName]:
                    i += 1;
                    serviceId, method, priority = args;
                    if key == serviceId+'.'+method:
                        if listener is [l, method]:
                            del self.__listeners[eventName][key];
                            if not self.__listeners[eventName]:
                                del self.__listeners[eventName];
                            del self.__listenerIds[eventName][i];
                            if not self.__listenerIds[eventName]:
                                del self.__listenerIds[eventName];

        EventDispatcher.removeListener(self, eventName, listener);

    def hasListeners(self, eventName=None):
        if eventName is None:
            return bool(self.__listenerIds or self.__listeners);

        if eventName in self.__listenerIds.keys():
            return True;

        return EventDispatcher.hasListeners(self, eventName=eventName)

    def addSubscriberService(self, serviceId, className):
        """Adds a service as event subscriber

        @param serviceId: string The service ID of the subscriber service
        @param className: string The service's class name (which must
                                 implement EventSubscriberInterface)
        """
        moduleName, className = Tool.split(className);
        try:
            module = __import__(moduleName, globals(), {}, [className], 0);
        except TypeError:
            module = __import__(moduleName, globals(), {}, ["__init__"], 0);
        subscriber = getattr(module, className);

        assert isinstance(subscriber, EventSubscriberInterface);

        for eventName, params in subscriber.getSubscribedEvents():
            if eventName not in self.__listenerIds:
                self.__listenerIds[eventName] = dict();

            if isinstance(params, basestring):
                self.__listenerIds[eventName].append([
                    serviceId,
                    params,
                    0,
                ]);
            elif isinstance(params[0], basestring):
                priority = 0;
                if len(params) > 1:
                    priority = params[1];
                self.__listenerIds[eventName].append([
                    serviceId,
                    params[0],
                    priority,
                ]);
            else:
                for listener in params:
                    priority = 0;
                    if len(listener) > 1:
                        priority = listener[1];
                    self.__listenerIds[eventName].append([
                        serviceId,
                        listener[0],
                        priority
                    ]);


    def dispatch(self, eventName, event=None):
        """Lazily loads listeners for this event from the dependency injection
        container.

        @raise InvalidArgumentException: if the service is not defined
        """

        self._lazyLoad(eventName);

        return EventDispatcher.dispatch(self, eventName, event);


    def getContainer(self):
        return self.__container;

    def _lazyLoad(self, eventName):
        """Lazily loads listeners for this event from the dependency injection
        container.

        @param eventName: string The name of the event to dispatch. The name of
                                 the event is the name of the method that is
                                 invoked on listeners.
        """
        if eventName not in self.__listeners.keys():
            self.__listeners[eventName] = dict();

        if eventName in self.__listenerIds.keys():
            for args in self.__listenerIds[eventName]:
                serviceId, method, priority = args;
                listener = self.__container.get(serviceId);

                key = serviceId+'.'+method;
                if key not in self.__listeners[eventName].keys():
                    self.addListener(
                        eventName,
                        [listener, method],
                        priority
                    );
                elif listener is not self.__listeners[eventName][key]:
                    EventDispatcher.removeListener(self,
                        eventName,
                        [self.__listeners[eventName][key], method]
                    );
                    self.addListener(
                        eventName,
                        [listener, method],
                        priority
                    );

                    self.__listeners[eventName][key] = listener;






