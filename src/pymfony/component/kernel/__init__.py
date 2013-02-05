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

import os;
from time import time;
import pickle;
import re;


from pymfony.component.system import Object, abstract, interface;
from pymfony.component.system import Array;
from pymfony.component.system import final;
from pymfony.component.system import ReflectionObject;
from pymfony.component.system.exception import LogicException;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import RuntimeException;
from pymfony.component.dependency import Container;
from pymfony.component.dependency import ContainerInterface;
from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency import ParameterBag;
from pymfony.component.dependency import ContainerAwareInterface;
from pymfony.component.dependency import ExtensionInterface;
from pymfony.component.dependency import ContainerAware;
from pymfony.component.dependency.compilerpass import ResolveParameterPlaceHoldersPass
from pymfony.component.dependency.loader import IniFileLoader;
from pymfony.component.dependency.loader import JsonFileLoader;
from pymfony.component.dependency.extension import Extension as BaseExtension;
from pymfony.component.config import FileLocator as BaseFileLocator;
from pymfony.component.config.loader import LoaderResolver;
from pymfony.component.config.loader import DelegatingLoader;

from pymfony.component.kernel.bundle import BundleInterface;
from pymfony.component.kernel.config import FileLocator;
from pymfony.component.kernel.config import FileResourceLocatorInterface;
from pymfony.component.kernel.dependency import MergeExtensionConfigurationPass;
from pymfony.component.kernel.debug import ExceptionHandler;

@interface
class KernelInterface(FileResourceLocatorInterface):
    def registerContainerConfiguration(self, loader):
        """Loads the container configuration

        @param loader: LoaderInterface A LoaderInterface instance
        """
        pass;

    def boot(self):
        """Boots the current kernel."""
        pass;

    def shutdown(self):
        """Shutdowns the kernel."""
        pass;

    def getName(self):
        """Gets the name of the kernel.

        @return: string The kernel name
        """
        pass;

    def getEnvironment(self):
        """Gets the environment.

        @return: string The current environment
        """
        pass;

    def isDebug(self):
        """Checks if debug mode is enabled.

        @return: Boolean true if debug mode is enabled, false otherwise
        """
        pass;

    def getContainer(self):
        """Gets the current container.

        @return: ContainerInterface A ContainerInterface instance
        """
        pass;

    def getStartTime(self):
        """Gets the request start time (not available if debug is disabled).

        @return: float The request start timestamp
        """
        pass;

    def getNamespace(self):
        """Gets the Kernel namespace.

        @return: string The Bundle namespace
        """
        pass;

    def registerBundles(self):
        """Returns a list of bundles to registers.

        @return: BundleInterface[] An list of bundle instances.
        """
        pass;

    def getBundles(self):
        """Gets the registered bundle instances.

        @return: BundleInterface{} An dict of registered bundle instances
        """
        pass;

    def isClassInActiveBundle(self, className):
        """Checks if a given class name belongs to an active bundle.

        @param className: string A class name

        @return: Boolean true if the class belongs to an active bundle,
            false otherwise
        """
        pass;

    def getBundle(self, name, first=True):
        """Returns a bundle and optionally its descendants by its name.

        @param name: string Bundle name
        @param first: Boolean Whether to return the first bundle only or
            together with its descendants

        @return: BundleInterface|BundleInterface[] A BundleInterface instance
            or an list of BundleInterface instances if $first is false

        @raise InvalidArgumentException: when the bundle is not enabled
        """
        pass;

    def getCharset(self):
        """Gets the charset of the application.

        @return: string The charset
        """
        pass;

    def getLogDir(self):
        """Gets the log directory.

        @return: string The log directory
        """
        pass;

    def getCacheDir(self):
        """Gets the cache directory.

        @return: string The cache directory
        """
        pass;

    def getRootDir(self):
        """Gets the application root dir.

        @return: string The application root dir
        """
        pass;


