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

from pymfony.component.system.exception import RuntimeException;

class DefinitionException(RuntimeException):
    pass;

class InvalidConfigurationException(DefinitionException):
    __path = None;
    def setPath(self, path):
        self.__path = path;
    def getPath(self):
        return self.__path;

class InvalidDefinitionException(DefinitionException):
    pass;

class UnsetKeyException(DefinitionException):
    pass;

class InvalidTypeException(InvalidConfigurationException):
    pass;


class ForbiddenOverwriteException(InvalidConfigurationException):
    pass;

class DuplicateKeyException(InvalidConfigurationException):
    pass;
