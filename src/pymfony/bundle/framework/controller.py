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
from pymfony.component.system import Object
from pymfony.component.console.output import OutputInterface

class TestController(Object):
    def commandAction(self, request):
        response = Response();
        response.getOutput().setVerbosity(OutputInterface.VERBOSITY_QUIET);
        return response;
