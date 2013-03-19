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

from pymfony.component.config import FileLocator;
from pymfony.component.system.exception import InvalidArgumentException

"""
"""

__DIR__ = os.path.dirname(os.path.realpath(__file__));

class FileLocatorTest(unittest.TestCase):

    def testIsAbsolutePath(self):
        """
        @dataProvider getIsAbsolutePathTests

        """
        def test(path):
            loader = FileLocator([]);
            self.assertTrue(getattr(loader, '_FileLocator__isAbsolutePath')(path), '->isAbsolutePath() returns True for an absolute path');

        for data in self.getIsAbsolutePathTests():
            test(*data);


    def getIsAbsolutePathTests(self):

        return [
            ['/foo.xml'],
            ['c:\\\\foo.xml'],
            ['c:/foo.xml'],
            ['\\server\\foo.xml'],
            ['https://server/foo.xml'],
            ['phar://server/foo.xml'],
        ];


    def testLocate(self):

        loader = FileLocator(__DIR__+'/Fixtures');

        self.assertEqual(
            __DIR__+os.path.sep+'test_file_locator.py',
            loader.locate('test_file_locator.py', __DIR__),
            '->locate() returns the absolute filename if the file exists in the given path'
        );

        self.assertEqual(
            __DIR__+'/Fixtures'+os.path.sep+'foo.xml',
            loader.locate('foo.xml', __DIR__),
            '->locate() returns the absolute filename if the file exists in one of the paths given in the constructor'
        );

        self.assertEqual(
            __DIR__+'/Fixtures'+os.path.sep+'foo.xml',
            loader.locate(__DIR__+'/Fixtures'+os.path.sep+'foo.xml', __DIR__),
            '->locate() returns the absolute filename if the file exists in one of the paths given in the constructor'
        );

        loader = FileLocator([__DIR__+'/Fixtures', __DIR__+'/Fixtures/Again']);

        self.assertEqual(
            [__DIR__+'/Fixtures'+os.path.sep+'foo.xml', __DIR__+'/Fixtures/Again'+os.path.sep+'foo.xml'],
            loader.locate('foo.xml', __DIR__, False),
            '->locate() returns an array of absolute filenames'
        );

        self.assertEqual(
            [__DIR__+'/Fixtures'+os.path.sep+'foo.xml', __DIR__+'/Fixtures/Again'+os.path.sep+'foo.xml'],
            loader.locate('foo.xml', __DIR__+'/Fixtures', False),
            '->locate() returns an array of absolute filenames'
        );

        loader = FileLocator(__DIR__+'/Fixtures/Again');

        self.assertEqual(
            [__DIR__+'/Fixtures'+os.path.sep+'foo.xml', __DIR__+'/Fixtures/Again'+os.path.sep+'foo.xml'],
            loader.locate('foo.xml', __DIR__+'/Fixtures', False),
            '->locate() returns an array of absolute filenames'
        );


    def testLocateThrowsAnExceptionIfTheFileDoesNotExists(self):
        """@expectedException InvalidArgumentException

        """

        try:
            loader = FileLocator([__DIR__+'/Fixtures']);

            loader.locate('foobar.xml', __DIR__);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));



    def testLocateThrowsAnExceptionIfTheFileDoesNotExistsInAbsolutePath(self):
        """@expectedException InvalidArgumentException

        """

        try:
            loader = FileLocator([__DIR__+'/Fixtures']);

            loader.locate(__DIR__+'/Fixtures/foobar.xml', __DIR__);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));


if __name__ == '__main__':
    unittest.main();
