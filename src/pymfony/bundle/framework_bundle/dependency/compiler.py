# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

from pymfony.component.system import ClassLoader;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.types import OrderedDict;

from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency.compilerpass import CompilerPassInterface;
from pymfony.component.dependency.definition import Reference;

from pymfony.component.event_dispatcher import EventSubscriberInterface;
from pymfony.component.dependency.interface import ContainerInterface
from pymfony.component.config import ConfigCache

"""
"""

class RegisterKernelListenersPass(CompilerPassInterface):
    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        if not container.hasDefinition('event_dispatcher'):
            return;

        definition = container.getDefinition('event_dispatcher');

        listeners = container.findTaggedServiceIds('kernel.event_listener');
        for identifier, events in listeners.items():
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
                    event['event'], [identifier, event['method']], priority
                ]);

        subscribers = container.findTaggedServiceIds('kernel.event_subscriber');
        for identifier, events in subscribers.items():
            # We must assume that the class value has been correctly filled,
            # even if the service is created by a factory
            qualClassName = container.getDefinition(identifier).getClass();

            classType = ClassLoader.load(qualClassName);

            if not issubclass(classType, EventSubscriberInterface):
                raise InvalidArgumentException(
                    'Service "{0}" must implement interface "{1}".'
                    ''.format(identifier, repr(EventSubscriberInterface))
                );

            definition.addMethodCall('addSubscriberService', [
                identifier,
                qualClassName
            ]);



class RoutingResolverPass(CompilerPassInterface):
    """Adds tagged routing.loader services to routing.resolver service

    @author: Fabien Potencier <fabien@symfony.com>
    """

    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        if (False is container.hasDefinition('routing.resolver')) :
            return;


        definition = container.getDefinition('routing.resolver');

        for identifier, attributes in container.findTaggedServiceIds('routing.loader').items():
            definition.addMethodCall('addLoader', [Reference(identifier)]);



class AddCacheClearerPass(CompilerPassInterface):
    """Registers the cache clearers.

    @author Dustin Dobervich <ddobervich@gmail.com>

    """

    def process(self, container):
        """@inheritDoc

        """
        assert isinstance(container, ContainerBuilder);

        if not container.hasDefinition('cache_clearer') :
            return;


        clearers = list();
        for identifier in container.findTaggedServiceIds('kernel.cache_clearer').keys() :
            clearers.append(Reference(identifier));


        container.getDefinition('cache_clearer').replaceArgument(0, clearers);




class AddCacheWarmerPass(CompilerPassInterface):
    """Registers the cache warmers.

    @author Fabien Potencier <fabien@symfony.com>

    """

    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        if not container.hasDefinition('cache_warmer') :
            return;


        warmers = dict();
        for identifier, attributes in container.findTaggedServiceIds('kernel.cache_warmer').items() :
            priority = attributes[0]['priority'] if attributes and 'priority' in attributes[0] else '0';
            if priority not in warmers:
                warmers[priority] = list();
            warmers[priority].append(Reference(identifier));


        if not warmers :
            return;


        # sort by priority and flatten
        krsortWarmers = self.__krsort(warmers);
        warmers = list();
        for warmerList in krsortWarmers.values():
            for warmer in warmerList:
                warmers.append(warmer);

        container.getDefinition('cache_warmer').replaceArgument(0, warmers);

    def __krsort(self, d):
        assert isinstance(d, dict);

        ret = OrderedDict();
        for k in sorted(list(d.keys()), reverse=True):
            ret[k] = d[k];

        return ret;


class CompilerDebugDumpPass(CompilerPassInterface):
    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        cache = ConfigCache(self.getCompilerLogFilename(container), False);
        cache.write('\n'.join(container.getCompiler().getLog()));


    @classmethod
    def getCompilerLogFilename(cls, container):
        assert isinstance(container, ContainerInterface);

        className = container.getParameter('kernel.container_class');

        return container.getParameter('kernel.cache_dir')+'/'+className+'Compiler.log';
