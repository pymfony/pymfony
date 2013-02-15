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
from pymfony.component.system import ReflectionObject;
from pymfony.component.system.types import OrderedDict;

from pymfony.component.dependency.exception import InvalidArgumentException;

from pymfony.component.dependency.definition import Alias
from pymfony.component.dependency.definition import Definition

@interface
class CompilerPassInterface(Object):
    """Interface that must be implemented by compilation passes
    """
    def process(self, container):
        """You can modify the container here before it is dumped to PHP code.

        @param container: ContainerBuilder
        """
        pass;


@interface
class RepeatablePassInterface(CompilerPassInterface):
    """Interface that must be implemented by passes that are run as part of an
 * RepeatedPass.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def setRepeatedPass(self, repeatedPass):
        """Sets the RepeatedPass interface.
     *
     * @param RepeatedPass repeatedPass

        """
        assert isinstance(repeatedPass, RepeatedPass);


class PassConfig(Object):
    """Compiler Pass Configuration

    This class has(, a default configuration embedded.):

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    @api

    """
    TYPE_AFTER_REMOVING = 'AfterRemoving';
    TYPE_BEFORE_OPTIMIZATION = 'BeforeOptimization';
    TYPE_BEFORE_REMOVING = 'BeforeRemoving';
    TYPE_OPTIMIZE = 'Optimization';
    TYPE_REMOVE = 'Removing';

    def __init__(self):
        """Constructor.

        """
        self.__mergePass = None;

        self.__beforeOptimizationPasses = list();
        self.__afterRemovingPasses = list();
        self.__optimizationPasses = list();
        self.__beforeRemovingPasses = list();
        self.__optimizationPasses = list();
        self.__removingPasses = list();

    def getPasses(self):
        """Returns all passes in order to be processed.

        @return: list An array of all passes to process

        @api

        """

        passes = list();
        if self.__mergePass:
            passes.append(self.__mergePass);
        passes.extend(self.__beforeOptimizationPasses);
        passes.extend(self.__optimizationPasses);
        passes.extend(self.__afterRemovingPasses);
        passes.extend(self.__removingPasses);
        passes.extend(self.__afterRemovingPasses);

        return passes;

    def addPass(self, cPass, cType=TYPE_BEFORE_OPTIMIZATION):
        """Adds a pass.

        @param: CompilerPassInterface pass A Compiler pass
        @param string                type The pass type

        @raise InvalidArgumentException when a pass type doesn't exist

        @api

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

    def getAfterRemovingPasses(self):
        """Gets all passes for the AfterRemoving pass.

        @return: list An array of passes

        @api

        """

        return self.__afterRemovingPasses;


    def getBeforeOptimizationPasses(self):
        """Gets all passes for the BeforeOptimization pass.

        @return: list An array of passes

        @api

        """

        return self.__beforeOptimizationPasses;


    def getBeforeRemovingPasses(self):
        """Gets all passes for the BeforeRemoving pass.

        @return: list An array of passes

        @api

        """

        return self.__beforeRemovingPasses;


    def getOptimizationPasses(self):
        """Gets all passes for the Optimization pass.

        @return: list An array of passes

        @api

        """

        return self.__optimizationPasses;


    def getRemovingPasses(self):
        """Gets all passes for the Removing pass.

        @return: list An array of passes

        @api

        """

        return self.__removingPasses;


    def getMergePass(self):
        """Gets all passes for the Merge pass.

        @return: CompilerPassInterface A merge pass # FIXED

        @api

        """

        return self.__mergePass;


    def setMergePass(self, mergePass):
        """Sets the Merge Pass.

        @param: CompilerPassInterface cPass The merge pass

        @api

        """
        assert isinstance(mergePass, CompilerPassInterface);

        self.__mergePass = mergePass;

    def setAfterRemovingPasses(self, passes):
        """Sets the AfterRemoving passes.

        @param: list passes An array of passes

        @api

        """
        assert isinstance(passes, list);

        self.__afterRemovingPasses = passes;


    def setBeforeOptimizationPasses(self, passes):
        """Sets the BeforeOptimization passes.

        @param: list passes An array of passes

        @api

        """
        assert isinstance(passes, list);

        self.__beforeOptimizationPasses = passes;


    def setBeforeRemovingPasses(self, passes):
        """Sets the BeforeRemoving passes.

        @param: list passes An array of passes

        @api

        """
        assert isinstance(passes, list);

        self.__beforeRemovingPasses = passes;


    def setOptimizationPasses(self, passes):
        """Sets the Optimization passes.

        @param: array passes An array of passes

        @api

        """
        assert isinstance(passes, list);

        self.__optimizationPasses = passes;


    def setRemovingPasses(self, passes):
        """Sets the Removing passes.

        @param: array passes An array of passes

        @api

        """
        assert isinstance(passes, list);

        self.__removingPasses = passes;




