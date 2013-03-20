# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import os.path;
import sys;
if sys.version_info[0] >= 3:
    from urllib.parse import urlparse;
else:
    from urlparse import urlparse;

from pymfony.component.system import Object;
from pymfony.component.system.oop import interface;
from pymfony.component.system.types import String;
from pymfony.component.system.types import Array;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import RuntimeException;
from pymfony.component.system.serializer import unserialize;
from pymfony.component.system.serializer import serialize;

"""
"""

@interface
class FileLocatorInterface(Object):
    """
    @author Fabien Potencier <fabien@symfony.com>
    """
    def locate(self, name, currentPath = None, first = True):
        """Returns a full path for a given file name.

        @param name: mixed The file name to locate
        @param currentPath: string The current path
        @param first: boolean Whether to return the first occurrence 
                      or an array of filenames

        @return: string|list The full path to the file|A list of file paths

        @raise InvalidArgumentException: When file is not found

        """
        pass;




class FileLocator(FileLocatorInterface):
    """FileLocator uses an array of pre-defined paths to find files.

    @author Fabien Potencier <fabien@symfony.com>

    """
    def __init__(self, paths = None):
        """Constructor.

        @param paths: string|list A path or an array of paths where to look
            for resources

        """
        if paths is None:
            self._paths = list();
        elif isinstance(paths, String):
            self._paths = [paths];
        else:
            self._paths = list(paths);

    def locate(self, name, currentPath = None, first = True):
        """Returns a full path for a given file name.

        @param name: mixed The file name to locate
        @param currentPath: string The current path
        @param first: boolean Whether to return the first occurrence 
                      or an array of filenames

        @return: string|list The full path to the file|A list of file paths

        @raise InvalidArgumentException: When file is not found

        """
        if self.__isAbsolutePath(name):
            if not os.path.exists(name):
                raise InvalidArgumentException(
                    'The file "{0}" does not exist.'.format(name)
                );
            return name;

        filepaths = list();

        paths = [];
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


    def __isAbsolutePath(self, path):
        """Returns whether the file path is an absolute path.

        @param path: string A file path

        @return Boolean

        """
        if (path.startswith('/') or path.startswith('\\')
            or ( len(path) > 3 and path[0].isalpha()
                and path[1] == ':'
                and (path[2] == '\\' or path[2] == '/')
            )
            or urlparse(path)[0]
        ):
            return True;

        return False;


class ConfigCache(Object):
    """ConfigCache manages PHP cache files.

    When debug is enabled, it knows when to flush the cache
    thanks to an array of ResourceInterface instances.

    @author Fabien Potencier <fabien@symfony.com>

    """


    def __init__(self, path, debug):
        """Constructor.

        @param string  path  The absolute cache path
        @param Boolean debug Whether debugging is enabled or not

        """

        self.__file = path;
        self.__debug = bool(debug);


    def __str__(self):
        """Gets the cache file path.

        @return string The cache file path

        """

        return self.__file;


    def isFresh(self):
        """Checks if the cache is still fresh.:

        This method always returns True when debug is off and the
        cache file exists.

        @return Boolean True if the cache is fresh, False otherwise:

        """

        if not os.path.isfile(self.__file) :
            return False;


        if not self.__debug :
            return True;


        metadata = self.__file+'.meta';
        if not os.path.isfile(metadata) :
            return False;


        time = os.path.getmtime(self.__file);
        f = open(metadata);
        content = f.read();
        f.close();
        meta = unserialize(content);
        for resource in meta :
            if not resource.isFresh(time) :
                return False;

        return True;


    def write(self, content, metadata = None):
        """Writes cache.

        @param string              content  The content to write in the cache
        @param ResourceInterface[] metadata An array of ResourceInterface instances

        @raise RuntimeException When cache file can't be wrote

        """
        assert isinstance(metadata, list);

        dirname = os.path.dirname(self.__file);
        if not os.path.isdir(dirname) :
            try:
                os.makedirs(dirname, 0o777);
            except os.error:
                raise RuntimeException('Unable to create the {0} directory'.format(dirname));

        elif not os.access(dirname, os.W_OK) :
            raise RuntimeException('Unable to write in the {0} directory'.format(dirname));

        try:
            suffix = 0;
            while os.path.exists(self.__file+str(suffix)):
                suffix += 1;
            tmpFile = self.__file+str(suffix);
            f = open(tmpFile, 'w');
            f.write(content);
            f.close();
            if os.path.exists(self.__file):
                os.remove(self.__file);
            os.rename(tmpFile, self.__file);
            if hasattr(os, 'chmod'):
                umask = os.umask(0o220);
                os.umask(umask);
                os.chmod(self.__file, 0o666 & ~umask);
        except Exception:
            raise RuntimeException('Failed to write cache file "{0}".'.format(self.__file));
        else:
            try:
                if hasattr(os, 'chmod'):
                    umask = os.umask(0o220);
                    os.umask(umask);
                    os.chmod(self.__file, 0o666 & ~umask);
            except Exception:
                pass;
        finally:
            try:
                f.close();
            except Exception:
                pass;
            if os.path.exists(tmpFile):
                os.remove(tmpFile);


        if None is not metadata and True is self.__debug :
            filename = self.__file+'.meta';
            content = serialize(metadata);

            try:
                suffix = 0;
                while os.path.exists(filename+str(suffix)):
                    suffix += 1;
                tmpFile = filename+str(suffix);
                f = open(tmpFile, 'w');
                f.write(content);
                f.close();
                if os.path.exists(filename):
                    os.remove(filename);
                os.rename(tmpFile, filename);
            except Exception:
                pass;
            else:
                try:
                    if hasattr(os, 'chmod'):
                        umask = os.umask(0o220);
                        os.umask(umask);
                        os.chmod(filename, 0o666 & ~umask);
                except Exception:
                    pass;
            finally:
                try:
                    f.close();
                except Exception:
                    pass;
                if os.path.exists(tmpFile):
                    os.remove(tmpFile);
