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

import re;

from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system import Tool;
from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency.compiler import CompilerPassInterface;
from pymfony.component.dispatcher import EventSubscriberInterface;

class RegisterKernelListenersPass(CompilerPassInterface):
    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        if not container.hasDefinition('event_dispatcher'):
            return;

        definition = container.getDefinition('event_dispatcher');

        listeners = container.findTaggedServiceIds('kernel.event_listener');
        for identifier, events in listeners:
            for event in events:
                if 'priority' in event:
                    priority = event['priority'];
                else:
                    priority = 0;

                if 'event' not in event:
                    raise InvalidArgumentException(
                        'Service "{0}" must define the "event" attribute on'
                        '"kernel.event_listener" tags.'.format(identifier)
                    );

                if 'method' not in event:
                    parts = event['event'].split(".");
                    method = "";
                    for part in parts:
                        method += part.title().replace('_', '');
                    event['method'] = 'on'+method;

                definition.addMethodCall('addListenerService', [
                    event['event'], [identifier, event['method'], priority]
                ]);

        subscribers = container.findTaggedServiceIds('kernel.event_subscriber');
        for identifier, events in subscribers:
            # We must assume that the class value has been correctly filled,
            # even if the service is created by a factory
            qualClassName = container.getDefinition(identifier).getClass();

            moduleName, className = Tool.split(qualClassName);
            try:
                module = __import__(moduleName, globals(), {}, [className], 0);
            except TypeError:
                module = __import__(moduleName, globals(), {}, ["__init__"], 0);
            classType = getattr(module, className);

            if not isinstance(classType, EventSubscriberInterface):
                raise InvalidArgumentException(
                    'Service "{0}" must implement interface "{1}".'
                    ''.format(identifier, repr(EventSubscriberInterface))
                );

            definition.addMethodCall('addSubscriberService', [
                identifier,
                qualClassName
            ]);
