# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import math;
import time;
import re;
import os;
from struct import pack

from pymfony.component.system import Object
from pymfony.component.system.types import String
from pymfony.component.system.types import Convert
from pymfony.component.system.types import OrderedDict
from pymfony.component.system.exception import InvalidArgumentException
from pymfony.component.system.serialiser import serialize
from pymfony.component.system.serialiser import unserialize

from pymfony.component.yaml.exception import ParseException
from pymfony.component.yaml.exception import RuntimeException
from pymfony.component.yaml.exception import DumpException

"""
"""


class Ref(Object):
    def __init__(self, i = 0):
        self.__i = i;

    def __str__(self):
        return str(self.__i);

    def get(self):
        return self.__i;

    def set(self, v):
        self.__i = v;

    def add(self, y):
        self.__i += y;

    def sub(self, y):
        self.__i -= y;


class Parser(Object):
    """Parser parses YAML strings to convert them to PHP arrays.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    def __init__(self, offset = 0):
        """Constructor

        @param: integer offset The offset of YAML document (used for line numbers in error messages)

        """

        self.__offset         = 0;
        self.__lines          = list();
        self.__currentLineNb  = -1;
        self.__currentLine    = '';
        self.__refs           = dict();


        self.__offset = offset;

    def __mb_detect_encoding(self, text, encoding_list=['ascii']):
        '''Return first matched encoding in encoding_list, otherwise return None.
        See [url]http://docs.python.org/2/howto/unicode.html#the-unicode-type[/url] for more info.
        See [url]http://docs.python.org/2/library/codecs.html#standard-encodings[/url] for encodings.'''
        for best_enc in encoding_list:
            try:
                text.encode(encoding=best_enc, errors='strict')
            except:
                best_enc = None
            else:
                break
        return best_enc

    def parse(self, value, exceptionOnInvalidType = False, objectSupport = False):
        """Parses a YAML string to a PHP value.

        @param: string  value                  A YAML string
        @param Boolean exceptionOnInvalidType True if an exception must be thrown on invalid types (a PHP resource or object), False otherwise:
        @param Boolean objectSupport          True if object support is enabled, False otherwise:

        @return mixed  A PHP value

        @raise ParseException If the YAML is not valid

        """
        self.__currentLineNb = -1;
        self.__currentLine = '';
        self.__lines = self.__cleanup(value).split("\n");

        if not self.__mb_detect_encoding(value, ['UTF-8']) :
            raise ParseException('The YAML value does not appear to be valid UTF-8.');


#        if (function_exists('mb_internal_encoding') and ((int) ini_get('mbstring.func_overload')) & 2) :
#            mbEncoding = mb_internal_encoding();
#            mb_internal_encoding('UTF-8');


        context = None;
        data = None;
        while (self.__moveToNextLine()):
            if (self.__isCurrentLineEmpty()) :
                continue;


            # tab?
            if ("\t" == self.__currentLine[0]) :
                raise ParseException('A YAML file cannot contain tabs as indentation.', self.__getRealCurrentLineNb() + 1, self.__currentLine);


            isRef = isInPlace = isProcessed = False;
            match = re.match('^\-((?P<leadspaces>\s+)(?P<value>.+?))?\s*$', self.__currentLine, flags=re.U);

            if match :
                values = {
                    0: match.group(0),
                    1: match.group(1),
                    'leadspaces': match.group('leadspaces'),
                    'value': match.group('value'),
                };
                if (context and 'mapping' == context) :
                    raise ParseException('You cannot define a sequence item when in a mapping');

                context = 'sequence';
                if not data:
                    data = list();

                if values['value']:
                    matches = re.match('^&(?P<ref>[^ ]+) *(?P<value>.*)', values['value'], re.U);
                    if matches:
                        isRef = matches.group('ref');
                        values['value'] = matches.group('value');


                # array
                if not values['value'] or '' == values['value'].strip(' ') or values['value'].lstrip(' ').startswith('#') :
                    c = self.__getRealCurrentLineNb() + 1;
                    parser = Parser(c);
                    parser.__refs = self.__refs;
                    data.append(parser.parse(self.__getNextEmbedBlock(), exceptionOnInvalidType, objectSupport));
                else :
                    if (values['leadspaces']
                        and ' ' == values['leadspaces']
                        and re.match('^(?P<key>'+Inline.REGEX_QUOTED_STRING+'|[^ \'"\\[].*?) *\:(\s+(?P<value>.+?))?\s*$', values['value'], re.U)
                    ):
                        # this is a compact notation element, add to next block and parse
                        c = self.__getRealCurrentLineNb();
                        parser = Parser(c);
                        parser.__refs = self.__refs;

                        block = values['value'];
                        if ( not self.__isNextLineIndented()) :
                            block += "\n"+self.__getNextEmbedBlock(self.__getCurrentLineIndentation() + 2);


                        data.append(parser.parse(block, exceptionOnInvalidType, objectSupport));
                    else :
                        data.append(self.__parseValue(values['value'], exceptionOnInvalidType, objectSupport));


            elif (re.match('^(?P<key>'+Inline.REGEX_QUOTED_STRING+'|[^ \'"\[\{].*?) *\:(\s+(?P<value>.+?))?\s*$', self.__currentLine, re.U)) :
                if (context and 'sequence' == context) :
                    raise ParseException('You cannot define a mapping item when in a sequence');

                values = re.match('^(?P<key>'+Inline.REGEX_QUOTED_STRING+'|[^ \'"\[\{].*?) *\:(\s+(?P<value>.+?))?\s*$', self.__currentLine, re.U);
                values = {
                    0: values.group(0),
                    'key': values.group('key'),
                    'value': values.group('value'),
                };
                context = 'mapping';
                if not data:
                    data = OrderedDict();

                # force correct settings
                Inline.parse(None, exceptionOnInvalidType, objectSupport);
                try:
                    key = Inline.parseScalar(values['key']);
                except ParseException as e:
                    e.setParsedLine(self.__getRealCurrentLineNb() + 1);
                    e.setSnippet(self.__currentLine);

                    raise e;


                if ('<<' == key) :
                    if values['value'] and values['value'].startswith('*') :
                        isInPlace = values['value'][1:];
                        if isInPlace not in self.__refs :
                            raise ParseException(
                                'Reference "{0}" does not exist.'.format(
                                    isInPlace),
                                    self.__getRealCurrentLineNb() + 1,
                                    self.__currentLine
                            );

                    else :
                        if values['value']:
                            value = values['value'];
                        else :
                            value = self.__getNextEmbedBlock();

                        c = self.__getRealCurrentLineNb() + 1;
                        parser = Parser(c);
                        parser.__refs = self.__refs;
                        parsed = parser.parse(value, exceptionOnInvalidType, objectSupport);

                        merged = OrderedDict();
                        if not isinstance(parsed, dict) :
                            raise ParseException('YAML merge keys used with a scalar value instead of an array.', self.__getRealCurrentLineNb() + 1, self.__currentLine);
                        elif 0 in parsed :
                            # Numeric array, merge individual elements
                            for parsedItem in reversed(parsed):
                                if not isinstance(parsedItem, dict) :
                                    raise ParseException('Merge items must be arrays.', self.__getRealCurrentLineNb() + 1, parsedItem);

                                merged.update(parsedItem);

                        else :
                            # Associative array, merge
                            merged.update(parsed);


                        isProcessed = merged;

                elif values['value'] :
                    matches = re.match('^&(?P<ref>[^ ]+) *(?P<value>.*)', values['value'], re.U);
                    if matches:
                        isRef = matches.group('ref');
                        values['value'] = matches.group('value');


                if (isProcessed) :
                    # Merge keys
                    data = isProcessed;
                # hash
                elif not values['value'] or '' == values['value'].strip(' ') or values['value'].lstrip(' ').startswith('#') :
                    # if next line is less indented or equal, then it means that the current value is None:
                    if (self.__isNextLineIndented() and  not self.__isNextLineUnIndentedCollection()) :
                        data[key] = None;
                    else :
                        c = self.__getRealCurrentLineNb() + 1;
                        parser = Parser(c);
                        parser.__refs = self.__refs;
                        data[key] = parser.parse(self.__getNextEmbedBlock(), exceptionOnInvalidType, objectSupport);

                else :
                    if (isInPlace) :
                        data = self.__refs[isInPlace];
                    else :
                        data[key] = self.__parseValue(values['value'], exceptionOnInvalidType, objectSupport);


            else :
                # 1-liner optionally followed by newline
                lineCount = len(self.__lines);
                if 1 == lineCount or (2 == lineCount and not self.__lines[1]) :
                    try:
                        value = Inline.parse(self.__lines[0], exceptionOnInvalidType, objectSupport);
                    except ParseException as e:
                        e.setParsedLine(self.__getRealCurrentLineNb() + 1);
                        e.setSnippet(self.__currentLine);

                        raise e;


                    if isinstance(value, list) and value :
                        first = value[0];
                        if isinstance(first, String) and first.startswith('*') :
                            data = list();
                            for alias in value:
                                data.append(self.__refs[alias[1:]]);

                            value = data;


                    return value;


#                switch (preg_last_error())
#                    case PREG_INTERNAL_ERROR:
#                        error = 'Internal PCRE error.';
#                        break;
#                    case PREG_BACKTRACK_LIMIT_ERROR:
#                        error = 'pcre.backtrack_limit reached.';
#                        break;
#                    case PREG_RECURSION_LIMIT_ERROR:
#                        error = 'pcre.recursion_limit reached.';
#                        break;
#                    case PREG_BAD_UTF8_ERROR:
#                        error = 'Malformed UTF-8 data.';
#                        break;
#                    case PREG_BAD_UTF8_OFFSET_ERROR:
#                        error = 'Offset doesn\'t correspond to the begin of a valid UTF-8 code point.';
#                        break;
#                    default:
#                        error = 'Unable to parse.';

                error = 'Unable to parse.';

                raise ParseException(error, self.__getRealCurrentLineNb() + 1, self.__currentLine);


            if (isRef) :
                if context == 'mapping':
                    self.__refs[isRef] = data.values()[-1];
                else:
                    self.__refs[isRef] = data[-1];


        return None if not data else data;


    def __getRealCurrentLineNb(self):
        """Returns the current line number (takes the offset into account).

        @return: integer The current line number

        """

        return self.__currentLineNb + self.__offset;


    def __getCurrentLineIndentation(self):
        """Returns the current line indentation.

        @return: integer The current line indentation

        """

        return len(self.__currentLine) - len(self.__currentLine.lstrip(' '));


    def __getNextEmbedBlock(self, indentation = None):
        """Returns the next embed block of YAML.

        @param: integer indentation The indent level at which the block is to be read, or None for default

        @return string A YAML string

        @raise ParseException When indentation problem are detected

        """

        self.__moveToNextLine();

        if (None is indentation) :
            newIndent = self.__getCurrentLineIndentation();

            unindentedEmbedBlock = self.__isStringUnIndentedCollectionItem();

            if (not self.__isCurrentLineEmpty() and 0 == newIndent and  not unindentedEmbedBlock) :
                raise ParseException('Indentation problem.', self.__getRealCurrentLineNb() + 1, self.__currentLine);

        else :
            newIndent = indentation;


        data = [self.__currentLine[newIndent:]];

        isItUnindentedCollection = self.__isStringUnIndentedCollectionItem();

        while (self.__moveToNextLine()):

            if (isItUnindentedCollection and  not self.__isStringUnIndentedCollectionItem()) :
                self.__moveToPreviousLine();
                break;


            if (self.__isCurrentLineEmpty()) :
                if (self.__isCurrentLineBlank()) :
                    data.append(self.__currentLine[newIndent:]);


                continue;


            indent = self.__getCurrentLineIndentation();

            match = re.match('^(?P<text> *)$', self.__currentLine);
            if match :
                # empty line
                data.append(match.group('text'));
            elif (indent >= newIndent) :
                data.append(self.__currentLine[newIndent:]);
            elif (0 == indent) :
                self.__moveToPreviousLine();

                break;
            else :
                raise ParseException('Indentation problem.', self.__getRealCurrentLineNb() + 1, self.__currentLine);



        return "\n".join(data);


    def __moveToNextLine(self):
        """Moves the parser to the next line.

        @return: Boolean

        """

        if (self.__currentLineNb >= len(self.__lines) - 1) :
            return False;

        self.__currentLineNb += 1;

        self.__currentLine = self.__lines[self.__currentLineNb];

        return True;


    def __moveToPreviousLine(self):
        """Moves the parser to the previous line.

        """

        self.__currentLineNb -= 1;

        self.__currentLine = self.__lines[self.__currentLineNb];


    def __parseValue(self, value, exceptionOnInvalidType, objectSupport):
        """Parses a YAML value.

        @param: string value A YAML value

        @return mixed  A PHP value

        @raise ParseException When reference does not exist

        """

        if value.startswith('*') :
            if '#' in value :
                pos = value.find('#');
                value = value[1:1 + pos - 2];
            else :
                value = value[1:];


            if value not in self.__refs :
                raise ParseException(
                    'Reference "{0}" does not exist.'.format(value),
                    self.__currentLine
                );


            return self.__refs[value];

        matches = re.match('^(?P<separator>\||>)(?P<modifiers>\+|\-|\d+|\+\d+|\-\d+|\d+\+|\d+\-)?(?P<comments> +#.*)?$', value);
        if (matches) :
            modifiers = matches.group('modifiers') if matches.group('modifiers') else '';

            return self.__parseFoldedScalar(matches.group('separator'), re.sub('\d+', '', modifiers), abs(Convert.str2int(modifiers)));


        try:
            return Inline.parse(value, exceptionOnInvalidType, objectSupport);
        except ParseException as e:
            e.setParsedLine(self.__getRealCurrentLineNb() + 1);
            e.setSnippet(self.__currentLine);

            raise e;



    def __parseFoldedScalar(self, separator, indicator = '', indentation = 0):
        """Parses a folded scalar.

        @param: string  separator   The separator that was used to begin this folded scalar (| or >)
        @param string  indicator   The indicator that was used to begin this folded scalar (+ or -)
        @param integer indentation The indentation that was used to begin this folded scalar

        @return string  The text value

        """

        separator = "\n" if '|' == separator else ' ';
        text = '';

        notEOF = self.__moveToNextLine();

        while (notEOF and self.__isCurrentLineBlank()):
            text += "\n";

            notEOF = self.__moveToNextLine();


        if ( not notEOF) :
            return '';

        matches = re.match('^(?P<indent>'+((' ' * indentation) if indentation else ' +')+')(?P<text>.*)$', self.__currentLine, re.U);
        if not matches :
            self.__moveToPreviousLine();

            return '';


        textIndent = matches.group('indent');
        previousIndent = textIndent;

        text += matches.group('text')+separator;
        while (self.__currentLineNb + 1 < len(self.__lines)):
            self.__moveToNextLine();
            matches = re.match('^(?P<indent>[ ]{'+str(len(textIndent))+',})(?P<text>.+)$', self.__currentLine, re.U)
            if matches :
                if ' ' == separator and previousIndent != matches.group('indent') :
                    text = text[0:-1]+"\n";

                previousIndent = matches.group('indent');

                diff = len(matches.group('indent')) - len(textIndent);
                text += (' ' * (diff - len(textIndent)))+matches.group('text')+("\n" if diff else separator);

                continue;

            matches = re.match('^(?P<text> *)$', self.__currentLine);
            if matches:
                text += re.sub('^[ ]{1,'+str(len(textIndent))+'}', '', matches.group('text'))+"\n";
            else :
                self.__moveToPreviousLine();

                break;



        if (' ' == separator) :
            # replace last separator by a newline
            text = re.sub(' (\n*)$', "\n\\1", text);


        if indicator == '':
            text = re.sub('\n+$', "\n", text, flags=re.S);
        elif indicator == '+':
            pass;
        elif indicator == '-':
            text = re.sub('\n+$', '', text, flags=re.S);

        return text;


    def __isNextLineIndented(self):
        """Returns True if the next line is indented.:

        @return: Boolean Returns True if the next line is indented, False otherwise:

        """

        currentIndentation = self.__getCurrentLineIndentation();
        notEOF = self.__moveToNextLine();

        while (notEOF and self.__isCurrentLineEmpty()):
            notEOF = self.__moveToNextLine();


        if (False is notEOF) :
            return False;


        ret = False;
        if (self.__getCurrentLineIndentation() <= currentIndentation) :
            ret = True;


        self.__moveToPreviousLine();

        return ret;


    def __isCurrentLineEmpty(self):
        """Returns True if the current line is blank or if it is a comment line.:

        @return: Boolean Returns True if the current line is empty or if it is a comment line, False otherwise:

        """

        return self.__isCurrentLineBlank() or self.__isCurrentLineComment();


    def __isCurrentLineBlank(self):
        """Returns True if the current line is blank.:

        @return: Boolean Returns True if the current line is blank, False otherwise:

        """

        return '' == self.__currentLine.strip(' ');


    def __isCurrentLineComment(self):
        """Returns True if the current line is a comment line.:

        @return: Boolean Returns True if the current line is a comment line, False otherwise:

        """

        # checking explicitly the first char of the strip is faster than loops or strpos
        lstripmedLine = self.__currentLine.lstrip(' ');

        return lstripmedLine.startswith('#');


    def __cleanup(self, value):
        """Cleanups a YAML string to be parsed.

        @param: string value The input YAML string

        @return string A cleaned up YAML string

        """

        value = value.replace("\r\n", "\n");
        value = value.replace("\r", "\n");

        # strip YAML header
        count = Ref(0);
        def callback(match):
            count.add(1);
            return '';
        value = re.sub('^\%YAML[: ][\d\.]+.*\n', callback, value, 0, re.S|re.U);
        self.__offset += count.get();

        # remove leading comments
        count.set(0);
        stripmedValue = re.sub('^(\#.*?\n)+', callback, value, 0, re.S);
        if (count.get() == 1) :
            # items have been removed, update the offset
            self.__offset += value.count("\n") - stripmedValue.count("\n");
            value = stripmedValue;


        # remove start of the document marker (---)
        count.set(0);
        stripmedValue = re.sub('^\-\-\-.*?\n', callback, value, 0, re.S);
        if (count.get() == 1) :
            # items have been removed, update the offset
            self.__offset += value.count("\n") - stripmedValue.count("\n");
            value = stripmedValue;

            # remove end of the document marker (...)
            value = re.sub('\.\.\.\s*$', '', value, flags=re.S);


        return value;


    def __isNextLineUnIndentedCollection(self):
        """Returns True if the next line starts unindented collection:

        @return: Boolean Returns True if the next line starts unindented collection, False otherwise:

        """

        currentIndentation = self.__getCurrentLineIndentation();
        notEOF = self.__moveToNextLine();

        while (notEOF and self.__isCurrentLineEmpty()):
            notEOF = self.__moveToNextLine();


        if (False is notEOF) :
            return False;


        ret = False;
        if (
            self.__getCurrentLineIndentation() == currentIndentation
            and
            self.__isStringUnIndentedCollectionItem()
        ):
            ret = True;


        self.__moveToPreviousLine();

        return ret;


    def __isStringUnIndentedCollectionItem(self):
        """Returns True if the string is un-indented collection item:

        @return: Boolean Returns True if the string is un-indented collection item, False otherwise:

        """

        return self.__currentLine.startswith('- ');


class Inline(Object):
    """Inline implements a YAML parser/dumper for the YAML inline syntax.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    REGEX_QUOTED_STRING = '(?:"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)"|\'([^\']*(?:\'\'[^\']*)*)\')';

    __exceptionOnInvalidType = False;
    __objectSupport = False;

    @classmethod
    def parse(cls, value, exceptionOnInvalidType = False, objectSupport = False):
        """Converts a YAML string to a PHP array.

        @param: string  value                  A YAML string
        @param Boolean exceptionOnInvalidType True if an exception must be thrown on invalid types (a PHP resource or object), False otherwise:
        @param Boolean objectSupport          True if object support is enabled, False otherwise:

        @return array A PHP array representing the YAML string

        @raise ParseException

        """

        cls.__exceptionOnInvalidType = exceptionOnInvalidType;
        cls.__objectSupport = objectSupport;

        if not value:
            value = '';

        value = value.strip();

        if not value :
            return '';


        i = Ref(0);
        if value[0] == '[':
            result = cls.__parseSequence(value, i);
            i.add(1);
        elif value[0] == '{':
            result = cls.__parseMapping(value, i);
            i.add(1);
        else:
            result = cls.parseScalar(value, None, ['"', "'"], i);

        # some comments are allowed at the end
        if re.sub('^\s+#.*$', '', value[i.get():]) :
            raise ParseException('Unexpected characters near "{0}".'.format(
                value[i.get():]
            ));

        return result;

    @classmethod
    def dump(cls, value, exceptionOnInvalidType = False, objectSupport = False):
        """Dumps a given PHP variable to a YAML string.

        @param: mixed   value                  The PHP variable to convert
        @param Boolean exceptionOnInvalidType True if an exception must be thrown on invalid types (a PHP resource or object), False otherwise:
        @param Boolean objectSupport          True if object support is enabled, False otherwise:

        @return string The YAML string representing the PHP array

        @raise DumpException When trying to dump PHP resource

        """

        if isinstance(value, (list, dict)):
            return cls.__dumpArray(value, exceptionOnInvalidType, objectSupport);
        if None is value:
            return 'null';
        if True is value:
            return 'true';
        if False is value:
            return 'false';
        if str(value).isdigit():
            return "'"+value+"'" if isinstance(value, String) else str(int(value));
        if cls.__is_numeric(value):
            return "'"+value+"'" if isinstance(value, String) else re.sub('INF', '.Inf', str(value), 0, re.I) if math.isinf(value) else str(value);
        if not isinstance(value, String):
            if (objectSupport) :
                return '!!python/object:'+serialize(value);

            if (exceptionOnInvalidType) :
                raise DumpException('Object support when dumping a YAML file has been disabled.');

            return 'null';
        if Escaper.requiresDoubleQuoting(value):
            return Escaper.escapeWithDoubleQuotes(value);
        if Escaper.requiresSingleQuoting(value):
            return Escaper.escapeWithSingleQuotes(value);
        if '' == value:
            return "''";
        if (cls.__getTimestampRegex().match(value)
            or value.lower() in ['null', '~', 'true', 'false']):
            return "'"+value+"'";
        if isinstance(value, String):
            return value;



    @classmethod
    def __dumpArray(cls, value, exceptionOnInvalidType, objectSupport):
        """Dumps a PHP array to a YAML string.

        @param: list|dict   value                  The PHP array to dump
        @param Boolean exceptionOnInvalidType True if an exception must be thrown on invalid types (a PHP resource or object), False otherwise:
        @param Boolean objectSupport          True if object support is enabled, False otherwise:

        @return string The YAML string representing the PHP array

        """

        if isinstance(value, list):
            # sequence
            output = list();
            for val in value:
                output.append(cls.dump(val, exceptionOnInvalidType, objectSupport));

            return '[{0}]'.format(', '.join(output));

        if isinstance(value, dict):
            # mapping
            output = list();
            for key, val in value.items():
                output.append('{0}: {1}'.format(cls.dump(key, exceptionOnInvalidType, objectSupport), cls.dump(val, exceptionOnInvalidType, objectSupport)));


            return '{'+' {0} '.format(', '.join(output))+'}';

    @classmethod
    def parseScalar(cls, scalar, delimiters = None, stringDelimiters = ['"', "'"], i = None, evaluate = True):
        """Parses a scalar to a YAML string.

        @param: scalar scalar
        @param string delimiters
        @param array  stringDelimiters
        @param integer &i
        @param Boolean evaluate

        @return string A YAML string

        @raise ParseException When malformed inline YAML string is parsed

        """
        if i is None:
            i = Ref(0);
        assert isinstance(i, Ref);

        if scalar[i.get()] in stringDelimiters :
            # quoted scalar
            output = cls.__parseQuotedScalar(scalar, i);

            if (None is not delimiters) :
                tmp = scalar[i.get():].lstrip(' ');
                if tmp[0] not in delimiters :
                    raise ParseException('Unexpected characters ({0}).'.format(
                        scalar[i.get():]
                    ));


        else :
            # "normal" string
            if not delimiters :
                output = scalar[i.get():];
                i.add(len(output));

                # remove comments
                strpos = output.find(' #');
                if strpos != -1 :
                    output = output[0:strpos].rstrip();

            elif (re.match('^(.+?)('+'|'.join(delimiters)+')', scalar[i.get():])) :
                match = re.match('^(.+?)('+'|'.join(delimiters)+')', scalar[i.get():])
                output = match.group(1);
                i.add(len(output));
            else :
                raise ParseException(
                    'Malformed inline YAML string ({0}).'.format(scalar)
                );


            output = cls.__evaluateScalar(output) if evaluate else output;


        return output;

    @classmethod
    def __parseQuotedScalar(cls, scalar, i):
        """Parses a quoted scalar to YAML.

        @param: string scalar
        @param integer &i

        @return string A YAML string

        @raise ParseException When malformed inline YAML string is parsed

        """
        assert isinstance(i, Ref);

        # Only check the current item we're dealing with (for sequences)
        subject = scalar[i.get():];
        items = re.split('[\'"]\s*(?:[,:]|[}\]]\s*,)', subject);
        subject = subject[:len(items[0]) + 1];

        match = re.match('^'+cls.REGEX_QUOTED_STRING, scalar[i.get():], flags=re.U);
        if not match :
            raise ParseException(
                'Malformed inline YAML string ({0}).'.format(
                scalar[i.get():]
            ));


        output = match.group(0)[1: 1 + len(match.group(0)) - 2];

        unescaper = Unescaper();
        if ('"' == scalar[i.get()]) :
            output = unescaper.unescapeDoubleQuotedString(output);
        else :
            output = unescaper.unescapeSingleQuotedString(output);


        i.add(len(match.group(0)));

        return output;

    @classmethod
    def __parseSequence(cls, sequence, i = None):
        """Parses a sequence to a YAML string.

        @param: string sequence
        @param integer &i

        @return string A YAML string

        @raise ParseException When malformed inline YAML string is parsed

        """
        if i is None:
            i = Ref(0);
        assert isinstance(i, Ref);

        output = list();
        lenght = len(sequence);
        i.add(1);

        # [foo, bar, ...]
        while (i.get() < lenght):
            if sequence[i.get()] == '[':
                output.append(cls.__parseSequence(sequence, i));
            elif sequence[i.get()] == '{':
                # nested mapping
                output.append(cls.__parseMapping(sequence, i));
            elif sequence[i.get()] == ']':
                return output;
            elif sequence[i.get()] in [',', ' ']:
                pass;
            else:
                isQuoted = sequence[i.get()] in ['"', "'"];
                value = cls.parseScalar(sequence, [',', ']'], ['"', "'"], i);

                if not isQuoted and isinstance(value, String) and ': ' in value :
                    # embedded mapping?
                    try:
                        value = cls.__parseMapping('{'+value+'}');
                    except InvalidArgumentException as e:
                        # no, it's not
                        pass;



                output.append(value);

                i.sub(1);


            i.add(1);


        raise ParseException(
            'Malformed inline YAML string {0}'.format(sequence)
        );

    @classmethod
    def __parseMapping(cls, mapping, i = None):
        """Parses a mapping to a YAML string.

        @param: string mapping
        @param integer &i

        @return string A YAML string

        @raise ParseException When malformed inline YAML string is parsed

        """
        if i is None:
            i = Ref(0);
        assert isinstance(i, Ref);

        output = OrderedDict();
        lenght = len(mapping);
        i.add(1);

        # foo: bar, bar:foo, ...
        while (i.get() < lenght):
            if mapping[i.get()] in [' ', ',']:
                i.add(1);
                continue;
            elif mapping[i.get()] == '}':
                return output;

            # key
            key = cls.parseScalar(mapping, [':', ' '], ['"', "'"], i, False);

            # value
            done = False;
            while (i.get() < lenght):
                if mapping[i.get()] == '[':
                    # nested sequence
                    output[key] = cls.__parseSequence(mapping, i);
                    done = True;
                elif mapping[i.get()] == '{':
                    # nested mapping
                    output[key] = cls.__parseMapping(mapping, i);
                    done = True;
                elif mapping[i.get()] in [':', ' ']:
                    pass;
                else:
                    output[key] = cls.parseScalar(mapping, [',', '}'], ['"', "'"], i);
                    done = True;
                    i.sub(1);


                i.add(1);

                if (done) :
                    break;




        raise ParseException(
            'Malformed inline YAML string {0}'.format(
            mapping
        ));

    @classmethod
    def __evaluateScalar(cls, scalar):
        """Evaluates scalars and replaces magic values.

        @param: string scalar

        @return string A YAML string

        """

        scalar = scalar.strip();

        if ('null' == scalar.lower() or
            '' == scalar or
            '~' == scalar):
            return None;
        if scalar.startswith('!str'):
            return scalar[5:];
        if scalar.startswith('! '):
            return Convert.str2int(cls.parseScalar(scalar[2:]));
        if scalar.startswith('!!python/object:'):
            if (cls.__objectSupport) :
                return unserialize(scalar[16:]);


            if cls.__exceptionOnInvalidType :
                raise ParseException(
                    'Object support when parsing a YAML file has been '
                    'disabled.'
                );

            return None;
        if scalar.isdigit():
            raw = scalar;
            cast = int(scalar);

            return int(scalar, 8) if scalar.startswith('0') else cast if str(raw) == str(cast) else raw;
        if scalar.startswith('-') and scalar[1:].isdigit():
            raw = scalar;
            cast = int(scalar);

            return int(scalar, 8) if '0' == scalar[1] else cast if str(raw) == str(cast) else raw;
        if 'true' == scalar.lower():
            return True;
        if 'false' == scalar.lower():
            return False;
        if cls.__is_numeric(scalar):
            return int(scalar, 16) if '0x' == scalar[0]+scalar[1] else float(scalar);
        if ( scalar.lower() == '.inf'
            or scalar.lower() == '.nan'):
            return 1e10000;
        if scalar.lower() == '-.inf':
            return -1e10000;
        if re.match('^(-|\+)?[0-9,]+(\.[0-9]+)?$', scalar):
            return float(scalar.replace(',', ''));
        if cls.__getTimestampRegex().match(scalar):
            return time.mktime(time.strptime(scalar, '%Y-%m-%d %H:%M:%S'));

        return str(scalar);

    @classmethod
    def __is_numeric(cls, var):
        """Finds whether the given variable is numeric.

        Numeric strings consist of optional sign, any number of digits,
        optional decimal part and optional exponential part. Thus +0123.45e6
        is a valid numeric value. Hexadecimal (e.g. 0xf4c3b00c),
        Binary(e.g. 0b10100111001), Octal (e.g. 0777) notation is allowed too
        but only without sign, decimal and exponential part.

        @param var: mixed The variable being evaluated.

        @return: boolean Returns TRUE if var is a number or a numeric string,
            FALSE otherwise.
        """

        isString = False;

        if isinstance(var, String):
            isString = True;

        if isString and re.search("\s", var):
            return False;


        # Int/Float/Complex
        try:
            int(var);
        except Exception:
            pass;
        else:
            return True;

        try:
            float(var);
        except Exception:
            pass;
        else:
            return True;

        try:
            complex(var);
        except Exception:
            pass;
        else:
            return True;

        # Empty string
        if not isString or not var:
            return False;

        # Handle '0'
        if var == '0':
            return True;


        # Hex/Binary
        litneg = var[1:] if var[0] in '-+' else var;
        if litneg[0] == '0':
            if litneg[1] in 'xX':
                try:
                    int(litneg[2:], 16);
                except Exception:
                    pass;
                else:
                    return True;
            if litneg[1] in 'bB':
                try:
                    int(litneg[2:]);
                except Exception:
                    pass;
                else:
                    return True;
            elif litneg[1] == 'o':
                try:
                    int(litneg[2:], 8);
                except Exception:
                    pass;
                else:
                    return True;
            else:
                try:
                    int(litneg[1:], 8);
                except Exception:
                    pass;
                else:
                    return True;



    @classmethod
    def __getTimestampRegex(self):
        """Gets a regex that matches a YAML date.

        @return: string The regular expression

        @see http://www.yaml.org/spec/1.2/spec.html#id2761573

        """

        return re.compile("""
        ^
        (?P<year>[0-9][0-9][0-9][0-9])
        -(?P<month>[0-9][0-9]?)
        -(?P<day>[0-9][0-9]?)
        (?:(?:[Tt]|[ t]+)
        (?P<hour>[0-9][0-9]?)
        :(?P<minute>[0-9][0-9])
        :(?P<second>[0-9][0-9])
        (?:\.(?P<fraction>[0-9]*))?
        (?:[ t]*(?P<tz>Z|(?P<tz_sign>[-+])(?P<tz_hour>[0-9][0-9]?)
        (?::(?P<tz_minute>[0-9][0-9]))?))?)?
        $
""", re.X);

