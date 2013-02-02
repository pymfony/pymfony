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


import os.path;
from pickle import dumps as serialize;
from pickle import loads as unserialize;

from pymfony.component.system import (
    interface,
    Object,
    SerializableInterface,
);

@interface
class ResourceInterface(Object):
    """ResourceInterface is the interface that must be implemented
    by all Resource classes.
    """
    def toString(self):
        """Returns a string representation of the Resource.

        @return: string
        """
        pass;

    def isFresh(self, timestamp):
        """Returns true if the resource has not been updated
        since the given timestamp.

        @param timestamp: int The last time the resource was loaded

        @return: Boolean
        """
        pass;

    def getResource(self):
        """Returns the resource tied to this Resource.

        @return: mixed The resource
        """
        pass;


class FileResource(ResourceInterface, SerializableInterface):
    def __init__(self, resource):
        self.__resource = str(os.path.realpath(str(resource)));

    def toString(self):
        return self.__resource;

    def getResource(self):
        return self.__resource;

    def isFresh(self, timestamp):
        if not os.path.exists(self.__resource):
            return False;
        return os.path.getmtime(self.__resource) < timestamp;

    def serialize(self):
        return serialize(self.__resource);

    def unserialize(self, serialized):
        self.__resource = unserialize(serialized);

#TODO:class DirectoryResource
