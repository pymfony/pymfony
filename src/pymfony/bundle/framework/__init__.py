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

from pymfony.component.kernel.bundle import Bundle;
from pymfony.component.dependency import ContainerBuilder;
from pymfony.bundle.framework.dependency.compiler import RegisterKernelListenersPass;
from pymfony.component.dependency.compiler import PassConfig;

class FrameworkBundle(Bundle):
    def build(self, container):
        assert isinstance(container, ContainerBuilder);
        Bundle.build(self, container);

        container.addCompilerPass(
            RegisterKernelListenersPass(),
            PassConfig.TYPE_AFTER_REMOVING
        );
