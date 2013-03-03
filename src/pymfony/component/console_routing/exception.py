# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

from pymfony.component.system.exception import RuntimeException
from pymfony.component.console_routing.interface import ExceptionInterface

"""
"""


class ResourceNotFoundException(RuntimeException, ExceptionInterface):
    """The resource was not found.

    This exception should trigger an exit code 127 in your application code.

    @author: Kris Wallsmith <kris@symfony.com>

    @api:
    """
    pass;
