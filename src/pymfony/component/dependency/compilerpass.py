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

from pymfony.component.dependency.compiler import CompilerPassInterface;
from pymfony.component.dependency import ContainerBuilder;
from pymfony.component.dependency.extension import PrependExtensionInterface;

class MergeExtensionConfigurationPass(CompilerPassInterface):
    """Merges extension configs into the container builder"""
    def process(self, container):
        assert isinstance(container, ContainerBuilder);

        parameters = container.getParameterBag().all();
        definitions = container.getDefinitions();
        aliases = container.getAliases();

        for extension in container.getExtensions().values():
            if isinstance(extension, PrependExtensionInterface):
                extension.prepend(container);

        for name, extension in container.getExtensions().items():
            config = container.getExtensionConfig(name);
            if not config:
                # this extension was not called
                continue;

            config = container.getParameterBag().resolveValue(config);

            tmpContainer = ContainerBuilder(container.getParameterBag());
            tmpContainer.setResourceTracking(container.isTrackingResources());
            tmpContainer.addObjectResource(extension);
            tmpContainer.set('kernel', container.get('kernel'));

            extension.load(config, tmpContainer);

            container.merge(tmpContainer);

        container.addDefinitions(definitions);
        container.addAliases(aliases);
        container.getParameterBag().add(parameters);



class ResolveDefinitionTemplatesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class ResolveParameterPlaceHoldersPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class CheckDefinitionValidityPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class ResolveReferencesToAliasesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class ResolveInvalidReferencesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class AnalyzeServiceReferencesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class CheckCircularReferencesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class CheckReferenceValidityPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class RemovePrivateAliasesPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class RemoveAbstractDefinitionsPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class ReplaceAliasByActualDefinitionPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class RepeatedPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class InlineServiceDefinitionsPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class RemoveUnusedDefinitionsPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class CheckExceptionOnInvalidReferenceBehaviorPass():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
class LoggingFormatter():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);

class ServiceReferenceGraph():
    # TODO: class
    def __init__(self):
        raise NotImplementedError(self);
