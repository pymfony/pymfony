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


from pymfony.component.clikernel import CliKernelEvents
from pymfony.component.dispatcher import EventSubscriberInterface
from pymfony.component.dependency import ContainerInterface
from pymfony.component.clikernel.event import GetResponseEvent
from pymfony.component.clikernel.exception import NotFoundCliException
from pymfony.component.console import Response
from pymfony.component.console.output import OutputInterface
from pymfony.component.console import Request
from pymfony.component.console.input import InputDefinition
from pymfony.component.clikernel.event import FilterResponseEvent
from pymfony.component.console.input import InputArgument
from pymfony.component.console.input import InputOption

class RouterListener(EventSubscriberInterface):
    """Initializes the context from the request and sets request attributes based on a matching route.
 *
 * @author Fabien Potencier <fabien@symfony.com>

    """

    def __init__(self, container):
        """Constructor.
     *
     * @param ContainerInterface

        """
        assert isinstance(container, ContainerInterface);

        self.__container = container;

    def onKernelRequest(self, event):
        assert isinstance(event, GetResponseEvent);

        request = event.getRequest();
        assert isinstance(request, Request);

        if (request.attributes.has('_controller')) :
            # routing is already done
            return;

        cmdName = request.getFirstArgument();

        defaultCommand = self.__container.getParameter('console.default_command');
        if not request.attributes.has('_default_command'):
            request.attributes.set('_default_command', defaultCommand);

        if request.hasParameterOption(['--help', '-h']):
            if not cmdName:
                cmdName = 'help';
                request.attributes.set('_default_command', 'help');
            else:
                request.attributes.set('_want_help', True);

        if request.hasParameterOption(['--no-interaction', '-n']):
            request.setInteractive(False);

        if request.hasParameterOption(['--version', '-V']):
            return Response(self.__container.get('cli_kernel').getLongVersion()); 

        # add attributes based on the request (routing)
        if not self.__container.hasParameter('console.commands'):
            raise NotFoundCliException('You need to registered commands.');

        commands = self.__container.getParameter('console.commands');

        if not cmdName:
            cmdName = request.attributes.get('_default_command');
        if cmdName not in commands:
            raise NotFoundCliException('The command "{0}" is not '
                'registered.'.format(cmdName)
            );

        controllerInfos = commands[cmdName];
        controller = self.__stripController(controllerInfos['_controller']);
        request.attributes.set('_controller', controller);

        definition = self._getDefaultInputDefinition();
        # parse the definition
        if '_definition' in controllerInfos:
            cmdDefinition = controllerInfos["_definition"];
            if isinstance(cmdDefinition, InputDefinition):
                definition.addArguments(cmdDefinition.getArguments());
                definition.addOptions(cmdDefinition.getOptions());

        request.bind(definition);

    def _getDefaultInputDefinition(self):
        """Gets the default input definition.

        @return InputDefinition An InputDefinition instance

        """

        return InputDefinition([
            InputArgument('command', InputArgument.REQUIRED, 'The command to execute'),

            InputOption('--help', '-h', InputOption.VALUE_NONE, 'Display this help message.'),
            InputOption('--quiet', '-q', InputOption.VALUE_NONE, 'Do not output any message.'),
            InputOption('--verbose', '-v', InputOption.VALUE_NONE, 'Increase verbosity of messages.'),
            InputOption('--version', '-V', InputOption.VALUE_NONE, 'Display this application version.'),
            InputOption('--ansi', '', InputOption.VALUE_NONE, 'Force ANSI output.'),
            InputOption('--no-ansi', '', InputOption.VALUE_NONE, 'Disable ANSI output.'),
            InputOption('--no-interaction', '-n', InputOption.VALUE_NONE, 'Do not ask any interactive question.'),
        ]);



    def __stripController(self, controller):
        """
        @param: dict controllerInfos
        """
        controller = str(controller);

        '@SomeBundle:controllerName:actionName'
        if not controller.startswith('@'):
            raise NotFoundCliException();

        bundleName, controllerName, actionName = controller[1:].split(':', 3);

        bundle = self.__container.get('kernel').getBundle(bundleName);
        bundleNamespace = bundle.getNamespace();
        className = ( bundleNamespace + '.command.' +
            controllerName + 'Controller'
        );
        methodName = actionName + 'Action';

        return className + "::" + methodName;


    @classmethod
    def getSubscribedEvents(self):

        return {
            CliKernelEvents.REQUEST: [['onKernelRequest', 32]],
        };


class ResponseListener(EventSubscriberInterface):
    """ResponseListener fixes the Response headers based on the Request.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    def onKernelResponse(self, event):
        """Filters the Response.

        @param: FilterResponseEvent event A FilterResponseEvent instance

        """
        assert isinstance(event, FilterResponseEvent);

        response = event.getResponse();
        request = event.getRequest();

        if request.hasParameterOption(['--ansi']):
            response.setDecorated(True);
        elif request.hasParameterOption(['--no-ansi']):
            response.setDecorated(False);

        if request.hasParameterOption(['--quiet', '-q']):
            response.setVerbosity(OutputInterface.VERBOSITY_QUIET);
        elif request.hasParameterOption(['--verbose', '-v']):
            response.setVerbosity(OutputInterface.VERBOSITY_VERBOSE);


    @classmethod
    def getSubscribedEvents(cls):
        return {
            CliKernelEvents.RESPONSE: 'onKernelResponse',
        };
