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

import re;

from pymfony.component.system import Object;
from pymfony.component.system.oop import interface;
from pymfony.component.system.exception import InvalidArgumentException;

@interface
class OutputFormatterInterface(Object):
    """Formatter interface for console output.
 *
 * @author Konstantin Kudryashov <ever.zet@gmail.com>
 *
 * @api

    """

    def setDecorated(self, decorated):
        """Sets the decorated flag.
     *
     * @param Boolean decorated Whether to decorate the messages or not
     *
     * @api

        """

    def isDecorated(self):
        """Gets the decorated flag.
     *
     * @return Boolean True if the output will decorate messages, False otherwise:
     *
     * @api

        """

    def setStyle(self, name, style):
        """Sets a new style.
     *
     * @param string                        name  The style name
     * @param OutputFormatterStyleInterface style The style instance
     *
     * @api

        """
        assert isinstance(style, OutputFormatterStyleInterface);

    def hasStyle(self, name):
        """Checks if output formatter has style with specified name.:
     *
     * @param string name
     *
     * @return Boolean
     *
     * @api

        """

    def getStyle(self, name):
        """Gets style options from style with specified name.:
     *
     * @param string name
     *
     * @return OutputFormatterStyleInterface
     *
     * @api

        """

    def format(self, message):
        """Formats a message according to the given styles.
     *
     * @param string message The message to style
     *
     * @return string The styled message
     *
     * @api

        """

@interface
class OutputFormatterStyleInterface(Object):
    """Formatter style interface for defining styles.
 *
 * @author Konstantin Kudryashov <ever.zet@gmail.com>
 *
 * @api

    """

    def setForeground(self, color = None):
        """Sets style foreground color.
     *
     * @param string color The color name
     *
     * @api

        """

    def setBackground(self, color = None):
        """Sets style background color.
     *
     * @param string color The color name
     *
     * @api

        """

    def setOption(self, option):
        """Sets some specific style option.:
     *
     * @param string option The option name
     *
     * @api

        """

    def unsetOption(self, option):
        """Unsets some specific style option.:
     *
     * @param string option The option name

        """

    def setOptions(self, options):
        """Sets multiple style options at once.
     *
     * @param list options

        """
        assert isinstance(options, list);

    def apply(self, text):
        """Applies the style to a given text.
     *
     * @param string text The text to style
     *
     * @return string

        """


