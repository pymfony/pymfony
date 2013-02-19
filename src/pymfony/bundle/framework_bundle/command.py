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

from pymfony.component.console import Response
from pymfony.component.dependency import ContainerAware

class ListController(ContainerAware):
    def showAction(self):
        commands = self._container.getParameter('console.commands');

        commandList = list();
        for name, command in commands.items():
            if '_description' in command:
                description = command['_description'];
            else:
                description = "no desciption";

            commandList.append("<info>{0}</info>: <comment>{1}</comment>".format(
                name,
                description
            ));

        return Response("Command List:\n- "+"\n- ".join(commandList));
