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

from pymfony.component.system.exception import SystemException;

class FileLoaderLoadException(SystemException):
    # TODO: code
    pass;

class FileLoaderImportCircularReferenceException(FileLoaderLoadException):
    # TODO: code
    pass;
