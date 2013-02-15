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

from pymfony.component.system import Object;
from pymfony.component.system.oop import interface;

from pymfony.component.config import FileLocator as BaseFileLocator;

@interface
class FileResourceLocatorInterface(Object):
    def locateResource(self, name, directory=None, first=True):
        """Returns the file path for a given resource.

        A Resource can be a file or a directory.
        The resource name must follow the following pattern:
            @BundleName/path/to/a/file.something
        where package is the name of the package
        and the remaining part is the relative path in the package.

        If directory is passed, and the first segment of the path is Resources,
        this method will look for a file named:
            directory/BundleName/path/without/Resources

        @param name: string A resource name to locate
        @param path: string A directory where to look for the resource first
        @param first: Boolean Whether to return the first path
            or paths for all matching bundles

        @return: string|array The absolute path of the resource
            or an array if $first is false

        @raise InvalidArgumentException: if the file cannot be found or
            the name is not valid
        @raise RuntimeException: if the name contains invalid/unsafe characters
        """
        pass;

class FileLocator(BaseFileLocator):
    """FileLocator uses the KernelInterface to locate resources in packages.
    """
    def __init__(self, kernel, path=None, paths=[]):
        """
        """
        assert isinstance(kernel, FileResourceLocatorInterface);
        self.__kernel = kernel;
        self.__path = path;

        if path:
            paths.append(path);

        BaseFileLocator.__init__(self, paths=paths);

    def locate(self, name, currentPath=None, first=True):
        if name.startswith("@"):
            return self.__kernel.locateResource(name, self.__path, first);

        return BaseFileLocator.locate(
            self,
            name,
            currentPath=currentPath,
            first=first
        );
