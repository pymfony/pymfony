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
import sys;
if sys.version_info[0] >= 3:
    from urllib.parse import urlparse;
else:
    from urlparse import urlparse;

from pymfony.component.system.types import String;
from pymfony.component.system import Object;
from pymfony.component.system.oop import interface;
from pymfony.component.system import Tool;
from pymfony.component.system.types import Array
from pymfony.component.system.exception import InvalidArgumentException;

from pymfony.component.config.exception import FileLoaderImportCircularReferenceException;
from pymfony.component.config.exception import FileLoaderLoadException;

@interface
class FileLocatorInterface(Object):
    def locate(self, name, currentPath=None, first=True):
        """Returns a full path for a given file name.
        
        @param name: mixed The file name to locate
        @param currentPath: string The current path
        @param first: boolean Whether to return the first occurrence 
                      or an array of filenames
        """
        pass;




class FileLocator(FileLocatorInterface):
    def __init__(self, paths=None):
        """
        @param paths: string|list A path or an array of paths 
            where to look for resources
        """
        if paths is None:
            self._paths = list();
        elif isinstance(paths, String):
            self._paths = [paths];
        else:
            self._paths = list(paths);

    def locate(self, name, currentPath=None, first=True):
        if self.__isAbsolutePath(name):
            if not os.path.exists(name):
                raise InvalidArgumentException(
                    'The file "{0}" does not exist.'.format(name)
                );
            return name;

        filepaths = list();

        paths = [""];
        if currentPath:
            paths.append(currentPath);
        paths.extend(self._paths);

        for path in paths:
            filename = os.path.join(path, name);
            if os.path.exists(filename):
                if first:
                    return filename;
                filepaths.append(filename);

        if not filepaths:
            raise InvalidArgumentException(
                'The file "{0}" does not exist (in: {1}).'
                ''.format(name, ", ".join(paths))
            );

        return Array.uniq(filepaths);


    def __isAbsolutePath(self, name):
        if os.path.isabs(name) and urlparse(name).scheme:
            return True;

