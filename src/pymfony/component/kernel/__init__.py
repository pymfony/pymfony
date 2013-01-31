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


from pymfony.component.system import Object, abstract, interface;
from pymfony.component.system import Array;
from pymfony.component.system import ReflectionObject;
from pymfony.component.dependency import Container;
from pymfony.component.dependency import ContainerInterface;
from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency import ParameterBag;
from pymfony.component.dependency import IniFileLoader;
from pymfony.component.dependency import JsonFileLoader;
from pymfony.component.dependency import CompilerPassInterface;
from pymfony.component.dependency import MergeExtensionConfigurationPass as\
BaseMergeExtensionConfigurationPass;
from pymfony.component.dependency import Extension as BaseExtension;
from pymfony.component.config import FileLocator as BaseFileLocator;
from pymfony.component.config import LoaderResolver;
from pymfony.component.config import DelegatingLoader;

@interface
class KernelInterface(Object):

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

    def locateResource(self, name, directory=None, first=True):
        """Returns the file path for a given resource.

        A Resource can be a file or a directory.
        The resource name must follow the following pattern:
            @<package>/path/to/a/file.something
        where package is the name of the package
        and the remaining part is the relative path in the package.

        If directory is passed, and the first segment of the path is Resources,
        this method will look for a file named:
            directory/<package>/path/without/Resources

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

    def getContainerExtension(self):
        """Returns the container extension that should be implicitly loaded.

        @return: ExtensionInterface|null The default extension
                 or null if there is none
        """
        pass;


    def getNamespace(self):
        """Gets the Kernel namespace.

        @return: string The Bundle namespace
        """
        pass;

class Kernel(KernelInterface):
    def __init__(self, environment, debug):
        self._environment = environment;
        self._debug = bool(debug);
        self._name = None;
        self._rootDir = None;
        self._rootDir = self.getRootDir();

        self._container = None;
        self._extention = None;
        self._booted = False;

        self._name = self.getName();

        if self._debug:
            self._startTime = time();

    def getKernelParameters(self):
        parameters = {
            'kernel.root_dir': self._rootDir,
            'kernel.environment': self._environment,
            'kernel.debug': self._debug,
            'kernel.name': self._name,
        };
        parameters.update(self.getEnvParameters());
        return parameters;

    def getEnvParameters(self):
        parameters = dict();
        for key, value in os.environ.items():
            key = str(key);
            prefix = str(self._name).upper();
            prefix.replace("-", "");
            if key.startswith(prefix):
                name = key.replace("_", ".").lower();
                parameters[name] = value;

        return parameters;

    def boot(self):
        if self._booted:
            return;

        # init container
        self.initializeContainer();

        self._booted = True;

    def initializeContainer(self):
        """Initializes the service container."""
        self._container = self.buildContainer();

    def buildContainer(self):
        ressouces = {
            'cache': self.getCacheDir()
        };
        for name, path in ressouces.items():
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

        # add this kernel as an extension
        extention = self.getContainerExtension();
        if extention:
            container.registerExtension(extention);
            extensions.append(extention.getAlias());

        container.addObjectResource(self);

        # ensure these extensions are implicitly loaded
        container.getCompilerPassConfig().setMergePass(
            MergeExtensionConfigurationPass(extensions)
        );

        cont = self.registerContainerConfiguration(
            self.getContainerLoader(container)
        );
        if not cont is None:
            container.merge(cont);

        container.addCompilerPass(AddClassesToCachePass(self));

        container.set('kernel', self);
        container.compile();

        return container;

    def getContainerExtension(self):
        """Returns the bundle's container extension.

        @return: ExtensionInterface|null The container extension

        @raise LogicException: When alias not respect the naming convention
        """
        if self._extention is None:
            basename = self.getName();

            className = "{0}Extension".format(basename);
            moduleName = self.getNamespace();
            try:
                module = __import__(moduleName, globals(), {}, [className], 0);
            except TypeError:
                module = __import__(moduleName, globals(), {}, ['__init__'], 0);

            if hasattr(module, className):
                extension = getattr(module, className)();
                # check naming convention
                expectedAlias = Container.underscore(basename);
                if expectedAlias != extension.getAlias():
                    raise LogicException(
                        'The extension alias for the default extension of a '
                        'kernel must be the underscored version of the '
                        'kernel name ("{0}" instead of "{1}")'
                        ''.format(expectedAlias, extension.getAlias())
                    );

                self._extention = extension;
            else:
                self._extention = False;

        if self._extention:
            return self._extention;

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
        self._container = None;

    def getName(self):
        if self._name is None:
            self._name = str(type(self).__name__).replace("Kernel", "");
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

        packageName = name[1:];
        if "/" in packageName:
            packageName, path = packageName.split("/", 1);

        if path.startswith("Resources") and not directory is None:
            isResource = True;
        overridePath = path[9:];
        files = [];

        if isResource:
            filename = os.path.join(
                directory,
                packageName.replace(".", os.path.sep),
                overridePath
            );
            if os.path.exists(filename):
                if first:
                    return filename;
                files.append(filename);

        if packageName == self.getName():
            rootPath = self._rootDir;
        else:
            moduleName = packageName;
            try:
                module = __import__(moduleName, {}, {}, [], 0);
            except TypeError:
                module = __import__(moduleName, {}, {}, ['__init__'], 0);

            rootPath = os.path.dirname(module.__file__);
        filename = os.path.join(rootPath, path);
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
        return os.path.join(self._rootDir, 'cache', self._environment);

    def setClassCache(self, classes):
        pass;
#        f = open(os.path.join(self.getCacheDir(), 'classes.map'), 'w');
#        f.write(pickle.dumps(classes));
#        f.close();

class FileLocator(BaseFileLocator):
    """FileLocator uses the KernelInterface to locate resources in packages.
    """
    def __init__(self, kernel, path=None, paths=[]):
        """
        """
        assert isinstance(kernel, KernelInterface);
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

class MergeExtensionConfigurationPass(BaseMergeExtensionConfigurationPass):
    """Ensures certain extensions are always loaded.
    """
    def __init__(self, extensions):
        """Constructor.

        @param extensions: list A list of extension name
        """
        assert isinstance(extensions, list);

        self.__extensions = extensions;

    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        for extension in self.__extensions:
            if not container.getExtensionConfig(extension):
                container.loadFromExtension(extension, dict());

        BaseMergeExtensionConfigurationPass.process(self, container);

class AddClassesToCachePass(CompilerPassInterface):
    """Sets the classes to compile in the cache for the container."""
    def __init__(self, kernel):
        assert isinstance(kernel, Kernel);

        self.__kernel = kernel;

    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        classes = list();
        for extension in container.getExtensions().values():
            if isinstance(extension, Extension):
                classes.extend(extension.getClassesToCompile());

        classes = Array.uniq(container.getParameterBag().resolveValue(classes));
        self.__kernel.setClassCache(classes);

@abstract
class Extension(BaseExtension):
    """Allow adding classes to the class cache."""

    def __init__(self, *args, **kwargs):
        BaseExtension.__init__(self, *args, **kwargs);
        self.__classes = list();

    def getClassesToCompile(self):
        """Gets the classes to cache.

        @return: dict A dict of classes
        """
        return self.__classes;

    def addClassesToCompile(self, classes):
        """Adds classes to the class cache.

        @param classes: list A list of classes
        """
        assert isinstance(classes, list);

        self.__classes.extend(classes);

@abstract
class ConfigurableExtension(Extension):
    def load(self, configs, container):
        """@final:"""
        self._loadInternal(self._processConfiguration(self.getConfiguration(dict(), container), configs), container);

    @abstract
    def _loadInternal(self, mergedConfig, container):
        """Configures the passed container according to the merged
        configuration.

        @param mergedConfig: dict
        @param container: ContainerBuilder
        """
        pass;

class LogicException(Exception):
    pass;

class InvalidArgumentException(LogicException):
    pass;

class RuntimeException(Exception):
    pass;
