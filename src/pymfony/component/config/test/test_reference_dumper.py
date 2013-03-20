# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;
import os;

from pymfony.component.system import SourceFileLoader;

from pymfony.component.config.definition import ReferenceDumper;

"""
"""

__DIR__ = os.path.dirname(os.path.realpath(__file__));

class ReferenceDumperTest(unittest.TestCase):

    def testDumper(self):

        path = __DIR__+'/Fixtures/Configuration/example_configuration.py';

        configuration = SourceFileLoader.load(path).ExampleConfiguration();

        dumper = ReferenceDumper();
        self.assertEqual(self.__getConfigurationAsString(), dumper.dump(configuration));


    def __getConfigurationAsString(self):

        return """root:
    boolean:              true
    scalar_empty:         ~
    scalar_null:          ~
    scalar_true:          true
    scalar_false:         false
    scalar_default:       default
    scalar_array_empty:   []
    scalar_array_defaults:

        # Defaults:
        - elem1
        - elem2

    # some info
    array:
        child1:               ~
        child2:               ~

        # this is a long
        # multi-line info text
        # which should be indented
        child3:               ~ # Example: example setting
    array_prototype:
        parameters:

            # Prototype
            name:
                value:                ~ # Required
""";

if __name__ == '__main__':
    unittest.main()
