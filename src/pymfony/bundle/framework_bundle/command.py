# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import re;
import shutil;
import os;

from pymfony.component.system.exception import StandardException;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import RuntimeException;
from pymfony.component.system.reflection import ReflectionObject;
from pymfony.component.system import clone;

from pymfony.component.console import Response;
from pymfony.component.console import Request;
from pymfony.component.console.output import OutputInterface;

from pymfony.component.console_routing import Router;
from pymfony.component.console_routing.interface import RouterInterface;

from pymfony.component.dependency import ContainerAware;

from pymfony.component.console_kernel.exception import NotFoundConsoleException;
from pymfony.component.console_kernel.interface import ConsoleKernelInterface;

"""
"""

class ListCommand(ContainerAware):
    """ListCommand displays the list of all available commands for the
    application.

    @author: Fabien Potencier <fabien@symfony.com>
    """
    def showAction(self, namespace = None, _o_raw = False):
        router = self._container.get('console.router');
        assert isinstance(router, Router);
        messages = list();

        routes = list();
        for name, route in router.getRouteCollection().all().items():
            path = route.getPath();
            if path.startswith('_fragment:') :
                continue;
            if namespace :
                if ':' in path and path.split(':')[0] == namespace :
                    routes.append(route);
            else:
                routes.append(route);

        width = 0;
        for route in routes :
            width = len(route.getPath()) if len(route.getPath()) > width else width;
        width += 2;

        messages.append(self.__getHelp(router));
        messages.append('');

        if namespace :
            messages.append("<comment>Available commands for the \"{0}\" namespace:</comment>".format(namespace));
        else:
            messages.append("<comment>Available commands:</comment>");

        # add commands by namespace
        lastNamespace = '_global';
        spaces = list();
        for route in self.__sortRoutes(routes) :
            name = route.getPath();
            if ':' in name :
                space = name.split(':')[0];
                append = spaces.append;
            else:
                space = '_global';
                append = messages.append;
            if not namespace and space != '_global' and lastNamespace != space :
                spaces.append('<comment>{0}</comment>'.format(space));
            lastNamespace = space;

            append(
                "  <info>{name:<{width}}</info> {desc}".format(
                name = name,
                desc = route.getDescription(),
                width = width
            ));

        messages.extend(spaces);

        return Response("\n".join(messages));

    def __sortRoutes(self, routes):
        sortedRoutes = list();
        routeNames = list();
        routeMap = dict();
        i = -1;
        for route in routes :
            i += 1;
            routeNames.append(route.getPath());
            routeMap[route.getPath()] = i;
        routeNames.sort();
        for routeName in routeNames:
            sortedRoutes.append(routes[routeMap[routeName]]);
        return sortedRoutes;


    def __getHelp(self, router):
        assert isinstance(router, RouterInterface);

        definition  = router.getRouteCollection().getDefinition();
        args = definition.getArguments();
        definition.setArguments();
        options = definition.asText();
        definition.setArguments(args);
        messages = [
            self.forward("FrameworkBundle:Version:long").getContent(),
            "",
            "<comment>Usage:</comment>",
            "  command [options] [arguments]",
            "",
            options,
        ];

        return '\n'.join(messages);


    def forward(self, controller, attributes = None):
        """Forwards the request to another controller.

        @param: string controller The controller name (a string like BlogBundle:Post:index)
        @param: dict  attributes An array of request attributes

        @return: Response A Response instance
        """
        if attributes is None:
            attributes = dict();
        assert isinstance(attributes, dict);

        attributes['_controller'] = controller;

        subRequest = clone(self._container.get('request'));
        subRequest.attributes.replace(attributes);

        return self._container.get('console_kernel').handle(subRequest, ConsoleKernelInterface.SUB_REQUEST);