class Unescaper(Object):
    """Unescaper encapsulates unescaping rules for single and double-quoted
    YAML strings.

    @author: Matthew Lewinski <matthew@lewinski.org>

    """

    # Parser and Inline assume UTF-8 encoding, so escaped Unicode characters
    # must be converted to that encoding.
    ENCODING = 'UTF-8';

    # Regex fragment that matches an escaped character in a double quoted
    # string.
    REGEX_ESCAPED_CHARACTER = "\\\\([0abt\tnvfre \\\"\\/\\\\N_LP]|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})";

    def unescapeSingleQuotedString(self, value):
        """Unescapes a single quoted string.

        @param: string value A single quoted string.

        @return string The unescaped string.

        """

        return value.replace('\'\'', '\'');


    def __callback(self, match):
        return self.unescapeCharacter(match.group(0));

    def unescapeDoubleQuotedString(self, value):
        """Unescapes a double quoted string.

        @param: string value A double quoted string.

        @return string The unescaped string.

        """

        # evaluate the string
        return re.sub(self.REGEX_ESCAPED_CHARACTER, self.__callback, value, 0, re.U);


    def unescapeCharacter(self, value):
        """Unescapes a character that was found in a double-quoted string

        @param: string value An escaped character

        @return string The unescaped character

        """

        if value[1] == '0':
            return "\x00";
        if value[1] == 'a':
            return "\x07";
        if value[1] == 'b':
            return "\x08";
        if value[1] == 't':
            return "\t";
        if value[1] == "\t":
            return "\t";
        if value[1] == 'n':
            return "\n";
        if value[1] == 'v':
            return "\x0b";
        if value[1] == 'f':
            return "\x0c";
        if value[1] == 'r':
            return "\x0d";
        if value[1] == 'e':
            return "\x1b";
        if value[1] == ' ':
            return ' ';
        if value[1] == '"':
            return '"';
        if value[1] == '/':
            return '/';
        if value[1] == '\\':
            return '\\';
        if value[1] == 'N':
            # U+0085 NEXT LINE
            return self.__convertEncoding("\x00\x85", self.ENCODING, 'UTF-16BE');
        if value[1] == '_':
            # U+00A0 NO-BREAK SPACE
            return self.__convertEncoding("\x00\xA0", self.ENCODING, 'UTF-16BE');
        if value[1] == 'L':
            # U+2028 LINE SEPARATOR
            return self.__convertEncoding("\x20\x28", self.ENCODING, 'UTF-16BE');
        if value[1] == 'P':
            # U+2029 PARAGRAPH SEPARATOR
            return self.__convertEncoding("\x20\x29", self.ENCODING, 'UTF-16BE');
        if value[1] == 'x':
            char = pack('>H', int(value[2:2 + 2], 16));

            return self.__convertEncoding(char, self.ENCODING, 'UTF-16BE');
        if value[1] == 'u':
            char = pack('>H', int(value[2:2 + 4], 16));

            return self.__convertEncoding(char, self.ENCODING, 'UTF-16BE');
        if value[1] == 'U':
            char = pack('>L', int(value[2:2 + 8], 16));

            return self.__convertEncoding(char, self.ENCODING, 'UTF-32BE');



    def __convertEncoding(self, value, to, fromV):
        """Convert a string from one encoding to another.

        @param: string value The string to convert
        @param string to    The input encoding
        @param string from  The output encoding

        @return string The string with the new encoding

        @raise RuntimeException if no suitable encoding function is found (iconv or mbstring):

        """

        return value.decode(fromV).encode(to);


        raise RuntimeException('No suitable convert encoding function (install the iconv or mbstring extension).');


