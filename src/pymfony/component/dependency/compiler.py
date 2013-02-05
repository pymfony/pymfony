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

from pymfony.component.system import (
    Object,
    interface,
);

from pymfony.component.dependency.exception import InvalidArgumentException;

@interface
class CompilerPassInterface(Object):
    """Interface that must be implemented by compilation passes
    """
    def process(self, container):
        """You can modify the container here before it is dumped to PHP code.

        @param container: ContainerBuilder
        """
        pass;


class PassConfig(Object):
    """Compiler Pass Configuration

    This class has a default configuration embedded.
    """
    TYPE_BEFORE_OPTIMIZATION = 'BeforeOptimization';
    TYPE_AFTER_REMOVING = 'AfterRemoving'

    def __init__(self):
        self.__mergePass = None;

        self.__beforeOptimizationPasses = list();
        self.__afterRemovingPasses = list();

    def getPasses(self):
        """Returns all passes in order to be processed.

        @return: list An list of all passes to process
        """

        passes = list();
        if self.__mergePass:
            passes.append(self.__mergePass);
        passes.extend(self.__beforeOptimizationPasses);
        passes.extend(self.__afterRemovingPasses);

        return passes;

    def addPass(self, cPass, cType=TYPE_BEFORE_OPTIMIZATION):
        """Adds a pass.

        @param cPass: CompilerPassInterface A Compiler pass
        @param cType: string The pass type

        @raise InvalidArgumentException: when a pass type doesn't exist
        """
        assert isinstance(cPass, CompilerPassInterface);

        getPropertyName = "get{0}Passes".format(cType);
        setPropertyName = "set{0}Passes".format(cType);

        if not hasattr(self, getPropertyName):
            raise InvalidArgumentException(
                'Invalid type "{0}".'.format(cType)
            );

        passes = getattr(self, getPropertyName)();
        passes.append(cPass);
        getattr(self, setPropertyName)(passes);

    def getMergePass(self):
        """Gets the Merge Pass.

        @return: CompilerPassInterface A merge pass
        """
        return self.__mergePass;

    def setMergePass(self, mergePass):
        """Sets the Merge Pass.

        @param mergePass: CompilerPassInterface A merge pass
        """
        assert isinstance(mergePass, CompilerPassInterface);

        self.__mergePass = mergePass;

    def getBeforeOptimizationPasses(self):
        """
        @return: list
        """
        return self.__beforeOptimizationPasses;

    def setBeforeOptimizationPasses(self, passes):
        """
        @param passes: list
        """
        self.__beforeOptimizationPasses = passes;

    def getAfterRemovingPasses(self):
        """
        @return: list
        """
        return self.__afterRemovingPasses;

    def setAfterRemovingPasses(self, passes):
        """
        @param passes: list
        """
        self.__afterRemovingPasses = passes;

class Compiler(Object):
    """This class is used to remove circular dependencies between individual
    passes.
    """
    def __init__(self):
        """Constructor.
        """
        self.__passConfig = PassConfig();

    def getPassConfig(self):
        """Returns the PassConfig.

        @return: PassConfig The PassConfig instance
        """
        return self.__passConfig;

    def addPass(self, cPass, cType=PassConfig.TYPE_BEFORE_OPTIMIZATION):
        """Adds a pass to the PassConfig.

        @param cPass: CompilerPassInterface A compiler pass
        @param cType: string The type of the pass
        """
        assert isinstance(cPass, CompilerPassInterface);

        self.__passConfig.addPass(cPass, cType);

    def compile(self, container):
        """Run the Compiler and process all Passes.

        @param container: ContainerBuilder
        """
        for cPass in self.__passConfig.getPasses():
            cPass.process(container);
