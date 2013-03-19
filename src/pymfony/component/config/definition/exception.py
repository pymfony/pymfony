# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

from pymfony.component.system.exception import RuntimeException;

"""
"""

class DefinitionException(RuntimeException):
    """Base exception for all configuration exceptions

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    pass;


class InvalidConfigurationException(DefinitionException):
    """A very general exception which can be thrown whenever non of the more
    specific exceptions is suitable.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self, message="", code=None, previous=None):
        DefinitionException.__init__(self, message=message, code=code, previous=previous);

        self.__path = None;

    def setPath(self, path):
        self.__path = path;

    def getPath(self):
        return self.__path;


class InvalidDefinitionException(DefinitionException):
    """Raise when an error is detected in a node Definition.

    @author Victor Berchet <victor.berchet@suumit.com>

    """
    pass;


class UnsetKeyException(DefinitionException):
    """This exception is usually not encountered by the end-user, but only used
    internally to signal the parent scope to unset a key.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    pass;


class InvalidTypeException(InvalidConfigurationException):
    """This exception is thrown if an invalid type is encountered.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    pass;


class ForbiddenOverwriteException(InvalidConfigurationException):
    """This exception is thrown when a configuration path is overwritten from a
    subsequent configuration file, but the entry node specifically forbids this.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    pass;


class DuplicateKeyException(InvalidConfigurationException):
    """This exception is thrown whenever the key of an array is not unique.
    This can only be the case if the configuration is coming from an XML file.

    @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """
    pass;
