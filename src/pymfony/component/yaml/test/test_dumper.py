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
import re;
import time;

from pymfony.component.system import Object;
from pymfony.component.system.types import OrderedDict;
from pymfony.component.system.serializer import serialize;

from pymfony.component.yaml import Parser;
from pymfony.component.yaml import Dumper;
from pymfony.component.yaml.exception import DumpException;


"""
"""

__DIR__ = os.path.dirname(os.path.abspath(__file__));

class DumperTest(unittest.TestCase):


    def setUp(self):

        self._parser = Parser();
        self._dumper = Dumper();
        self._path = __DIR__+'/Fixtures';


    def tearDown(self):

        self._parser = None;
        self._dumper = None;
        self._path = None;


    def testSpecifications(self):

        f = open(self._path+'/index.yml');
        content = f.read();
        f.close();

        files = self._parser.parse(content);
        for filename in files:
            f = open(self._path+'/'+filename+'.yml');
            yamls = f.read();
            f.close();

            # split YAMLs documents
            for yaml in re.compile('^---( %YAML\:1\.0)?', re.M).split(yamls):
                if ( not yaml) :
                    continue;


                test = self._parser.parse(yaml);

                if not isinstance(test, dict):
                    continue;

                if 'dump_skip' in test and test['dump_skip'] :
                    continue;
                elif 'todo' in test and test['todo'] :
                    # TODO
                    pass;
                else:
                    try:
                        expected = eval(test['python'].strip());

                        self.assertEqual(expected, self._parser.parse(self._dumper.dump(expected, 10)), test['test']);

                    except Exception as e:
                        raise e;

    def testInlineLevel(self):

        # inline level
        array = OrderedDict([
            ('' , 'bar'),
            ('foo' , '#bar'),
            ('foo\'bar' , dict()),
            ('bar' , [1, 'foo']),
            ('foobar' , OrderedDict([
                ('foo' , 'bar'),
                ('bar' , [1, 'foo']),
                ('foobar' , OrderedDict([
                    ('foo' , 'bar'),
                    ('bar' , [1, 'foo']),
                ])),
            ])),
        ]);

        expected = """{ '': bar, foo: '#bar', 'foo''bar': {  }, bar: [1, foo], foobar: { foo: bar, bar: [1, foo], foobar: { foo: bar, bar: [1, foo] } } }""";

        self.assertEqual(expected, self._dumper.dump(array, -10), '->dump() takes an inline level argument');
        self.assertEqual(expected, self._dumper.dump(array, 0), '->dump() takes an inline level argument');

        expected = """'': bar
foo: '#bar'
'foo''bar': {  }
bar: [1, foo]
foobar: { foo: bar, bar: [1, foo], foobar: { foo: bar, bar: [1, foo] } }
""";
        self.assertEqual(expected, self._dumper.dump(array, 1), '->dump() takes an inline level argument');

        expected = """'': bar
foo: '#bar'
'foo''bar': {  }
bar:
    - 1
    - foo
foobar:
    foo: bar
    bar: [1, foo]
    foobar: { foo: bar, bar: [1, foo] }
""";
        self.assertEqual(expected, self._dumper.dump(array, 2), '->dump() takes an inline level argument');

        expected = """'': bar
foo: '#bar'
'foo''bar': {  }
bar:
    - 1
    - foo
foobar:
    foo: bar
    bar:
        - 1
        - foo
    foobar:
        foo: bar
        bar: [1, foo]
""";
        self.assertEqual(expected, self._dumper.dump(array, 3), '->dump() takes an inline level argument');

        expected = """'': bar
foo: '#bar'
'foo''bar': {  }
bar:
    - 1
    - foo
foobar:
    foo: bar
    bar:
        - 1
        - foo
    foobar:
        foo: bar
        bar:
            - 1
            - foo
""";
        self.assertEqual(expected, self._dumper.dump(array, 4), '->dump() takes an inline level argument');
        self.assertEqual(expected, self._dumper.dump(array, 10), '->dump() takes an inline level argument');


    def testObjectSupportEnabled(self):

        dump = self._dumper.dump(OrderedDict([('foo' , A()), ('bar' , 1)]), 0, 0, False, True);

        self.assertEqual('{{ foo: !!python/object:{0}, bar: 1 }}'.format(serialize(A())), dump, '->dump() is able to dump objects');


    def testObjectSupportDisabledButNoExceptions(self):

        dump = self._dumper.dump(OrderedDict([('foo' , A()), ('bar' , 1)]));

        self.assertEqual('{ foo: null, bar: 1 }', dump, '->dump() does not dump objects when disabled');


    def testObjectSupportDisabledWithExceptions(self):
        """@expectedException: Symfony\Component\Yaml\Exception\DumpException

        """

        try:
            self._dumper.dump(OrderedDict([('foo' , A()), ('bar' , 1)]), 0, 0, True, False);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, DumpException));




class A(Object):

    a = 'foo';

if __name__ == '__main__':
    unittest.main();