class Escaper(Object):
    """Escaper encapsulates escaping rules for single and double-quoted
    YAML strings.

    @author: Matthew Lewinski <matthew@lewinski.org>

    """

    # Characters that would cause a dumped string to require double quoting.
    REGEX_CHARACTER_TO_ESCAPE = "[\\x00-\\x1f]|\xc2\x85|\xc2\xa0|\xe2\x80\xa8|\xe2\x80\xa9";

    # Mapping arrays for escaping a double quoted string. The backslash is
    # first to ensure proper escaping because str_replace operates iteratively
    # on the input arrays. This ordering of the characters avoids the use of strtr,
    # which performs more slowly.
    __escapees = ['\\\\', '\\"', '"',
        "\x00",  "\x01",  "\x02",  "\x03",  "\x04",  "\x05",  "\x06",  "\x07",
        "\x08",  "\x09",  "\x0a",  "\x0b",  "\x0c",  "\x0d",  "\x0e",  "\x0f",
        "\x10",  "\x11",  "\x12",  "\x13",  "\x14",  "\x15",  "\x16",  "\x17",
        "\x18",  "\x19",  "\x1a",  "\x1b",  "\x1c",  "\x1d",  "\x1e",  "\x1f",
        "\xc2\x85", "\xc2\xa0", "\xe2\x80\xa8", "\xe2\x80\xa9"];
    __escaped  = ['\\"', '\\\\', '\\"',
        "\\0",   "\\x01", "\\x02", "\\x03", "\\x04", "\\x05", "\\x06", "\\a",
        "\\b",   "\\t",   "\\n",   "\\v",   "\\f",   "\\r",   "\\x0e", "\\x0f",
        "\\x10", "\\x11", "\\x12", "\\x13", "\\x14", "\\x15", "\\x16", "\\x17",
        "\\x18", "\\x19", "\\x1a", "\\e",   "\\x1c", "\\x1d", "\\x1e", "\\x1f",
        "\\N", "\\_", "\\L", "\\P"];

    @classmethod
    def requiresDoubleQuoting(cls, value):
        """Determines if a PHP value would require double quoting in YAML.

        @param: string value A PHP value

        @return Boolean True if the value would require double quotes.

        """

        return re.search(cls.REGEX_CHARACTER_TO_ESCAPE, value, re.U);

    @classmethod
    def escapeWithDoubleQuotes(cls, value):
        """Escapes and surrounds a PHP value with double quotes.

        @param: string value A PHP value

        @return string The quoted, escaped string

        """

        return '"{0}"'.format(cls.__mapReplace(cls.__escapees, cls.__escaped, value));

    @classmethod
    def __mapReplace(cls, fromList, toList, string):
        for k in range(len(fromList)):
            v = fromList[k];
            r = toList[k];
            string = string.replace(v, r);

        return string;

    @classmethod
    def requiresSingleQuoting(cls, value):
        """Determines if a PHP value would require single quoting in YAML.:

        @param: string value A PHP value

        @return Boolean True if the value would require single quotes.:

        """

        return re.search('[ \s \' " \: \{ \} \[ \] , & \* \# \?] | \A[ - ? | < > = ! % @ ` ]', value, re.X);


    @classmethod
    def escapeWithSingleQuotes(cls, value):
        """Escapes and surrounds a PHP value with single quotes.

        @param: string value A PHP value

        @return string The quoted, escaped string

        """

        return "'{0}'".format(value.replace('\'', '\'\''));


