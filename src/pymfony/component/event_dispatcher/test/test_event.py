# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.event_dispatcher import Event;
from pymfony.component.event_dispatcher import EventDispatcher;

"""
"""

class EventTest(unittest.TestCase):
    """Test class for Event.

    """

    def setUp(self):
        """Sets up the fixture, for example, opens a network connection.
        This method is called before a test is executed.

        """

        self._event = Event();
        self._dispatcher = EventDispatcher();


    def tearDown(self):
        """Tears down the fixture, for example, closes a network connection.
        This method is called after a test is executed.

        """

        self._event = None;
        self._eventDispatcher = None;


    def testIsPropagationStopped(self):

        self.assertFalse(self._event.isPropagationStopped());


    def testStopPropagationAndIsPropagationStopped(self):

        self._event.stopPropagation();
        self.assertTrue(self._event.isPropagationStopped());


    def testSetDispatcher(self):

        self._event.setDispatcher(self._dispatcher);
        self.assertEqual(self._dispatcher, self._event.getDispatcher());


    def testGetDispatcher(self):

        self.assertTrue(None is self._event.getDispatcher());


    def testGetName(self):

        self.assertTrue(None is self._event.getName());


    def testSetName(self):

        self._event.setName('foo');
        self.assertEqual('foo', self._event.getName());


if __name__ == '__main__':
    unittest.main();