class Kernel(KernelInterface):
    def __init__(self, environment, debug):
        self._environment = environment;
        self._debug = bool(debug);
        self._name = None;
        self._rootDir = None;
        self._bundles = dict();
        self._bundleMap = dict();

        self._container = None;
        self._extension = None;
        self._booted = False;

        self._rootDir = self.getRootDir();
        self._name = self.getName();

        if self._debug:
            self._startTime = time();

        self.init();

    def init(self):
        if self._debug:
            ExceptionHandler.register(self._debug);

    def __copy__(self):
        clone = Object.__copy__(self);
        if self._debug:
            clone._startTime = time();
        clone._booted = False;
        clone._container = None;
        return clone;

    def getKernelParameters(self):
        bundles = dict();
        for name, bundle in self._bundles.items():
            bundles[name] = ReflectionObject(bundle).getName();

        parameters = {
            'kernel.root_dir': self._rootDir,
            'kernel.logs_dir': self.getLogDir(),
            'kernel.cache_dir': self.getCacheDir(),
            'kernel.environment': self._environment,
            'kernel.debug': self._debug,
            'kernel.name': self._name,
            'kernel.bundles': bundles,
            'kernel.charset': self.getCharset(),
        };
        parameters.update(self.getEnvParameters());
        return parameters;

    def getEnvParameters(self):
        parameters = dict();
        for key, value in os.environ.items():
            key = str(key);
            prefix = self.getName().upper()+"__";
            prefix.replace("-", "");
            if key.startswith(prefix):
                name = key.replace("__", ".").lower();
                parameters[name] = value;

        return parameters;

    def boot(self):
        if self._booted:
            return;

        # init container
        self._initializeBundles();

        # init container
        self._initializeContainer();

        for bundle in self.getBundles().values():
            assert isinstance(bundle, ContainerAwareInterface);
            bundle.setContainer(self._container);
            bundle.boot();

        self._booted = True;



    def _initializeContainer(self):
        """Initializes the service container."""
        self._container = self.buildContainer();

    def _initializeBundles(self):
        """Initializes the data structures related to the bundle management.

         - the bundles property maps a bundle name to the bundle instance,
         - the bundleMap property maps a bundle name to the bundle inheritance
           hierarchy (most derived bundle first).

        @raise LogicException: if two bundles share a common name
        @raise LogicException: if a bundle tries to extend a non-registered
                               bundle
        @raise LogicException: if a bundle tries to extend itself
        @raise LogicException: if two bundles extend the same ancestor
        """
        #  init bundle
        self._bundles = dict();
        topMostBundles = dict();
        directChildren = dict();

        for bundle in self.registerBundles():
            assert isinstance(bundle, BundleInterface);

            name = bundle.getName();
            if name in self._bundles.keys():
                raise LogicException(
                    'Trying to register two bundles with the same name "{0}"'
                    ''.format(name)
                );

            self._bundles[name] = bundle;

            parentName = bundle.getParent();
            if parentName:
                if parentName in directChildren.keys():
                    raise LogicException(
                        'Bundle "{0}" is directly extended by two bundles '
                        '"{1}" and "{2}".'
                        ''.format(parentName, name, directChildren[parentName])
                    );
                if parentName == name:
                    raise LogicException(
                        'Bundle "{0}" can not extend itself.'.format(name)
                    );
                directChildren[parentName] = name;
            else:
                topMostBundles[name] = bundle;

            # look for orphans
            diff = Array.diff(
                list(directChildren.keys()),
                list(self._bundles.keys()),
            );
            if diff:
                raise LogicException(
                    'Bundle "{0}" extends bundle "{1}", which is not registered.'
                    ''.format(directChildren[diff[0]], diff[0])
                );

            # inheritance
            self._bundleMap = dict();
            for name, bundle in topMostBundles.items():
                bundleMap = [bundle];
                hierarchy = [name];

                while name in directChildren.keys():
                    name = directChildren[name];
                    bundleMap.insert(0, self._bundles[name]);
                    hierarchy.append(name);

                for name in hierarchy:
                    self._bundleMap[name] = bundleMap;
                    bundleMap.pop();



    def buildContainer(self):
        resouces = {
            'cache': self.getCacheDir(),
            'logs': self.getLogDir(),
        };
        for name, path in resouces.items():
            if not os.path.isdir(path):
                try:
                    os.makedirs(path, 0o777);
                except Exception:
                    raise RuntimeException(
                        "Unable to create the {0} directory ({1})\n"
                        "".format(name, path)
                    );
            elif not os.access(path, os.W_OK):
                raise RuntimeException(
                    "Unable to write in the {0} directory ({1})\n"
                    "".format(name, path)
                );

        container = self.getContainerBuilder();
        extensions = list();

        container.addObjectResource(self);

        for bundle in self._bundles.values():
            extension = bundle.getContainerExtension();
            if extension:
                container.registerExtension(extension);
                extensions.append(extension.getAlias());

            if self._debug:
                container.addObjectResource(bundle);

        for bundle in self._bundles.values():
            bundle.build(container);

        # ensure these extensions are implicitly loaded
        container.getCompilerPassConfig().setMergePass(
            MergeExtensionConfigurationPass(extensions)
        );

        container.getCompilerPassConfig().setOptimizationPasses([
            ResolveParameterPlaceHoldersPass()
        ]);

        cont = self.registerContainerConfiguration(
            self.getContainerLoader(container)
        );
        if not cont is None:
            container.merge(cont);

        container.set('kernel', self);
        container.compile();

        return container;

    def getNamespace(self):
        return str(type(self).__module__);

    def getContainerLoader(self, container):
        assert isinstance(container, ContainerInterface);
        locator = FileLocator(self);
        resolver = LoaderResolver([
            IniFileLoader(container, locator),
            JsonFileLoader(container, locator),
        ]);
        return DelegatingLoader(resolver);

    def getContainerBuilder(self):
        return ContainerBuilder(ParameterBag(self.getKernelParameters()));

    def shutdown(self):
        if not self._booted:
            return;
        self._booted = False;

        for bundle in self.getBundles().values():
            assert isinstance(bundle, BundleInterface);
            bundle.shutdown();
            bundle.setContainer(None);

        self._container = None;

    def getBundles(self):
        return self._bundles;

    def isClassInActiveBundle(self, className):
        for bundle in self._bundles.values():
            assert isinstance(bundle, BundleInterface);
            if 0 == str(className).find(bundle.getNamespace()):
                return True;

        return False;

    def getBundle(self, name, first=True):
        if name not in self._bundleMap:
            raise InvalidArgumentException(
                'Bundle "{0}" does not exist or it is not enabled. Maybe you '
                'forgot to add it in the registerBundles() method of your {1} '
                'file?'.format(name, ReflectionObject(self).getFileName())
            );

        if first is True:
            return self._bundleMap[name][0];

        return self._bundleMap[name];

    def getName(self):
        if self._name is None:
            self._name = str(type(self).__name__);
            self._name = re.sub(r"/Kernel$/", "", self._name);
        return self._name;

    def getEnvironment(self):
        return self._environment;

    def getContainer(self):
        return self._container;

    def getStartTime(self):
        if self._debug:
            return self._startTime;
        else:
            return -1;

    def isDebug(self):
        return self._debug;

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

        If BundleName is empty the application root directory is use.
            %kernel.root_dir%/path/to/a/file.something

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
        name = str(name);
        isResource = False;

        if not name.startswith("@"):
            raise InvalidArgumentException(
                'A resource name must start with @ ("{0}" given).'
                "".format(name)
            )

        if ".." in name:
            raise RuntimeException(
                'File name "{0}" contains invalid characters (..).'
                "".format(name)
            );

        bundleName = name[1:];
        if "/" in bundleName:
            bundleName, path = bundleName.split("/", 1);

        if path.startswith("Resources") and directory:
            isResource = True;
        overridePath = path[9:];
        resourceBundle = None;
        files = [];

        if bundleName:
            bundles = self.getBundle(bundleName, False);
            for bundle in bundles:
                if isResource:
                    filename = os.path.join(
                        directory,
                        bundle.getName(),
                        overridePath
                    );
                    if os.path.exists(filename):
                        if resourceBundle:
                            raise RuntimeException(
                                '"{0}" resource is hidden by a resource from '
                                'the "{1}" derived bundle. Create a "{2}" '
                                'file to override the bundle resource.'
                                ''.format(
                                filename,
                                resourceBundle,
                                directory+'/'+bundles[0].getName()+overridePath
                            ));
                        if first:
                            return filename;
                        files.append(filename);
    
                filename = os.path.join(bundle.getPath(), path);
                if os.path.exists(filename):
                    if first and not isResource:
                        return filename;
                    files.append(filename);
                    resourceBundle = bundle.getName();

        elif not isResource:
            # check in root_dir when bundle name is empty
            filename = os.path.join(self._rootDir, path);
            if os.path.exists(filename):
                if first and not isResource:
                    return filename;
                files.append(filename);

        if files:
            if first and isResource:
                return files[0];
            else:
                return files;

        raise InvalidArgumentException(
            'Unable to find file "{0}".'.format(name)
        );

    def getRootDir(self):
        if self._rootDir is None:
            r = ReflectionObject(self);
            self._rootDir = os.path.dirname(r.getFileName()).replace('\\', '/');

        return self._rootDir;

    def getCacheDir(self):
        return self._rootDir+'/Resources/cache/'+self._environment;

    def getLogDir(self):
        return self._rootDir+'/Resources/logs/'+self._environment;

    def getCharset(self):
        return 'UTF-8';