class Dumper(Object):
    """Dumper dumps PHP variables to YAML strings.

    @author: Fabien Potencier <fabien@symfony.com>

    """

    def __init__(self):

        self._indentation = 4;
        """The amount of spaces to use for indentation of nested nodes.

        @var: integer

        """

    def setIndentation(self, num):
        """Sets the indentation.

        @param: integer num The amount of spaces to use for indentation of nested nodes.

        """

        self._indentation = int(num);


    def dump(self, inputv, inline = 0, indent = 0, exceptionOnInvalidType = False, objectSupport = False):
        """Dumps a PHP value to YAML.

        @param: mixed  inputv                 The PHP value
        @param integer inline                 The level where you switch to inline YAML
        @param integer indent                 The level of indentation (used internally)
        @param Boolean exceptionOnInvalidType True if an exception must be thrown on invalid types (a PHP resource or object), False otherwise:
        @param Boolean objectSupport          True if object support is enabled, False otherwise:

        @return string  The YAML representation of the PHP value

        """

        output = '';
        prefix = ' ' * indent if indent else '';

        if inline <= 0 or not isinstance(inputv, (list, dict)) or not inputv :
            output += prefix+Inline.dump(inputv, exceptionOnInvalidType, objectSupport);
        else:
            if isinstance(inputv, list):
                for value in inputv:
                    willBeInlined = inline - 1 <= 0 or not isinstance(value, (list, dict)) or not value;

                    output += '{0}{1}{2}{3}'.format(
                        prefix,
                        '-',
                        ' ' if willBeInlined else "\n",
                        self.dump(value, inline - 1, 0 if willBeInlined else indent + self._indentation, exceptionOnInvalidType, objectSupport)
                    )+("\n" if willBeInlined else '');

            else:
                for key, value in inputv.items():
                    willBeInlined = inline - 1 <= 0 or not isinstance(value, (list, dict)) or not value;

                    output += '{0}{1}{2}{3}'.format(
                        prefix,
                        Inline.dump(key, exceptionOnInvalidType, objectSupport)+':',
                        ' ' if willBeInlined else "\n",
                        self.dump(value, inline - 1, 0 if willBeInlined else indent + self._indentation, exceptionOnInvalidType, objectSupport)
                    )+("\n" if willBeInlined else '');


        return output;


