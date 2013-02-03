#!/usr/bin/python
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

import unittest
import os.path as op;

from pymfony.component.kernel import Kernel;
from pymfony.component.config import FileLocator;
from pymfony.bundle.framework import FrameworkBundle;


class AppKernel(Kernel):
    def registerBundles(self):
        return [
            FrameworkBundle(),
        ];

    def registerContainerConfiguration(self, loader):
        path = self.locateResource("@/Resources/config/config_{0}.ini".format(
            self.getEnvironment()
        ));
        loader.load(path);




class Test(unittest.TestCase):
    def setUp(self):
        self._kernel = AppKernel("test", True);
        self._kernel.boot();
        self.container = self._kernel.getContainer();


    def tearDown(self):
        self._kernel.shutdown();


    def testLocateResource(self):
        currdir = op.realpath(op.dirname(__file__));
        formater = lambda v: op.normpath(op.normcase(op.realpath(v)));
        values = {
            "@/Resources/config/config.ini": op.join(
                currdir, "Resources/config/config.ini"
            ),
            "Resources/config": op.join(currdir, "Resources/config"),
        };

        locator = self.container.get('file_locator');
        self.assertTrue(isinstance(locator, FileLocator), repr(locator));

        for value, expected in values.items():
            result = locator.locate(value, currdir);
            self.assertEqual(formater(result), formater(expected));


    def testExtensionConfig(self):
        self.assertEqual(
            self.container.getParameter('framework.default_locale'),
            'en'
        );
        self.assertEqual(
            self.container.getParameter('locale'),
            'en'
        );


if __name__ == "__main__":
    unittest.main();