class OutputFormatter(OutputFormatterInterface):
    """Formatter class for(, console output.):
 *
 * @author Konstantin Kudryashov <ever.zet@gmail.com>
 *
 * @api

    """

    # The pattern to phrase the format.
    FORMAT_PATTERN = re.compile(r"(\\?)<(/?)([a-z][a-z0-9_=;-]+)?>((?: [^<\\]+ | (?!<(?:/?[a-z]|/>)). | .(?<=\\<) )*)", re.IGNORECASE | re.DOTALL | re.X);



    @classmethod
    def escape(cls, text):
        """Escapes "<" special char in given text.
     *
     * @param string text Text to escape
     *
     * @return string Escaped text

        """

        return re.sub(r"([^\\]?)<", r'\1\<', text, re.DOTALL | re.IGNORECASE);


    def __init__(self, decorated = None, styles = dict()):
        """Initializes console output formatter.
     *
     * @param Boolean          decorated Whether this formatter should actually decorate strings
     * @param FormatterStyle{} styles    dict of "name: FormatterStyle" instances
     *
     * @api

        """
        assert isinstance(styles, dict);

        self.__decorated = None;
        self.__styles = dict();
        self.__styleStack = None;

        self.__decorated = bool(decorated);

        self.setStyle('error', OutputFormatterStyle('white', 'red'));
        self.setStyle('info', OutputFormatterStyle('green'));
        self.setStyle('comment', OutputFormatterStyle('yellow'));
        self.setStyle('question', OutputFormatterStyle('black', 'cyan'));

        for name, style in styles.items():
            self.setStyle(name, style);


        self.__styleStack = OutputFormatterStyleStack();


    def setDecorated(self, decorated):
        """Sets the decorated flag.
     *
     * @param Boolean decorated Whether to decorate the messages or not
     *
     * @api

        """

        self.__decorated = bool(decorated);


    def isDecorated(self):
        """Gets the decorated flag.
     *
     * @return Boolean True if the output will decorate messages, False otherwise:
     *
     * @api

        """

        return self.__decorated;


    def setStyle(self, name, style):
        """Sets a new style.
     *
     * @param string                        name  The style name
     * @param OutputFormatterStyleInterface style The style instance
     *
     * @api

        """
        assert isinstance(style, OutputFormatterStyleInterface);

        self.__styles[str(name).lower()] = style;


    def hasStyle(self, name):
        """Checks if output formatter has style with specified name.:
     *
     * @param string name
     *
     * @return Boolean
     *
     * @api

        """

        return str(name).lower() in self.__styles.keys();


    def getStyle(self, name):
        """Gets style options from style with specified name.:
     *
     * @param string name
     *
     * @return OutputFormatterStyleInterface
     *
     * @raise InvalidArgumentException When style isn't defined
     *
     * @api

        """

        if ( not self.hasStyle(name)) :
            raise InvalidArgumentException('Undefined style: '+name);


        return self.__styles[str(name).lower()];


    def format(self, message):
        """Formats a message according to the given styles.
     *
     * @param string message The message to style
     *
     * @return string The styled message
     *
     * @api

        """

        message = self.FORMAT_PATTERN.sub(self.__replaceStyle, message);

        return str(message).replace('\\<', '<');


    def getStyleStack(self):
        """@return OutputFormatterStyleStack

        """

        return self.__styleStack;


    def __replaceStyle(self, match):
        """Replaces style of the output.
     *
     * @param array match
     *
     * @return string The replaced style

        """
        if not match:
            return;

        # we got "\<" escaped char
        if ('\\' == match.group(1)) :
            return self.__applyCurrentStyle(match.group(0));


        if not match.group(3) :
            if ('/' == match.group(2)) :
                # we got "</>" tag
                self.__styleStack.pop();

                return self.__applyCurrentStyle(match.group(4));


            # we got "<>" tag
            return '<>'+self.__applyCurrentStyle(match.group(4));


        if str(match.group(3)).lower() in self.__styles :
            style = self.__styles[str(match.group(3)).lower()];
        else :
            style = self.__createStyleFromString(match.group(3));

            if (False is style) :
                return self.__applyCurrentStyle(match.group(0));



        if ('/' == match.group(2)) :
            self.__styleStack.pop(style);
        else :
            self.__styleStack.push(style);


        return self.__applyCurrentStyle(match.group(4));


    def __createStyleFromString(self, string):
        """Tries to create new style instance from string.
     *
     * @param string string
     *
     * @return OutputFormatterStyle|Boolean False if string is not format string:

        """

        matches = re.findall(r"([^=]+)=([^;]+)(;|$)", str(string).lower());
        if not matches :
            return False;


        style = OutputFormatterStyle();
        for match in matches:
            if ('fg' == match[0]) :
                style.setForeground(match[1]);
            elif ('bg' == match[0]) :
                style.setBackground(match[1]);
            else :
                style.setOption(match[1]);



        return style;


    def __applyCurrentStyle(self, text):
        """Applies current style from stack to text, if must be applied.:
     *
     * @param string text Input text
     *
     * @return string string Styled text

        """

        if self.isDecorated() and text:
            return self.__styleStack.getCurrent().apply(text);
        else:
            return text;