class Yaml(Object):
    """Yaml offers convenience methods to load and dump YAML.

    @author: Fabien Potencier <fabien@symfony.com>

    @api

    """

    @classmethod
    def parse(cls, content, exceptionOnInvalidType = False, objectSupport = False):
        """Parses YAML into a PHP array.

        The parse method, when supplied with a YAML stream (string or file),
        will do its best to convert YAML in a file into a PHP array.

         Usage:
         <code>
          array = Yaml::parse('config.yml');
          print_r(array);
         </code>

        As this method accepts both plain strings and file names as an input,
        you must validate the input before calling this method. Passing a file
        as an input is a deprecated feature and will be removed in 3.0.

        @param: string content Path to a YAML file or a string containing YAML

        @return array The YAML converted to a PHP array

        @raise ParseException If the YAML is not valid

        @api

        """

        # if content is a file, process it
        filename = '';
        if ("\n" not in content and os.path.isfile(content)) :
            if (False is os.access(filename, os.R_OK)) :
                raise ParseException(
                    'Unable to parse "{0}" as the file is not readable.'
                    ''.format(filename)
                );

            filename = content;

            f = open(filename);
            content = f.read(filename);
            f.close();



        yaml = Parser();

        try:
            return yaml.parse(content, exceptionOnInvalidType, objectSupport);
        except ParseException as e:
            if (filename) :
                e.setParsedFile(filename);


            raise e;

    @classmethod
    def dump(cls, array, inline = 2, indent = 2, exceptionOnInvalidType = False, objectSupport = False):
        """Dumps a PHP array to a YAML string.

        The dump method, when supplied with an array, will do its best
        to convert the array into friendly YAML.

        @param: list|dict   array             Python array
        @param integer inline                 The level where you switch to inline YAML
        @param integer indent                 The amount of spaces to use for indentation of nested nodes.
        @param Boolean exceptionOnInvalidType True if an exception must be thrown on invalid types (a PHP resource or object), False otherwise:
        @param Boolean objectSupport          True if object support is enabled, False otherwise:

        @return string A YAML string representing the original PHP array

        @api

        """

        yaml = Dumper();
        yaml.setIndentation(indent);

        return yaml.dump(array, inline, 0, exceptionOnInvalidType, objectSupport);