class RepeatedPass(CompilerPassInterface):
    """A pass that might be run repeatedly.
 *
 * @author Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self, passes):
        """Constructor.
     *
     * @param RepeatablePassInterface[] passes An array of RepeatablePassInterface objects
     *
     * @raise InvalidArgumentException when the passes don't implement RepeatablePassInterface

        """
        assert isinstance(passes, list);

        self.__repeat = False;
        """@var Boolean

        """

        self.__passes = None;
        """@var RepeatablePassInterface[]

        """

        for cPass in passes:
            if ( not isinstance(cPass, RepeatablePassInterface)) :
                raise InvalidArgumentException(
                    'passes must be an array of RepeatablePassInterface.'
                );


            cPass.setRepeatedPass(self);


        self.__passes = passes;


    def process(self, container):
        """Process the repeatable passes that run more than once.
     *
     * @param ContainerBuilder container

        """

        self.__repeat = False;

        for cPass in self.__passes:
            cPass.process(container);


        if (self.__repeat) :
            self.process(container);



    def setRepeat(self):
        """Sets if the pass should repeat:

        """

        self.__repeat = True;


    def getPasses(self):
        """Returns the passes
     *
     * @return RepeatablePassInterface[] An array of RepeatablePassInterface objects

        """

        return self.__passes;


class Compiler(Object):
    """This class is(, used to remove circular dependencies between individual passes.):

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    @api

    """
    def __init__(self):
        """Constructor.

        """
        self.__passConfig = PassConfig();
        self.__log = list();
        self.__loggingFormatter = LoggingFormatter();
        self.__serviceReferenceGraph = ServiceReferenceGraph();


    def getPassConfig(self):
        """Returns the PassConfig.

        @return: PassConfig The PassConfig instance

        @api

        """

        return self.__passConfig;

    def getServiceReferenceGraph(self):
        """Returns the ServiceReferenceGraph.

        @return: ServiceReferenceGraph The ServiceReferenceGraph instance

        @api

        """

        return self.__serviceReferenceGraph;

    def getLoggingFormatter(self):
        """Returns the logging formatter which can be used by compilation passes.

        @return: LoggingFormatter

        """

        return self.__loggingFormatter;

    def addPass(self, cPass, cType=PassConfig.TYPE_BEFORE_OPTIMIZATION):
        """Adds a pass to the PassConfig.

        @param: CompilerPassInterface pass A compiler pass
        @param string                type The type of the pass

        @api

        """
        assert isinstance(cPass, CompilerPassInterface);

        self.__passConfig.addPass(cPass, cType);

    def addLogMessage(self, string):
        """Adds a log message.

        @param: string string The log message

        """

        self.__log.append(string);

    def getLog(self):
        """Returns the log.

        @return: list Log array

        """

        return self.__log;

    def compile(self, container):
        """Run the Compiler and process all Passes.

        @param: ContainerBuilder container

        @api

        """
        for cPass in self.__passConfig.getPasses():
            cPass.process(container);



class LoggingFormatter(Object):
    """Used to format logging messages during the compilation.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def formatRemoveService(self, cpass, identifier, reason):
        assert isinstance(cpass, CompilerPassInterface);

        return self.format(cpass, 'Removed service "{0}"; reason: {1}'.format(identifier, reason));


    def formatInlineService(self, cpass, identifier, target):
        assert isinstance(cpass, CompilerPassInterface);

        return self.format(cpass, 'Inlined service "{0}" to "{1}".'.format(identifier, target));


    def formatUpdateReference(self, cpass, serviceId, oldDestId, newDestId):
        assert isinstance(cpass, CompilerPassInterface);

        return self.format(cpass, 'Changed reference of service "{0}" previously pointing to "{1}" to "{2}".'.format(serviceId, oldDestId, newDestId));


    def formatResolveInheritance(self, cpass, childId, parentId):
        assert isinstance(cpass, CompilerPassInterface);

        return self.format(cpass, 'Resolving inheritance for "{0}" (parent: {1}).'.format(childId, parentId));


    def format(self, cpass, message):
        assert isinstance(cpass, CompilerPassInterface);

        return '{0}: {1}'.format(ReflectionObject(cpass).getName(), message);




