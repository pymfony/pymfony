# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.system import Object;

from pymfony.component.event_dispatcher import GenericEvent;
from pymfony.component.system.exception import InvalidArgumentException

"""
"""


class GenericEventTest(unittest.TestCase):
    """Test class for Event.

    """

    def setUp(self):
        """Prepares the environment before running a test.

        """

        self._subject = Object();
        self._event = GenericEvent(self._subject, {'name' : 'Event'});


    def tearDown(self):
        """Cleans up the environment after running a test.

        """

        self._subject = None;
        self._event = None;



    def testConstruct(self):

        event = GenericEvent(self._subject, {'name' : 'Event'});
        self.assertEqual(event._Event__propagationStopped, self._event._Event__propagationStopped);
        self.assertEqual(event._Event__dispatcher, self._event._Event__dispatcher);
        self.assertEqual(event._Event__name, self._event._Event__name);
        self.assertEqual(event._arguments, self._event._arguments);
        self.assertEqual(event._subject, self._event._subject);



    def testGetArguments(self):
        """Tests Event.getArgs()

        """

        # test getting all
        self.assertEqual({'name' : 'Event'}, self._event.getArguments());


    def testSetArguments(self):

        result = self._event.setArguments({'foo' : 'bar'});
        self.assertEqual({'foo' : 'bar'}, self._event._arguments);
        self.assertEqual(self._event, result);


    def testSetArgument(self):

        result = self._event.setArgument('foo2', 'bar2');
        self.assertEqual({'name' : 'Event', 'foo2' : 'bar2'}, self._event._arguments);
        self.assertEqual(self._event, result);


    def testGetArgument(self):

        # test getting key
        self.assertEqual('Event', self._event.getArgument('name'));


    def testGetArgException(self):
        """@expectedException InvalidArgumentException

        """

        try:
            self._event.getArgument('nameNotExist');
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));


    def testOffsetGet(self):

        # test getting key
        self.assertEqual('Event', self._event['name']);

        # test getting invalid arg
        try:
            self.assertFalse(self._event['nameNotExist']);
            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, InvalidArgumentException));


    def testOffsetSet(self):

        self._event['foo2'] = 'bar2';
        self.assertEqual({'name' : 'Event', 'foo2' : 'bar2'}, self._event._arguments);


    def testOffsetUnset(self):

        del self._event['name'];
        self.assertEqual({}, self._event._arguments);


    def testOffsetIsset(self):

        self.assertTrue('name' in self._event);
        self.assertFalse('nameNotExist' in self._event);


    def testHasArgument(self):

        self.assertTrue(self._event.hasArgument('name'));
        self.assertFalse(self._event.hasArgument('nameNotExist'));


    def testGetSubject(self):

        self.assertEqual(self._subject, self._event.getSubject());


    def testHasIterator(self):

        data = dict();
        for key in self._event:
            value = self._event[key];
            data[key] = value;

        self.assertEqual({'name' : 'Event'}, data);

if __name__ == '__main__':
    unittest.main();
