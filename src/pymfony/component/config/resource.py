# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;


import os.path;
from pickle import dumps as serialize;
from pickle import loads as unserialize;
import re

from pymfony.component.system.oop import interface;
from pymfony.component.system import Object;

from pymfony.component.system import SerializableInterface

"""
"""

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


class DirectoryResource(ResourceInterface, SerializableInterface):
    """DirectoryResource represents a resources stored in a subdirectory tree.
 *
 * @author Fabien Potencier <fabien@symfony.com>

    """


    def __init__(self, resource, pattern = None):
        """Constructor.
     *
     * @param string resource The file path to the resource
     * @param string pattern  A pattern to restrict monitored files

        """
        self.__resource = None;
        self.__pattern = None;

        self.__resource = resource;
        self.__pattern = pattern;


    def __toString(self):
        """Returns a string representation of the Resource.
     *
     * @return string A string representation of the Resource

        """

        return str(self.__resource);


    def getResource(self):
        """Returns the resource tied to this Resource.
     *
     * @return mixed The resource

        """

        return self.__resource;


    def getPattern(self):

        return self.__pattern;


    def isFresh(self, timestamp):
        """Returns True if the resource has not been updated since the given timestamp.:
     *
     * @param integer timestamp The last time the resource was loaded
     *
     * @return Boolean True if the resource has not been updated, False otherwise:

        """

        if ( not os.path.isdir(self.__resource)) :
            return False;


        newestMTime = os.path.getmtime(self.__resource);
        files = os.listdir(self.__resource);
        for filename in files:
            # if regex filtering is enabled only check matching files:
            if (self.__pattern and os.path.isfile(filename) and  not re.match(self.__pattern, os.path.basename(filename))) :
                continue;

            # always monitor directories for changes, except the .. entries
            # (otherwise deleted files wouldn't get detected)
            if os.path.isdir(filename) and '/..' == filename[-3:] :
                continue;

            newestMTime = max(os.path.getmtime(filename), newestMTime);

        return newestMTime < timestamp;


    def serialize(self):

        return serialize([self.__resource, self.__pattern]);


    def unserialize(self, serialized):

        self.__resource, self.__pattern = unserialize(serialized);
