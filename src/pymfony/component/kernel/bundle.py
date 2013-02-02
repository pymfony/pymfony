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

import re;

from pymfony.component.system import interface;
from pymfony.component.system import abstract;
from pymfony.component.system.exception import LogicException;
from pymfony.component.system import ReflectionObject;

from pymfony.component.dependency import ContainerAwareInterface;
from pymfony.component.dependency import ContainerAware;
from pymfony.component.dependency import ContainerBuilder;



@interface
class BundleInterface(ContainerAwareInterface):
    def boot(self):
        """Boots the Bundle.
        """
        pass;

    def shutdown(self):
        """Shutdowns the Bundle.
        """
        pass;

    def build(self, container):
        """Builds the bundle.

        It is only ever called once when the cache is empty.

        @param container: ContainerBuilder A ContainerBuilder instance
        """
        pass;

    def getContainerExtension(self):
        """Returns the container extension that should be implicitly loaded.

        @return: ExtensionInterface|null The default extension or null
            if there is none
        """
        pass;

    def getParent(self):
        """Returns the bundle name that this bundle overrides.

        Despite its name, this method does not imply any parent/child
        relationship between the bundles, just a way to extend and override
        an existing Bundle.

        @return: string The Bundle name it overrides or null if no parent
        """
        pass;

    def getName(self):
        """Returns the bundle name (the class short name).

        @return: string The Bundle name
        """
        pass;

    def getNamespace(self):
        """Gets the Bundle namespace.

        @return: string The Bundle namespace
        """
        pass;

    def getPath(self):
        """Gets the Bundle directory path.

        The path should always be returned as a Unix path (with /).

        @return: string The Bundle absolute path
        """
        pass;



@abstract
class Bundle(ContainerAware, BundleInterface):
    """An implementation of BundleInterface that adds a few conventions

    for DependencyInjection extensions.
    """

    def __init__(self):
        self._name = None;
        self._reflected = None;
        self._extension = None;

    def boot(self):
        pass;

    def shutdown(self):
        pass;

    def build(self, container):
        assert isinstance(container, ContainerBuilder);

    def getContainerExtension(self):
        """Returns the bundle's container extension.

        @return: ExtensionInterface|null The container extension

        @raise LogicException: When alias not respect the naming convention
        """
        if self._extension is None:
            basename = re.sub(r"Bundle$", "", self.getName());

            className = "{0}Extension".format(basename);
            moduleName = self.getNamespace();
            try:
                module = __import__(moduleName, globals(), {}, [className], 0);
            except TypeError:
                module = __import__(moduleName, globals(), {}, ['__init__'], 0);

            if hasattr(module, className):
                extension = getattr(module, className)();
                # check naming convention
                expectedAlias = ContainerBuilder.underscore(basename);
                if expectedAlias != extension.getAlias():
                    raise LogicException(
                        'The extension alias for the default extension of a '
                        'bundle must be the underscored version of the '
                        'bundle name ("{0}" instead of "{1}")'
                        ''.format(expectedAlias, extension.getAlias())
                    );

                self._extension = extension;
            else:
                self._extension = False;

        if self._extension:
            return self._extension;

    def getNamespace(self):
        if self._reflected is None:
            self._reflected = ReflectionObject(self);
        return self._reflected.getNamespaceName();

    def getPath(self):
        if self._reflected is None:
            self._reflected = ReflectionObject(self);
        return self._reflected.getFileName();

    def getName(self):
        if self._name is None:
            self._name = str(type(self).__name__);
        return self._name;

    def getParent(self):
        return None;