class OutputFormatterStyle(OutputFormatterStyleInterface):
    """Formatter style class for(, defining styles.):
 *
 * @author Konstantin Kudryashov <ever.zet@gmail.com>
 *
 * @api

    """

    __availableForegroundColors = {
        'black'     : "30",
        'red'       : "31",
        'green'     : "32",
        'yellow'    : "33",
        'blue'      : "34",
        'magenta'   : "35",
        'cyan'      : "36",
        'white'     : "37",
    };
    __availableBackgroundColors = {
        'black'     : "40",
        'red'       : "41",
        'green'     : "42",
        'yellow'    : "43",
        'blue'      : "44",
        'magenta'   : "45",
        'cyan'      : "46",
        'white'     : "47",
    };
    __availableOptions = {
        'bold'          : "1",
        'underscore'    : "4",
        'blink'         : "5",
        'reverse'       : "7",
        'conceal'       : "8",
    };


    def __init__(self, foreground = None, background = None, options = list()):
        """Initializes output formatter style.
     *
     * @param string foreground The style foreground color name
     * @param string background The style background color name
     * @param array  options    The style options
     *
     * @api

        """
        assert isinstance(options, list);

        self.__foreground = None;
        self.__background = None;
        self.__options = list();

        if (None is not foreground) :
            self.setForeground(foreground);

        if (None is not background) :
            self.setBackground(background);

        if (len(options)) :
            self.setOptions(options);



    def setForeground(self, color = None):
        """Sets style foreground color.
     *
     * @param string color The color name
     *
     * @raise InvalidArgumentException When the color name isn't defined
     *
     * @api

        """

        if (None is color) :
            self.__foreground = None;

            return;

        color = str(color);

        if color not in self.__availableForegroundColors :
            raise InvalidArgumentException(
                'Invalid foreground color specified: "{0}". Expected one of'
                '({1})'.format(
                color,
                ', '.join(self.__availableForegroundColors.keys())
            ));


        self.__foreground = self.__availableForegroundColors[color];


    def setBackground(self, color = None):
        """Sets style background color.
     *
     * @param string color The color name
     *
     * @raise InvalidArgumentException When the color name isn't defined
     *
     * @api

        """

        if (None is color) :
            self.__background = None;

            return;

        color = str(color);

        if color not in self.__availableBackgroundColors :
            raise InvalidArgumentException(
                'Invalid background color specified: "{0}". Expected one of '
                '({1})'.format(
                color,
                ', '.join(self.__availableBackgroundColors.keys())
            ));


        self.__background = self.__availableBackgroundColors[color];


    def setOption(self, option):
        """Sets some specific style option.:
     *
     * @param string option The option name
     *
     * @raise InvalidArgumentException When the option name isn't defined
     *
     * @api

        """

        option = str(option);

        if option not in self.__availableOptions :
            raise InvalidArgumentException(
                'Invalid option specified: "{0}". Expected one of ({1})'
                ''.format(
                option,
                ', '.join(self.__availableOptions.keys())
            ));

        if self.__availableOptions[option] not in self.__options:
            self.__options.append(self.__availableOptions[option]);



    def unsetOption(self, option):
        """Unsets some specific style option.:
     *
     * @param string option The option name
     *
     * @raise InvalidArgumentException When the option name isn't defined
     *

        """

        if option not in self.__availableOptions :
            raise InvalidArgumentException(
                'Invalid option specified: "{0}". Expected one of ({1})'
                ''.format(
                option,
                ', '.join(self.__availableOptions.keys())
            ));

        try:
            pos = self.__options.index(self.__availableOptions[option]);
        except ValueError:
            pass;
        else:
            del self.__options[pos];



    def setOptions(self, options):
        """Sets multiple style options at once.
     *
     * @param array options

        """
        assert isinstance(options, list);

        self.__options = list();

        for option in options:
            self.setOption(option);



    def apply(self, text):
        """Applies the style to a given text.
     *
     * @param string text The text to style
     *
     * @return string

        """

        codes = list();

        if (None is not self.__foreground) :
            codes.append(self.__foreground);

        if (None is not self.__background) :
            codes.append(self.__background);

        if self.__options :
            codes.extend(self.__options);


        if not codes:
            return text;


        return "\033[{0}m{1}\033[0m".format(';'.join(codes), text);


class OutputFormatterStyleStack():
    """@author Jean-François Simon <contact@jfsimon.fr>

    """



    def __init__(self, emptyStyle = None):
        """Constructor.
     *
     * @param OutputFormatterStyleInterface emptyStyle

        """
        if emptyStyle:
            assert isinstance(emptyStyle, OutputFormatterStyleInterface);

        # @var OutputFormatterStyleInterface[]
        self.__styles = None;

        # @var OutputFormatterStyleInterface
        self.__emptyStyle = None;

        if None is emptyStyle:
            self.__emptyStyle = OutputFormatterStyle();
        self.reset();


    def reset(self):
        """Resets stack (ie. empty internal arrays).

        """

        self.__styles = list();


    def push(self, style):
        """Pushes a style in the stack.
     *
     * @param OutputFormatterStyleInterface style

        """
        assert isinstance(style, OutputFormatterStyleInterface);

        self.__styles.append(style);


    def pop(self, style = None):
        """Pops a style from the stack.
     *
     * @param OutputFormatterStyleInterface style
     *
     * @return OutputFormatterStyleInterface
     *
     * @raise InvalidArgumentException  When style tags incorrectly nested

        """
        if style:
            assert isinstance(style, OutputFormatterStyleInterface);

        if not self.__styles :
            return self.__emptyStyle;


        if (None is style) :
            return self.__styles.pop();

        rstyles = self.__styles[:];
        rstyles.reverse();
        index = len(rstyles);

        for stackedStyle in rstyles:
            index -= 1;
            if style.apply('') == stackedStyle.apply(''):
                self.__styles = self.__styles[0:index];
                return stackedStyle;

        raise InvalidArgumentException('Incorrectly nested style tag found.');


    def getCurrent(self):
        """Computes current style with stacks top codes.
     *
     * @return OutputFormatterStyle

        """

        if not self.__styles :
            return self.__emptyStyle;


        return self.__styles[-1];


    def setEmptyStyle(self, emptyStyle):
        """@param OutputFormatterStyleInterface emptyStyle
     *
     * @return OutputFormatterStyleStack

        """
        assert isinstance(emptyStyle, OutputFormatterStyleInterface);

        self.__emptyStyle = emptyStyle;

        return self;


    def getEmptyStyle(self):
        """@return OutputFormatterStyleInterface

        """

        return self.__emptyStyle;

