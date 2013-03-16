# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import unittest;

from pymfony.component.yaml.exception import ParseException;
from pymfony.component.yaml import Inline;

from pymfony.component.system.types import OrderedDict;

"""
"""


class InlineTest(unittest.TestCase):

    def testParse(self):

        for yaml, value in self._getTestsForParse().items():
            self.assertEqual(value, Inline.parse(yaml), '::parse() converts an inline YAML to a PHP structure ({0})'.format(yaml));



    def testDump(self):

        testsForDump = self._getTestsForDump();

        for yaml, value in testsForDump.items():
            self.assertEqual(yaml, Inline.dump(value), '::dump() converts a PHP structure to an inline YAML ({0})'.format(yaml));


        for yaml, value in self._getTestsForParse().items():
            self.assertEqual(value, Inline.parse(Inline.dump(value)), 'check consistency');


        for yaml, value in testsForDump.items():
            self.assertEqual(value, Inline.parse(Inline.dump(value)), 'check consistency');



    def testDumpNumericValueWithLocale(self):

        self.assertEqual('1.2', Inline.dump(1.2));


    def testHashStringsResemblingExponentialNumericsShouldNotBeChangedToINF(self):

        value = '686e444';

        self.assertEqual(value, Inline.parse(Inline.dump(value)));


    def testParseScalarWithIncorrectlyQuotedStringShouldThrowException(self):
        """@expectedException: Symfony\Component\Yaml\Exception\ParseException

        """

        try:
            value = "'don't do somthin' like that'";
            Inline.parse(value);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ParseException));



    def testParseScalarWithIncorrectlyDoubleQuotedStringShouldThrowException(self):
        """@expectedException: Symfony\Component\Yaml\Exception\ParseException

        """

        try:
            value = '"don"t do somthin" like that"';
            Inline.parse(value);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ParseException));



    def testParseInvalidMappingKeyShouldThrowException(self):
        """@expectedException: Symfony\Component\Yaml\Exception\ParseException

        """

        try:
            value = '{ "foo " bar": "bar" }';
            Inline.parse(value);

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ParseException));




    def testParseInvalidMappingShouldThrowException(self):
        """@expectedException: Symfony\Component\Yaml\Exception\ParseException

        """
        try:
            Inline.parse('[foo] bar');

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ParseException));




    def testParseInvalidSequenceShouldThrowException(self):
        """@expectedException: Symfony\Component\Yaml\Exception\ParseException

        """

        try:
            Inline.parse('{ foo: bar } bar');

            self.fail()
        except Exception as e:
            self.assertTrue(isinstance(e, ParseException));




    def testParseScalarWithCorrectlyQuotedStringShouldReturnString(self):

        value = "'don''t do somthin'' like that'";
        expect = "don't do somthin' like that";

        self.assertEqual(expect, Inline.parseScalar(value));


    def _getTestsForParse(self):

        return {
            '' : '',
            'null' : None,
            'false' : False,
            'true' : True,
            '12' : 12,
            '-12' : -12,
            '"quoted string"' : 'quoted string',
            "'quoted string'" : 'quoted string',
            '12.30e+02' : 12.30e+02,
            '0x4D2' : 0x4D2,
            '02333' : 0o2333,
            '.Inf' : 1e10000,
            '-.Inf' : -1e10000,
            "'686e444'" : '686e444',
            '686e444' : 646e444,
            '123456789123456789123456789123456789' : 123456789123456789123456789123456789,
            '"foo\\r\\nbar"' : "foo\r\nbar",
            "'foo#bar'" : 'foo#bar',
            "'foo # bar'" : 'foo # bar',
            "'#cfcfcf'" : '#cfcfcf',
            '::form_base.html.twig' : '::form_base.html.twig',

            # FIXME: dates
#            '2007-10-30' : time.mktime(datetime.datetime(2007, 10, 30).timetuple()),
#            '2007-10-30T02:59:43Z' : time.mktime(datetime.datetime(2007, 10, 30, 2, 59, 43).timetuple()),
#            '2007-10-30 02:59:43 Z' : time.mktime(datetime.datetime(2007, 10, 30, 2, 59, 43).timetuple()),
#            '1960-10-30 02:59:43 Z' : time.mktime(datetime.datetime(1960, 10, 30, 2, 59, 43).timetuple()),
#            '1730-10-30T02:59:43Z' : time.mktime(datetime.datetime(1730, 10, 30, 2, 59, 43).timetuple()),

            '"a \\"string\\" with \'quoted strings inside\'"' : 'a "string" with \'quoted strings inside\'',
            "'a \"string\" with ''quoted strings inside'''" : 'a "string" with \'quoted strings inside\'',

            # sequences
            # urls are no key value mapping. see #3609. Valid yaml "key: value" mappings require a space after the colon
            '[foo, http://urls.are/no/mappings, false, null, 12]' : ['foo', 'http://urls.are/no/mappings', False, None, 12],
            '[  foo  ,   bar , false  ,  null     ,  12  ]' : ['foo', 'bar', False, None, 12],
            '[\'foo,bar\', \'foo bar\']' : ['foo,bar', 'foo bar'],

            # mappings
            '{foo:bar,bar:foo,false:false,null:null,integer:12}' : {'foo' : 'bar', 'bar' : 'foo', 'false' : False, 'null' : None, 'integer' : 12},
            '{ foo  : bar, bar : foo,  false  :   false,  null  :   null,  integer :  12  }' : {'foo' : 'bar', 'bar' : 'foo', 'false' : False, 'null' : None, 'integer' : 12},
            '{foo: \'bar\', bar: \'foo: bar\'}' : {'foo' : 'bar', 'bar' : 'foo: bar'},
            '{\'foo\': \'bar\', "bar": \'foo: bar\'}' : {'foo' : 'bar', 'bar' : 'foo: bar'},
            '{\'foo\'\'\': \'bar\', "bar\\"": \'foo: bar\'}' : {'foo\'' : 'bar', "bar\"" : 'foo: bar'},
            '{\'foo: \': \'bar\', "bar: ": \'foo: bar\'}' : {'foo: ' : 'bar', "bar: " : 'foo: bar'},

            # nested sequences and mappings
            '[foo, [bar, foo]]' : ['foo', ['bar', 'foo']],
            '[foo, {bar: foo}]' : ['foo', {'bar' : 'foo'}],
            '{ foo: {bar: foo} }' : {'foo' : {'bar' : 'foo'}},
            '{ foo: [bar, foo] }' : {'foo' : ['bar', 'foo']},

            '[  foo, [  bar, foo  ]  ]' : ['foo', ['bar', 'foo']],

            '[{ foo: {bar: foo} }]' : [{'foo' : {'bar' : 'foo'}}],

            '[foo, [bar, [foo, [bar, foo]], foo]]' : ['foo', ['bar', ['foo', ['bar', 'foo']], 'foo']],

            '[foo, {bar: foo, foo: [foo, {bar: foo}]}, [foo, {bar: foo}]]' : ['foo', {'bar' : 'foo', 'foo' : ['foo', {'bar' : 'foo'}]}, ['foo', {'bar' : 'foo'}]],

            '[foo, bar: { foo: bar }]' : ['foo', {'bar' : {'foo' : 'bar'}}],
            '[foo, \'@foo.baz\', { \'%foo%\': \'foo is %foo%\', bar: \'%foo%\' }, true, \'@service_container\']' : ['foo', '@foo.baz', {'%foo%' : 'foo is %foo%', 'bar' : '%foo%',}, True, '@service_container',],
        };


    def _getTestsForDump(self):

        return {
            'null' : None,
            'false' : False,
            'true' : True,
            '12' : 12,
            "'quoted string'" : 'quoted string',
            '1230.0' : 12.30e+02,
            '1234' : 0x4D2,
            '1243' : 0o2333,
            '.Inf' : 1e10000,
            '-.Inf' : -1e10000,
            "'686e444'" : '686e444',
            '.Inf' : 646e444,
            '"foo\\r\\nbar"' : "foo\r\nbar",
            "'foo#bar'" : 'foo#bar',
            "'foo # bar'" : 'foo # bar',
            "'#cfcfcf'" : '#cfcfcf',

            "'a \"string\" with ''quoted strings inside'''" : 'a "string" with \'quoted strings inside\'',

            # sequences
            '[foo, bar, false, null, 12]' : ['foo', 'bar', False, None, 12],
            '[\'foo,bar\', \'foo bar\']' : ['foo,bar', 'foo bar'],

            # mappings
            '{ foo: bar, bar: foo, \'false\': false, \'null\': null, integer: 12 }' : OrderedDict([('foo', 'bar'), ('bar', 'foo'), ('false', False), ('null', None), ('integer', 12)]),
            '{ foo: bar, bar: \'foo: bar\' }' : OrderedDict([('foo', 'bar'), ('bar' , 'foo: bar')]),

            # nested sequences and mappings
            '[foo, [bar, foo]]' : ['foo', ['bar', 'foo']],

            '[foo, [bar, [foo, [bar, foo]], foo]]' : ['foo', ['bar', ['foo', ['bar', 'foo']], 'foo']],

            '{ foo: { bar: foo } }' : {'foo' : {'bar' : 'foo'}},

            '[foo, { bar: foo }]' : ['foo', {'bar' : 'foo'}],

            '[foo, { bar: foo, foo: [foo, { bar: foo }] }, [foo, { bar: foo }]]' : ['foo', OrderedDict([('bar', 'foo'), ('foo', ['foo', {'bar' : 'foo'}])]), ['foo', {'bar' : 'foo'}]],

            '[foo, \'@foo.baz\', { \'%foo%\': \'foo is %foo%\', bar: \'%foo%\' }, true, \'@service_container\']' : ['foo', '@foo.baz', OrderedDict([('%foo%' , 'foo is %foo%'), ('bar' , '%foo%'),]), True, '@service_container',],
        };

if __name__ == '__main__':
    unittest.main();