class ServiceReferenceGraph(Object):
    """This is a directed graph of your services.

    This information can be used by your compiler passes instead of collecting
    it themselves which improves performance quite a lot.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """



    def __init__(self):
        """Constructor.

        """

        self.__nodes = None;
        self.clear();


    def hasNode(self, identifier):
        """Checks if the graph has a specific node.:

        @param: string id Id to check

        @return Boolean

        """

        return identifier in self.__nodes;


    def getNode(self, identifier):
        """Gets a node by identifier.:

        @param: string id The id to retrieve

        @return ServiceReferenceGraphNode The node matching the supplied identifier:

        @raise InvalidArgumentException if no node matches the supplied identifier:

        """

        if identifier not in self.__nodes :
            raise InvalidArgumentException(
                'There is no node with id "{0}".'.format(identifier)
            );


        return self.__nodes[identifier];


    def getNodes(self):
        """Returns all nodes.

        @return: ServiceReferenceGraphNode[] An array of all ServiceReferenceGraphNode objects

        """

        return self.__nodes;


    def clear(self):
        """Clears all nodes.

        """

        self.__nodes = OrderedDict();


    def connect(self, sourceId, sourceValue, destId, destValue = None, reference = None):
        """Connects 2 nodes together in the Graph.

        @param: string sourceId
        @param string sourceValue
        @param string destId
        @param string destValue
        @param string reference

        """

        sourceNode = self.__createNode(sourceId, sourceValue);
        destNode = self.__createNode(destId, destValue);
        edge = ServiceReferenceGraphEdge(sourceNode, destNode, reference);

        sourceNode.addOutEdge(edge);
        destNode.addInEdge(edge);


    def __createNode(self, identifier, value):
        """Creates a graph node.

        @param: string id
        @param string value

        @return ServiceReferenceGraphNode

        """

        if identifier in self.__nodes and self.__nodes[identifier].getValue() == value :
            return self.__nodes[identifier];

        self.__nodes[identifier] = ServiceReferenceGraphNode(identifier, value)
        return self.__nodes[identifier];




class ServiceReferenceGraphEdge(Object):
    """Represents an edge in your service graph.

    Value is typically a reference.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """

    def __init__(self, sourceNode, destNode, value = None):
        """Constructor.

        @param: ServiceReferenceGraphNode sourceNode
        @param ServiceReferenceGraphNode destNode
        @param string                    value

        """
        assert isinstance(destNode, ServiceReferenceGraphNode);
        assert isinstance(sourceNode, ServiceReferenceGraphNode);

        self.__sourceNode = None;
        self.__destNode = None;
        self.__value = None;
        self.__sourceNode = sourceNode;
        self.__destNode = destNode;
        self.__value = value;


    def getValue(self):
        """Returns the value of the edge

        @return: ServiceReferenceGraphNode

        """

        return self.__value;


    def getSourceNode(self):
        """Returns the source node

        @return: ServiceReferenceGraphNode

        """

        return self.__sourceNode;


    def getDestNode(self):
        """Returns the destination node

        @return: ServiceReferenceGraphNode

        """

        return self.__destNode;




class ServiceReferenceGraphNode(Object):
    """Represents a node in your service graph.

    Value is typically a definition, or an alias.

    @author: Johannes M. Schmitt <schmittjoh@gmail.com>

    """


    def __init__(self, identifier, value):
        """Constructor.

        @param: string id    The node identifier:
        @param mixed  value The node value

        """
        self.__id = None;
        self.__inEdges = None;
        self.__outEdges = None;
        self.__value = None;

        self.__id = identifier;
        self.__value = value;
        self.__inEdges = list();
        self.__outEdges = list();


    def addInEdge(self, edge):
        """Adds an in edge to this node.

        @param: ServiceReferenceGraphEdge edge

        """
        assert isinstance(edge, ServiceReferenceGraphEdge);

        self.__inEdges.append(edge);


    def addOutEdge(self, edge):
        """Adds an out edge to this node.

        @param: ServiceReferenceGraphEdge edge

        """
        assert isinstance(edge, ServiceReferenceGraphEdge);

        self.__outEdges.append(edge);


    def isAlias(self):
        """Checks if the value of this node is an Alias.:

        @return: Boolean True if the value is an Alias instance:

        """

        return isinstance(self.__value, Alias);


    def isDefinition(self):
        """Checks if the value of this node is a Definition.:

        @return: Boolean True if the value is a Definition instance:

        """

        return isinstance(self.__value, Definition);


    def getId(self):
        """Returns the identifier.:

        @return: string

        """

        return self.__id;


    def getInEdges(self):
        """Returns the in edges.

        @return: list The in ServiceReferenceGraphEdge array

        """

        return self.__inEdges;


    def getOutEdges(self):
        """Returns the out edges.

        @return: list The out ServiceReferenceGraphEdge array

        """

        return self.__outEdges;


    def getValue(self):
        """Returns the value of this Node

        @return: mixed The value

        """

        return self.__value;