class ExceptionCommand(ContainerAware):
    """ExceptionController to caught exceptions.

    @author: Alexandre Quercia <alquerci@email.com>
    """
    def showAction(self, request, exception):
        assert isinstance(request, Request);

        if isinstance(exception, NotFoundConsoleException):
            title = 'Sorry, the command you are executing for could not be found.';
        else:
            title = 'Whoops, looks like something went wrong.';

        debug = self._container.getParameter('kernel.debug');

        verbose = False;
        if request.hasOption('verbose'):
            verbose = request.getOption('verbose');

        content = "";
        nl = "\n";

        if debug:
            try:
                content += self._renderException(exception, nl, verbose);
            except Exception as e:
                message = e.getMessage() if isinstance(e, StandardException) else str(e);

                title = 'Exception thrown when handling an exception ({0}: {1})'.format(
                    ReflectionObject(e).getName(),
                    message
                );

        return Response("<error>{0}</error>{nl}{1}".format(
            title,
            content,
            nl=nl
        ));

    def _renderException(self, e, nl = "\n", verbose = False):
        content = "";
        while e:
            title = '  [{0}]  '.format(ReflectionObject(e).getName());
            lenght = len(title);
            width = 80; # TODO: console width - 1
            lines = list();
            message = e.getMessage() if isinstance(e, StandardException) else str(e);
            for line in list(re.split('\r?\n', message)):
                for line in filter(None, re.split('(.{{1,{0}}})'.format(str(width - 4)), line)):
                    lines.append('  {0}  '.format(line));
                    lenght = max(len(line) + 4, lenght);


            messages = [' ' * lenght, title + (' ' * max(0, lenght - len(title)))];

            for line in lines:
                messages.append(line + (' ' * (lenght - len(line))));


            messages.append(' ' * lenght);

            content += nl;
            content += nl;
            for message in messages:
                content += '<error>' + message + '</error>' + nl;

            content += nl;
            content += nl;

            if verbose and isinstance(e, StandardException):
                content += '<comment>Exception trace:</comment>' + nl;

                # exception related properties
                trace = e.getTrace();

                for stack in trace:

                    className = ReflectionObject(stack['locals']['self']).getName() if 'self' in stack['locals'] else '';
                    function = stack['name'];
                    file = stack['filename'] if 'filename' in stack else 'n/a';
                    line = stack['lineno'] if 'lineno' in stack else 'n/a';

                    content += ' {0}.{1}() at <info>{2}:{3}</info>{4}'.format(
                        className,
                        function,
                        file,
                        line,
                        nl,
                    );


                content += nl;
                content += nl;

            if isinstance(e, StandardException):
                e = e.getPrevious();
            else:
                e = False;

        return content;


class VersionCommand(ContainerAware):
    def longAction(self):
        name = self._container.getParameter('kernel.name');
        version = self._container.getParameter('kernel.version');

        if ('UNKNOWN' != name and 'UNKNOWN' != version) :
            content = '<info>{0}</info> version <comment>{1}</comment>'.format(
                name, version
            );
        else:
            content = '<info>Console Tool</info>';

        return Response(content);


class HelpCommand(ContainerAware):
    def showAction(self, command = 'help', command_name = 'help', _o_xml = False, wantHelps = False):
        if wantHelps :
            command_name = command;
        router = self._container.get('console.router');

        route = None;
        for route in router.getRouteCollection().all().values():
            if command_name == route.getPath() :
                break;

        if None is route:
            raise InvalidArgumentException('The command "{0}" does not exists.'.format(command_name));

        if _o_xml :
            response = Response(route.asXml());
            response.setOutputType(OutputInterface.OUTPUT_RAW);
        else:
            response = Response(route.asText());

        return response;


class CacheCommand(ContainerAware):
    def clearAction(self, _o_no_warmup, _o_no_optional_warmers):
        realCacheDir = self._container.getParameter('kernel.cache_dir');
        oldCacheDir = realCacheDir + '_old';

        if not os.access(realCacheDir, os.W_OK) :
            raise RuntimeException('Unable to write in the "{0}" directory'.format(realCacheDir));

        kernel = self._container.get('kernel');

        self._container.get('cache_clearer').clear(realCacheDir);

        if os.path.isdir(realCacheDir) :
            shutil.rmtree(oldCacheDir, True);
            shutil.copytree(realCacheDir, oldCacheDir, symlinks=True);
            shutil.rmtree(realCacheDir);

        if not _o_no_warmup :
            warmupDir = realCacheDir;
            self._warmup(warmupDir, not _o_no_optional_warmers);


        shutil.rmtree(oldCacheDir, True);

        return Response('Clearing the cache for the <info>{0}</info> environment with debug <info>{1}</info>'.format(kernel.getEnvironment(), kernel.isDebug()));


    def _warmup(self, warmupDir, enableOptionalWarmers = True):

        if os.path.isdir(warmupDir) :
            shutil.rmtree(warmupDir, True);

        parent = self._container.get('kernel');
        classKernel = parent.__class__;

        kernel = classKernel(parent.getEnvironment(), parent.isDebug());
        kernel.boot();

        warmer = self._container.get('cache_warmer');

        if enableOptionalWarmers :
            warmer.enableOptionalWarmers();

        warmer.warmUp(warmupDir);


    def warmupAction(self, _o_no_optional_warmers):

        kernel = self._container.get('kernel');

        warmer = self._container.get('cache_warmer');

        if not _o_no_optional_warmers :
            warmer.enableOptionalWarmers();

        warmer.warmUp(self._container.getParameter('kernel.cache_dir'));

        return Response('Warming up the cache for the <info>{0}</info> environment with debug <info>{1}</info>'.format(kernel.getEnvironment(), kernel.isDebug()));
