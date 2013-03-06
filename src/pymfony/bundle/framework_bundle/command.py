# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import re;

from pymfony.component.system.exception import StandardException;
from pymfony.component.system.reflection import ReflectionObject;

from pymfony.component.console import Response;

from pymfony.component.console_routing import Router;
from pymfony.component.console_routing import Route;

from pymfony.component.dependency import ContainerAware;
from pymfony.component.console import Request
from pymfony.component.console_kernel.exception import NotFoundConsoleException

"""
"""

class ListCommand(ContainerAware):
    """ListCommand displays the list of all available commands for the
    application.

    @author: Fabien Potencier <fabien@symfony.com>
    """
    def showAction(self):
        router = self._container.get('console.router');
        assert isinstance(router, Router);
        commandList = list();
        for name, route in router.getRouteCollection().all().items():
            assert isinstance(route, Route);

            if name == '_default':
                continue;

            commandList.append(
                "<info>{0}</info>: <comment>{1}</comment>".format(
                route.getPath(),
                route.getDescription(),
            ));

        return Response("Command List:\n- "+"\n- ".join(commandList));

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
