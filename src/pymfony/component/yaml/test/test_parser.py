# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest
import re
from os.path import dirname

from pymfony.component.system import Object
from pymfony.component.system.types import OrderedDict
from pymfony.component.system.exception import StandardException

from pymfony.component.yaml.exception import ParseException
from pymfony.component.yaml import Parser
from pymfony.component.yaml import Yaml

"""
"""


class ParserTest(unittest.TestCase):

    def setUp(self):

        self._parser = Parser();


    def tearDown(self):

        self._parser = None;


    def testSpecifications(self):
        """@dataProvider: getDataFormSpecifications:

        """

        def test(filename, expected, yaml, comment):
            self.assertEqual(expected, self._parser.parse(yaml), comment);

        for data in self.getDataFormSpecifications():
            test(*data);


    def getDataFormSpecifications(self):

        parser = Parser();
        path = dirname(__file__)+'/Fixtures';

        tests = list();
        f = open(path+'/index.yml');
        content = f.read();
        f.close();
        files = parser.parse(content);
        for filename in files:
            f = open(path+'/'+filename+'.yml');
            yamls = f.read();
            f.close();

            # split YAMLs documents
            for yaml in re.split('^---( %YAML\:1\.0)?', yamls, flags=re.M):
                if ( not yaml) :
                    continue;


                test = parser.parse(yaml);
                if 'todo' in test and test['todo'] :
                    # TODO
                    pass;
                else:
                    expected = eval(test['python'].strip());

                    tests.append([file, expected, test['yaml'], test['test']]);




        return tests;

    def __strpbrk(self, haystack, char_list):
        try:
            pos = next(i for i,x in enumerate(haystack) if x in char_list)
            return haystack[pos:]
        except:
            return None

    def testTabsInYaml(self):

        # test tabs in YAML
        yamls = [
            "foo:\n\tbar",
            "foo:\n \tbar",
            "foo:\n\t bar",
            "foo:\n \t bar",
        ];

        for yaml in yamls:
            try:
                content = self._parser.parse(yaml);

                self.fail('YAML files must not contain tabs');
            except Exception as e:
                self.assertTrue(isinstance(e, StandardException), 'YAML files must not contain tabs');
                self.assertEqual('A YAML file cannot contain tabs as indentation at line 2 (near "'+self.__strpbrk(yaml, "\t")+'").', e.getMessage(), 'YAML files must not contain tabs');




    def testEndOfTheDocumentMarker(self):

        yaml = """--- %YAML:1.0
foo
...""";

        self.assertEqual('foo', self._parser.parse(yaml));


    def getBlockChompingTests(self):

        tests = dict();

        yaml = """
foo: |-
    one
    two

bar: |-
    one
    two
""";
        expected = OrderedDict([
            ('foo' , "one\ntwo"),
            ('bar' , "one\ntwo"),
        ]);
        tests['Literal block chomping strip with trailing newline'] = [expected, yaml];

        yaml = """
foo: |-
    one
    two
bar: |-
    one
    two
""";
        expected = OrderedDict([
            ('foo' , "one\ntwo"),
            ('bar' , "one\ntwo"),
        ]);
        tests['Literal block chomping strip without trailing newline'] = [expected, yaml];

        yaml = """
foo: |
    one
    two

bar: |
    one
    two
""";
        expected = OrderedDict([
            ('foo' , "one\ntwo\n"),
            ('bar' , "one\ntwo\n"),
        ]);
        tests['Literal block chomping clip with trailing newline'] = [expected, yaml];

        yaml = """
foo: |
    one
    two
bar: |
    one
    two""";
        expected = OrderedDict([
            ('foo' , "one\ntwo\n"),
            ('bar' , "one\ntwo\n"),
        ]);
        tests['Literal block chomping clip without trailing newline'] = [expected, yaml];

        yaml = """
foo: |+
    one
    two

bar: |+
    one
    two
""";
        expected = OrderedDict([
            ('foo' , "one\ntwo\n\n"),
            ('bar' , "one\ntwo\n\n"),
        ]);
        tests['Literal block chomping keep with trailing newline'] = [expected, yaml];

        yaml = """
foo: |+
    one
    two
bar: |+
    one
    two""";
        expected = OrderedDict([
            ('foo' , "one\ntwo\n"),
            ('bar' , "one\ntwo\n"),
        ]);
        tests['Literal block chomping keep without trailing newline'] = [expected, yaml];

        yaml = """
foo: >-
    one
    two

bar: >-
    one
    two
""";
        expected = OrderedDict([
            ('foo' , "one two"),
            ('bar' , "one two"),
        ]);
        tests['Folded block chomping strip with trailing newline'] = [expected, yaml];

        yaml = """
foo: >-
    one
    two
bar: >-
    one
    two""";
        expected = OrderedDict([
            ('foo' , "one two"),
            ('bar' , "one two"),
        ]);
        tests['Folded block chomping strip without trailing newline'] = [expected, yaml];

        yaml = """
foo: >
    one
    two

bar: >
    one
    two
""";
        expected = OrderedDict([
            ('foo' , "one two\n"),
            ('bar' , "one two\n"),
        ]);
        tests['Folded block chomping clip with trailing newline'] = [expected, yaml];

        yaml = """
foo: >
    one
    two
bar: >
    one
    two""";
        expected = OrderedDict([
            ('foo' , "one two\n"),
            ('bar' , "one two\n"),
        ]);
        tests['Folded block chomping clip without trailing newline'] = [expected, yaml];

        yaml = """
foo: >+
    one
    two

bar: >+
    one
    two
""";
        expected = OrderedDict([
            ('foo' , "one two\n\n"),
            ('bar' , "one two\n\n"),
        ]);
        tests['Folded block chomping keep with trailing newline'] = [expected, yaml];

        yaml = """
foo: >+
    one
    two
bar: >+
    one
    two""";
        expected = OrderedDict([
            ('foo' , "one two\n"),
            ('bar' , "one two\n"),
        ]);
        tests['Folded block chomping keep without trailing newline'] = [expected, yaml];

        return tests;


    def testBlockChomping(self):
        """@dataProvider: getBlockChompingTests

        """

        def test(expected, yaml):
            self.assertEqual(expected, self._parser.parse(yaml));
 
        for data in self.getBlockChompingTests().values():
            test(*data);



    def testObjectSupportEnabled(self):

        inputv = """
foo: !!python/object:O:30:"Symfony\Component\Yaml\Tests\B":1:s:1:"b";s:3:"foo";
bar: 1
""";
        self.assertEqual(OrderedDict([('foo' , B()), ('bar' , 1)]), self._parser.parse(inputv, False, True), '->parse() is able to parse objects');


    def testObjectSupportDisabledButNoExceptions(self):

        inputv = """
foo: !!python/object:O:30:"Symfony\Tests\Component\Yaml\B":1:s:1:"b";s:3:"foo";
bar: 1
""";

        self.assertEqual(OrderedDict([('foo' , None), ('bar' , 1)]), self._parser.parse(inputv), '->parse() does not parse objects');


    def testObjectsSupportDisabledWithExceptions(self):
        """@expectedException: Symfony\Component\Yaml\Exception\ParseException

        """

        try:
            self._parser.parse('foo: !!python/object:O:30:"Symfony\Tests\Component\Yaml\B":1:s:1:"b";s:3:"foo";', True, False);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ParseException));




    def testNonUtf8Exception(self):

        yamls = [
            "foo: 'äöüß'".encode("ISO-8859-1"),
            "euro: '€'".encode("ISO-8859-15"),
            "cp1252: '©ÉÇáñ'".encode("CP1252"),
        ];

        for yaml in yamls:
            try:
                self._parser.parse(yaml);

                self.fail('charsets other than UTF-8 are rejected.');
            except Exception as e:
                self.assertTrue(isinstance(e, ParseException), 'charsets other than UTF-8 are rejected.');




    def testUnindentedCollectionException(self):
        """@expectedException: Symfony\Component\Yaml\Exception\ParseException


        """

        yaml = """

collection:
-item1
-item2
-item3

""";

        try:
            self._parser.parse(yaml);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ParseException));


    def testSequenceInAMapping(self):
        """@expectedException: Symfony\Component\Yaml\Exception\ParseException

        """

        try:
            Yaml.parse("""
yaml:
  hash: me
  - array stuff
"""
        );

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ParseException));



    def testMappingInASequence(self):
        """@expectedException: Symfony\Component\Yaml\Exception\ParseException

        """

        try:

            Yaml.parse("""
yaml:
  - array stuff
  hash: me
"""
        );

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ParseException));



class B(Object):

    def __init__(self):
        self.b = 'foo';

if __name__ == '__main__':
    unittest.main();
