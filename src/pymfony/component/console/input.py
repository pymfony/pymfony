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

import sys
from xml.dom.minidom import Document
import json
import re

from pymfony.component.system import Array
from pymfony.component.system import Tool
from pymfony.component.system import interface;
from pymfony.component.system import Object;
from pymfony.component.system import abstract;
from pymfony.component.system.exception import RuntimeException;
from pymfony.component.system.exception import InvalidArgumentException;
from pymfony.component.system.exception import LogicException;

@interface
class InputInterface(Object):
    """InputInterface is the interface implemented by all input classes.
    """

    def getFirstArgument(self):
        """Returns the first argument from the raw parameters (not parsed).

        @return: string The value of the first argument or None otherwise
        """
        pass;

    def hasParameterOption(self, values):
        """Returns True if the raw parameters (not parsed) contain a value.

        This method is to be used to introspect the input parameters
        before they have been validated. It must be used carefully.

        @param values: string|list The values to look for in the raw
                                   parameters (can be a list)

        @return: Boolean True if the value is contained in the raw parameters
        """
        pass;

    def getParameterOption(self, values, default=False):
        """Returns the value of a raw option (not parsed).

        This method is to be used to introspect the input parameters
        before they have been validated. It must be used carefully.

        @param values: string|list The value(s) to look for in the raw
                                   parameters (can be a list)
        @param default:      mixed The default value to return if no result is
                                   found

        @return: mixed The option value
        """
        pass;

    def bind(self, definition):
        """Binds the current Input instance with the given arguments and options.

        @param definition: InputDefinition A InputDefinition instance
        """
        pass;

    def validate(self):
        """Validates if arguments given are correct.

        Throws an exception when not enough arguments are given.

        @raise RuntimeException:
        """
        pass;

    def getArguments(self):
        """Returns all the given arguments merged with the default values.

        @return: dict
        """
        pass;

    def getArgument(self, name):
        """Gets argument by name.

        @param: name: string The name of the argument

        @return: mixed
        """
        pass;

    def setArgument(self, name, value):
        """Sets an argument value by name.

        @param name: string The argument name
        @param value: string The argument value

        @raise InvalidArgumentException: When argument given doesn't exist
        """
        pass;

    def hasArgument(self, name):
        """Returns True if an InputArgument object exists by name or position.

        @param name: string|integer The InputArgument name or position

        @return: Boolean True if the InputArgument object exists,
                         False otherwise
        """
        pass;

    def getOptions(self):
        """Returns all the given options merged with the default values.

        @return: dict
        """
        pass;

    def getOption(self, name):
        """Gets an option by name.

        @param name: string The name of the option

        @return: mixed
        """
        pass;

    def setOption(self, name, value):
        """Sets an option value by name.

        @param name: string The option name
        @param value: string The option value

        @raise InvalidArgumentException: When option given doesn't exist
        """
        pass;

    def hasOption(self, name):
        """Returns True if an InputOption object exists by name.

        @param string name: The InputOption name

        @return: Boolean True if the InputOption object exists, False otherwise
        """
        pass;

    def isInteractive(self):
        """Is this input means interactive?

        @return: Boolean
        """
        pass;

    def setInteractive(self, interactive):
        """Sets the input interactivity.

        @param Boolean interactive: If the input should be interactive
        """
        pass;

@abstract
class Input(InputInterface):
    """Input is the base class for all concrete Input classes.

    Three concrete classes are provided by default:

    * `ArgvInput`: The input comes from the CLI arguments (argv)
    * `StringInput`: The input is provided as a string
    * `ArrayInput`: The input is provided as an array

    @author Fabien Potencier <fabien@symfony.com>
    """


    def __init__(self, definition = None):
        """Constructor.

        @param InputDefinition definition A InputDefinition instance
        """
        if definition:
            assert isinstance(definition, InputDefinition);

        self._definition = None;
        self._options = None;
        self._arguments = None;
        self._interactive = True;

        if (None is definition):
            self._arguments = dict();
            self._options = dict();
            self._definition = InputDefinition();
        else:
            self.bind(definition);
            self.validate();



    def bind(self, definition):
        """Binds the current Input instance with the given arguments and options.
     *
     * @param InputDefinition definition A InputDefinition instance

        """
        assert isinstance(definition, InputDefinition);


        self._arguments = dict();
        self._options = dict();
        self._definition = definition;

        self._parse();


    @abstract
    def _parse(self):
        """Processes command line arguments.

        """

    def validate(self):
        """Validates the input.
     *
     * @raise RuntimeException When not enough arguments are given

        """

        if (len(self._arguments) < self._definition.getArgumentRequiredCount()):
            raise RuntimeException('Not enough arguments.');



    def isInteractive(self):
        """Checks if the input is interactive.
     *
     * @return Boolean Returns True if the input is interactive

        """

        return self._interactive;


    def setInteractive(self, interactive):
        """Sets the input interactivity.
     *
     * @param Boolean interactive If the input should be interactive

        """

        self._interactive = bool(interactive);


    def getArguments(self):
        """Returns the argument values.
     *
     * @return array An array of argument values

        """
        args = dict();
        args.update(self._definition.getArgumentDefaults());
        args.update(self._arguments);
        return args;


    def getArgument(self, name):
        """Returns the argument value for a given argument name.
     *
     * @param string name The argument name
     *
     * @return mixed The argument value
     *
     * @raise InvalidArgumentException When argument given doesn't exist

        """

        if ( not self._definition.hasArgument(name)):
            raise InvalidArgumentException(
                'The "{0}" argument does not exist.'.format(name)
            );

        if name in self._arguments:
            return self._arguments[name];
        else:
            return self._definition.getArgument(name).getDefault();



    def setArgument(self, name, value):
        """Sets an argument value by name.
     *
     * @param string name  The argument name
     * @param string value The argument value
     *
     * @raise InvalidArgumentException When argument given doesn't exist

        """

        if ( not self._definition.hasArgument(name)):
            raise InvalidArgumentException(
                'The "{0}" argument does not exist.'.format(name)
            );


        self._arguments[name] = value;


    def hasArgument(self, name):
        """Returns True if an InputArgument object exists by name or position.
     *
     * @param string|integer name The InputArgument name or position
     *
     * @return Boolean True if the InputArgument object exists, False otherwise

        """

        return self._definition.hasArgument(name);


    def getOptions(self):
        """Returns the options values.
     *
     * @return array An array of option values

        """
        args = dict();
        args.update(self._definition.getOptionDefaults());
        args.update(self._options);
        return args;


    def getOption(self, name):
        """Returns the option value for a given option name.
     *
     * @param string name The option name
     *
     * @return mixed The option value
     *
     * @raise InvalidArgumentException When option given doesn't exist

        """

        if ( not self._definition.hasOption(name)):
            raise InvalidArgumentException(
                'The "{0}" option does not exist.'.format(name)
            );


        if name in self._options:
            return self._options[name];
        else:
            return self._definition.getOption(name).getDefault();



    def setOption(self, name, value):
        """Sets an option value by name.
     *
     * @param string name  The option name
     * @param string value The option value
     *
     * @raise InvalidArgumentException When option given doesn't exist

        """

        if ( not self._definition.hasOption(name)):
            raise InvalidArgumentException(
                'The "{0}" option does not exist.'.format(name)
            );


        self._options[name] = value;


    def hasOption(self, name):
        """Returns True if an InputOption object exists by name.
     *
     * @param string name The InputOption name
     *
     * @return Boolean True if the InputOption object exists, False otherwise

        """

        return self._definition.hasOption(name);



class InputDefinition(Object):
    """A InputDefinition represents a set of valid command line arguments and options.
 *
 * Usage:
 *
 *     definition = InputDefinition([
 *       InputArgument('name', InputArgument.REQUIRED),
 *       InputOption('foo', 'f', InputOption.VALUE_REQUIRED),
 *     ]);
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """

    XML_INDENT = " "*2;
    XML_NL = "\n";
    XML_CHARSET = "UTF-8";

    def __init__(self, definition = list()):
        """Constructor.
     *
     * @param list definition A list of InputArgument and InputOption instance
     *
     * @api

        """
        assert isinstance(definition, list);

        self.__arguments = None; # dict[name] = InputArgument
        self.__argumentsIndex = None; # name[] list of argument name
        self.__requiredCount = None;
        self.__hasAnArrayArgument = False;
        self.__hasOptional = None;
        self.__options = None;
        self.__shortcuts = None;

        self.setDefinition(definition);


    def setDefinition(self, definition):
        """Sets the definition of the input.
     *
     * @param list definition The definition list
     *
     * @api

        """
        assert isinstance(definition, list);


        arguments = list();
        options = list();
        for item in definition:
            if (isinstance(item, InputOption)) :
                options.append(item);
            else :
                arguments.append(item);



        self.setArguments(arguments);
        self.setOptions(options);


    def setArguments(self, arguments = list()):
        """Sets the InputArgument objects.
     *
     * @param InputArgument[] arguments An array of InputArgument objects
     *
     * @api

        """

        self.__arguments          = dict();
        self.__argumentsIndex     = list();
        self.__requiredCount      = 0;
        self.__hasOptional        = False;
        self.__hasAnArrayArgument = False;
        self.addArguments(arguments);


    def addArguments(self, arguments = list()):
        """Adds an array of InputArgument objects.
     *
     * @param InputArgument[] arguments A list of InputArgument objects
     *
     * @api

        """
        assert isinstance(arguments, list);

        if arguments:
            for argument in arguments:
                self.addArgument(argument);




    def addArgument(self, argument):
        """Adds an InputArgument object.
     *
     * @param InputArgument argument An InputArgument object
     *
     * @raise LogicException When incorrect argument is given
     *
     * @api

        """
        assert isinstance(argument, InputArgument);


        if argument.getName() in self.__argumentsIndex :
            raise LogicException(
                'An argument with name "{0}" already exists.'
                ''.format(argument.getName())
            );


        if (self.__hasAnArrayArgument) :
            raise LogicException('Cannot add an argument after an array argument.');


        if (argument.isRequired() and self.__hasOptional) :
            raise LogicException('Cannot add a required argument after an optional one.');


        if (argument.isArray()) :
            self.__hasAnArrayArgument = True;


        if (argument.isRequired()) :
            self.__requiredCount+=1;
        else :
            self.__hasOptional = True;


        self.__arguments[argument.getName()] = argument;
        self.__argumentsIndex.append(argument.getName());


    def getArgument(self, name):
        """Returns an InputArgument by name or by position.
     *
     * @param string|integer name The InputArgument name or position
     *
     * @return InputArgument An InputArgument object
     *
     * @raise InvalidArgumentException When argument given doesn't exist
     *
     * @api

        """

        if ( not self.hasArgument(name)) :
            raise InvalidArgumentException(
                'The "{0}" argument does not exist.'.format(name)
            );

        if isinstance(name, int):
            return self.__arguments[self.__argumentsIndex[name]];

        return self.__arguments[name];



    def hasArgument(self, name):
        """Returns True if an InputArgument object exists by name or position.:
     *
     * @param string|integer name The InputArgument name or position
     *
     * @return Boolean True if the InputArgument object exists, False otherwise:
     *
     * @api

        """
        if isinstance(name, int):
            return name >= 0 and name < len(self.__argumentsIndex);

        return name in self.__argumentsIndex;



    def getArguments(self):
        """Gets the array of InputArgument objects.
     *
     * @return InputArgument[] A dict of InputArgument objects
     *
     * @api

        """

        return self.__arguments;


    def getArgumentCount(self):
        """Returns the number of InputArguments.
     *
     * @return integer The number of InputArguments

        """

        if self.__hasAnArrayArgument:
            return sys.maxsize;
        else:
            return len(self.__arguments);


    def getArgumentRequiredCount(self):
        """Returns the number of required InputArguments.
     *
     * @return integer The number of required InputArguments

        """

        return self.__requiredCount;


    def getArgumentDefaults(self):
        """Gets the default values.
     *
     * @return dict An dict of default values

        """

        values = dict();
        for argument in self.__arguments.values():
            values[argument.getName()] = argument.getDefault();


        return values;


    def setOptions(self, options = list()):
        """Sets the InputOption objects.
     *
     * @param InputOption[] options A list of InputOption objects
     *
     * @api

        """

        self.__options = dict();
        self.__shortcuts = dict();
        self.addOptions(options);


    def addOptions(self, options = list()):
        """Adds an array of InputOption objects.
     *
     * @param InputOption[] options A list of InputOption objects
     *
     * @api

        """

        for option in options:
            self.addOption(option);



    def addOption(self, option):
        """Adds an InputOption object.
     *
     * @param InputOption option An InputOption object
     *
     * @raise LogicException When option given already exist
     *
     * @api

        """
        assert isinstance(option, InputOption);


        if (option.getName() in self.__options.keys() and not option.equals(self.__options[option.getName()])) :
            raise LogicException(
                'An option named "{0}" already exists.'.format(option.getName())
            );
        elif (option.getShortcut() in self.__shortcuts.keys() and  not option.equals(self.__options[self.__shortcuts[option.getShortcut()]])) :
            raise LogicException(
                'An option with shortcut "{0}" already exists.'
                ''.format(option.getShortcut())
            );


        self.__options[option.getName()] = option;
        if (option.getShortcut()) :
            self.__shortcuts[option.getShortcut()] = option.getName();



    def getOption(self, name):
        """Returns an InputOption by name.
     *
     * @param string name The InputOption name
     *
     * @return InputOption A InputOption object
     *
     * @raise InvalidArgumentException When option given doesn't exist
     *
     * @api

        """

        if ( not self.hasOption(name)) :
            raise InvalidArgumentException(
                'The "--{0}" option does not exist.'.format(name)
            );


        return self.__options[name];


    def hasOption(self, name):
        """Returns True if an InputOption object exists by name.:
     *
     * @param string name The InputOption name
     *
     * @return Boolean True if the InputOption object exists, False otherwise:
     *
     * @api

        """

        return name in self.__options.keys();


    def getOptions(self):
        """Gets the array of InputOption objects.
     *
     * @return InputOption[] An dict of InputOption objects
     *
     * @api

        """

        return self.__options;


    def hasShortcut(self, name):
        """Returns True if an InputOption object exists by shortcut.:
     *
     * @param string name The InputOption shortcut
     *
     * @return Boolean True if the InputOption object exists, False otherwise:

        """

        return name in self.__shortcuts.keys();


    def getOptionForShortcut(self, shortcut):
        """Gets an InputOption by shortcut.
     *
     * @param string shortcut the Shortcut name
     *
     * @return InputOption An InputOption object

        """

        return self.getOption(self.__shortcutToName(shortcut));


    def getOptionDefaults(self):
        """Gets an array of default values.
     *
     * @return array An array of all default values

        """

        values = dict();
        for  option in self.__options.values():
            values[option.getName()] = option.getDefault();


        return values;


    def __shortcutToName(self, shortcut):
        """Returns the InputOption name given a shortcut.
     *
     * @param string shortcut The shortcut
     *
     * @return string The InputOption name
     *
     * @raise InvalidArgumentException When option given does not exist

        """

        if shortcut not in self.__shortcuts.keys() :
            raise InvalidArgumentException(
                'The "-{0}" option does not exist.'.format(shortcut)
            );


        return self.__shortcuts[shortcut];


    def getSynopsis(self):
        """Gets the synopsis.
     *
     * @return string The synopsis

        """

        elements = list();
        for option in self.getOptions().values():
            if option.getShortcut():
                shortcut = '-{0}|'.format(option.getShortcut());
            else:
                shortcut = '';

            if option.isValueRequired():
                value = '{0}--{1}="..."';
            elif option.isValueOptional():
                value = '{0}--{1}[="..."]';
            else:
                value = '{0}--{1}';
            elements.append(str('['+value+']').format(shortcut, option.getName()));


        for argument in self.getArguments().values():
            if argument.isRequired():
                value = '{0}';
            else:
                value = '[{0}]';

            if argument.isArray():
                arr = '1';
            else:
                arr = '';

            elements.append(value.format(argument.getName()+arr));

            if (argument.isArray()) :
                elements.append('... [{0}N]'.format(argument.getName()));



        return ' '.join(elements);


    def asText(self):
        """Returns a textual representation of the InputDefinition.
     *
     * @return string A string representing the InputDefinition

        """

        # find the largest option or argument name
        maxi = 0;
        for option in self.getOptions().values():
            nameLength = len(option.getName()) + 2;
            if (option.getShortcut()) :
                nameLength += len(option.getShortcut()) + 3;


            maxi = max(maxi, nameLength);

        for argument in self.getArguments().values():
            maxi = max(maxi, len(argument.getName()));

        ++maxi;

        text = list();

        if (self.getArguments()) :
            text.append('<comment>Arguments:</comment>');
            for argument in self.getArguments().values():
                if (None is not argument.getDefault() and ( not isinstance(argument.getDefault(), list) or len(argument.getDefault()))) :
                    default = '<comment> (default: {0})</comment>'.format(self.__formatDefaultValue(argument.getDefault()));
                else :
                    default = '';


                description = argument.getDescription().replace("\n", "\n"+' ' * (maxi + 2));
                name = argument.getName()+' '*(maxi+2-len(argument.getName()));
                text.append(" <info>{0}</info> {1}{2}".format(name, description, default));


            text.append('');


        if (self.getOptions()) :
            text.append('<comment>Options:</comment>');

            for option in self.getOptions().values():
                if (option.acceptValue() and None is not option.getDefault() and ( not isinstance(option.getDefault(), list) or len(option.getDefault()))) :
                    default = '<comment> (default: {0})</comment>'.format(self.__formatDefaultValue(option.getDefault()));
                else :
                    default = '';

                if option.isArray():
                    multiple = '<comment> (multiple values allowed)</comment>';
                else:
                    multiple = '';

                description = option.getDescription().replace("\n", "\n"+' ' * (maxi + 2));

                if option.getShortcut():
                    shortcut = '(-{0}) '.format(option.getShortcut());
                else: 
                    shortcut = '';
                optionMax = maxi - len(option.getName()) - len(shortcut) - 1;
                text.append(" <info>{0}</info> {1}{2}{3}{4}".format(
                    '--'+option.getName(),
                    shortcut+' '*optionMax,
                    description,
                    default,
                    multiple
                ));


            text.append('');


        return "\n".join(text);


    def asXml(self, asDom = False):
        """Returns an XML representation of the InputDefinition.
     *
     * @param Boolean asDom Whether to return a DOM or an XML string
     *
     * @return string|DOMDocument An XML string representing the InputDefinition

        """
        dom = Document();
        definitionXML = dom.createElement('definition');
        dom.appendChild(definitionXML);

        argumentsXML = dom.createElement('arguments');
        definitionXML.appendChild(argumentsXML);
        for argument in self.getArguments().values():
            argumentXML = dom.createElement('argument');
            argumentsXML.appendChild(argumentXML);
            argumentXML.setAttribute('name', argument.getName());
            argumentXML.setAttribute('is_required', str(int(argument.isRequired())));
            argumentXML.setAttribute('is_array', str(int(argument.isArray())));
            descriptionXML = dom.createElement('description');
            argumentXML.appendChild(descriptionXML);
            descriptionXML.appendChild(dom.createTextNode(argument.getDescription()));
            defaultsXML = dom.createElement('defaults');
            argumentXML.appendChild(defaultsXML);
            if isinstance(argument.getDefault(), dict):
                defaults = argument.getDefault().values();
            elif isinstance(argument.getDefault(), list):
                defaults = argument.getDefault();
            elif isinstance(argument.getDefault(), bool):
                defaults = [repr(argument.getDefault())];
            elif argument.getDefault():
                defaults = [argument.getDefault()];
            else:
                defaults = list();
            for default in defaults:
                defaultXML = dom.createElement('default');
                defaultsXML.appendChild(defaultXML);
                defaultXML.appendChild(dom.createTextNode(str(default)));


        optionsXML = dom.createElement('options');
        definitionXML.appendChild(optionsXML);
        for option in self.getOptions().values():
            optionXML = dom.createElement('option');
            optionsXML.appendChild(optionXML);
            optionXML.setAttribute('name', '--'+option.getName());
            if option.getShortcut():
                shortcut = '-'+option.getShortcut()
            else:
                shortcut = '';
            optionXML.setAttribute('shortcut', shortcut);
            
            if option.acceptValue():
                accept_value = 1;
            else:
                accept_value = 0;
            
            optionXML.setAttribute('accept_value', str(accept_value));
            optionXML.setAttribute('is_value_required', str(int(option.isValueRequired())));
            optionXML.setAttribute('is_multiple',str(int(option.isArray())));
            descriptionXML = dom.createElement('description');
            optionXML.appendChild(descriptionXML);
            descriptionXML.appendChild(dom.createTextNode(option.getDescription()));

            if (option.acceptValue()) :
                defaultsXML = dom.createElement('defaults');
                optionXML.appendChild(defaultsXML);

                if isinstance(option.getDefault(), dict):
                    defaults = option.getDefault().values();
                elif isinstance(option.getDefault(), list):
                    defaults = option.getDefault();
                elif isinstance(option.getDefault(), bool):
                    defaults = [repr(option.getDefault())];
                elif option.getDefault():
                    defaults = [option.getDefault()];
                else:
                    defaults = list();
                for default in defaults:
                    defaultXML = dom.createElement('default');
                    defaultsXML.appendChild(defaultXML);
                    defaultXML.appendChild(dom.createTextNode(str(default)));



        if asDom:
            return dom;
        else:
            return str(dom.toprettyxml(self.XML_INDENT, self.XML_NL, self.XML_CHARSET));


    def __formatDefaultValue(self, default):
        return json.dumps(default).replace('\/', '/');


class InputOption(Object):
    """Represents a command line option.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """

    VALUE_NONE     = 1;
    VALUE_REQUIRED = 2;
    VALUE_OPTIONAL = 4;
    VALUE_IS_ARRAY = 8;


    def __init__(self, name, shortcut = None, mode = None, description = '', default = None):
        """Constructor.
     *
     * @param string  name        The option name
     * @param string  shortcut    The shortcut (can be None)
     * @param integer mode        The option mode: One of the VALUE_* constants
     * @param string  description A description text
     * @param mixed   default     The default value (must be None for self.VALUE_REQUIRED or self.VALUE_NONE)
     *
     * @raise InvalidArgumentException If option mode is invalid or incompatible
     *
     * @api

        """
        self.__name = None;
        self.__shortcut = None;
        self.__mode = None;
        self.__default = None;
        self.__description = None;
        name = str(name);

        if name.startswith('--'):
            name = name[2:];


        if not name :
            raise InvalidArgumentException('An option name cannot be empty.');


        if not shortcut :
            shortcut = None;


        if (None is not shortcut) :
            shortcut = str(shortcut);
            if shortcut.startswith('-') :
                shortcut = shortcut[1:];


            if not shortcut :
                raise InvalidArgumentException('An option shortcut cannot be empty.');



        if (None is mode) :
            mode = self.VALUE_NONE;
        elif ( not isinstance(mode, int) or mode > 15 or mode < 1) :
            raise InvalidArgumentException(
                'Option mode "{0}" is not valid.'.format(mode)
            );


        self.__name        = name;
        self.__shortcut    = shortcut;
        self.__mode        = mode;
        self.__description = description;

        if (self.isArray() and  not self.acceptValue()) :
            raise InvalidArgumentException('Impossible to have an option mode VALUE_IS_ARRAY if the option does not accept a value.');


        self.setDefault(default);


    def getShortcut(self):
        """Returns the option shortcut.
     *
     * @return string The shortcut

        """

        return self.__shortcut;


    def getName(self):
        """Returns the option name.
     *
     * @return string The name

        """

        return self.__name;


    def acceptValue(self):
        """Returns True if the option accepts a value.:
     *
     * @return Boolean True if value mode is not self.VALUE_NONE, False otherwise:

        """

        return self.isValueRequired() or self.isValueOptional();


    def isValueRequired(self):
        """Returns True if the option requires a value.:
     *
     * @return Boolean True if value mode is self.VALUE_REQUIRED, False otherwise:

        """

        return self.VALUE_REQUIRED == (self.VALUE_REQUIRED & self.__mode);


    def isValueOptional(self):
        """Returns True if the option takes an optional value.:
     *
     * @return Boolean True if value mode is self.VALUE_OPTIONAL, False otherwise:

        """

        return self.VALUE_OPTIONAL == (self.VALUE_OPTIONAL & self.__mode);


    def isArray(self):
        """Returns True if the option can take multiple values.:
     *
     * @return Boolean True if mode is self.VALUE_IS_ARRAY, False otherwise:

        """

        return self.VALUE_IS_ARRAY == (self.VALUE_IS_ARRAY & self.__mode);


    def setDefault(self, default = None):
        """Sets the default value.
     *
     * @param mixed default The default value
     *
     * @raise LogicException When incorrect default value is given

        """

        if (self.VALUE_NONE == (self.VALUE_NONE & self.__mode) and None is not default) :
            raise LogicException('Cannot set a default value when using InputOption.VALUE_NONE mode.');


        if (self.isArray()) :
            if (None is default) :
                default = list();
            elif isinstance(default, dict) :
                default = list(default.values());
            elif ( not isinstance(default, list)) :
                raise LogicException('A default value for an array option must be a list or dict.');



        if self.acceptValue():
            self.__default = default;
        else:
            self.__default = False;


    def getDefault(self):
        """Returns the default value.
     *
     * @return mixed The default value

        """

        return self.__default;


    def getDescription(self):
        """Returns the description text.
     *
     * @return string The description text

        """

        return self.__description;


    def equals(self, option):
        """Checks whether the given option equals this one
     *
     * @param InputOption option option to compare
     * @return Boolean

        """
        assert isinstance(option, InputOption);


        return option.getName() == self.getName()\
            and option.getShortcut() == self.getShortcut()\
            and option.getDefault() == self.getDefault()\
            and option.isArray() == self.isArray()\
            and option.isValueRequired() == self.isValueRequired()\
            and option.isValueOptional() == self.isValueOptional()\
        ;



class InputArgument(Object):
    """Represents a command line argument.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """

    REQUIRED = 1;
    OPTIONAL = 2;
    IS_ARRAY = 4;


    def __init__(self, name, mode = None, description = '', default = None):
        """Constructor.
     *
     * @param string  name        The argument name
     * @param integer mode        The argument mode: self.REQUIRED or self.OPTIONAL
     * @param string  description A description text
     * @param mixed   default     The default value (for self.OPTIONAL mode only)
     *
     * @raise InvalidArgumentException When argument mode is not valid
     *
     * @api

        """
        self.__name = None;
        self.__mode = None;
        self.__default = None;
        self.__description = None;

        if (None is mode) :
            mode = self.OPTIONAL;
        elif ( not isinstance(mode, int) or mode > 7 or mode < 1) :
            raise InvalidArgumentException(
                'Argument mode "{0}" is not valid.'.format(mode)
            );





        self.__name        = name;
        self.__mode        = mode;
        self.__description = description;

        self.setDefault(default);


    def getName(self):
        """Returns the argument name.
     *
     * @return string The argument name

        """

        return self.__name;


    def isRequired(self):
        """Returns True if the argument is required.:
     *
     * @return Boolean True if parameter mode is self.REQUIRED, False otherwise:

        """

        return self.REQUIRED == (self.REQUIRED & self.__mode);


    def isArray(self):
        """Returns True if the argument can take multiple values.:
     *
     * @return Boolean True if mode is self.IS_ARRAY, False otherwise:

        """

        return self.IS_ARRAY == (self.IS_ARRAY & self.__mode);


    def setDefault(self, default = None):
        """Sets the default value.
     *
     * @param mixed default The default value
     *
     * @raise LogicException When incorrect default value is given

        """

        if (self.REQUIRED == self.__mode and None is not default) :
            raise LogicException('Cannot set a default value except for InputArgument.OPTIONAL mode.');


        if (self.isArray()) :
            if (None is default) :
                default = list();
            elif ( not isinstance(default, list)) :
                raise LogicException('A default value for an array argument must be a list.');



        self.__default = default;


    def getDefault(self):
        """Returns the default value.
     *
     * @return mixed The default value

        """

        return self.__default;


    def getDescription(self):
        """Returns the description text.
     *
     * @return string The description text

        """

        return self.__description;


class ArrayInput(Input):
    """ArrayInput represents an input provided as an array.
 *
 * Usage:
 *
 *     input = ArrayInput(array('name' => 'foo', '--bar' => 'foobar'));
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """


    def __init__(self, parameters, definition = None):
        """Constructor.
     *
     * @param array           parameters An array of parameters
     * @param InputDefinition definition A InputDefinition instance
     *
     * @api

        """
        if definition:
            assert isinstance(definition, InputDefinition);
        if isinstance(parameters, list):
            parameters = Array.toDict(parameters);
        assert isinstance(parameters, dict);

        self.__parameters = None;

        self.__parameters = parameters;

        Input.__init__(self, definition);


    def getFirstArgument(self):
        """Returns the first argument from the raw parameters (not parsed).
     *
     * @return string The value of the first argument or None otherwise

        """

        for key, value in self.__parameters.items():
            if (key and key.startswith('-')) :
                continue;


            return value;



    def hasParameterOption(self, values):
        """Returns True if the raw parameters (not parsed) contain a value.:
     *
     * This method is to be used to introspect the input parameters
     * before they have been validated. It must be used carefully.
     *
     * @param string|list values The values to look for in the raw parameters (can be an list)
     *
     * @return Boolean True if the value is contained in the raw parameters:

        """

        for k, v in self.__parameters.items():
            if not isinstance(k, int) :
                v = k;


            if v in values :
                return True;



        return False;


    def getParameterOption(self, values, default = False):
        """Returns the value of a raw option (not parsed).
     *
     * This method is to be used to introspect the input parameters
     * before they have been validated. It must be used carefully.
     *
     * @param string|list values  The value(s) to look for in the raw parameters (can be an list)
     * @param mixed        default The default value to return if no result is found:
     *
     * @return mixed The option value

        """

        values = list(values);

        for k, v in self.__parameters.items():
            if isinstance(k, int) and v in values :
                return True;
            elif k in values :
                return v;



        return default;


    def _parse(self):
        """Processes command line arguments.

        """

        for key, value in self.__parameters.items():
            if key.startswith('--') :
                self.__addLongOption(key[2:], value);
            elif key.startswith('-') :
                self.__addShortOption(key[1:], value);
            else :
                self.__addArgument(key, value);




    def __addShortOption(self, shortcut, value):
        """Adds a short option value.
     *
     * @param string shortcut The short option key
     * @param mixed  value    The value for the option
     *
     * @raise InvalidArgumentException When option given doesn't exist

        """

        if ( not self._definition.hasShortcut(shortcut)) :
            raise InvalidArgumentException(
                'The "-{0}" option does not exist.'.format(shortcut)
            );


        self.__addLongOption(self._definition.getOptionForShortcut(shortcut).getName(), value);


    def __addLongOption(self, name, value):
        """Adds a long option value.
     *
     * @param string name  The long option key
     * @param mixed  value The value for the option
     *
     * @raise InvalidArgumentException When option given doesn't exist
     * @raise InvalidArgumentException When a required value is missing

        """

        if ( not self._definition.hasOption(name)) :
            raise InvalidArgumentException(
                'The "--{0}" option does not exist.'.format(name)
            );



        option = self._definition.getOption(name);

        if (None is value) :
            if (option.isValueRequired()) :
                raise InvalidArgumentException(
                    'The "--{0}" option requires a value.'.format(name)
                );


            if option.isValueOptional():
                value = option.getDefault();
            else:
                value = True;

        self._options[name] = value;


    def __addArgument(self, name, value):
        """Adds an argument value.
     *
     * @param string name  The argument name
     * @param mixed  value The value for the argument
     *
     * @raise InvalidArgumentException When argument given doesn't exist

        """

        if ( not self._definition.hasArgument(name)) :
            raise InvalidArgumentException(
                'The "{0}" argument does not exist.'.format(name)
            );


        self._arguments[name] = value;



class ArgvInput(Input):
    """ArgvInput represents an input coming from the CLI arguments.
 *
 * Usage:
 *
 *     input = ArgvInput();
 *
 * By default, the `sys.argv` array is used for the input values.
 *
 * This can be overridden by explicitly passing the input values in the constructor:
 *
 *     input = ArgvInput(sys.argv);
 *
 * If you pass it yourself, don't forget that the first element of the array
 * is the name of the running application.
 *
 * When passing an argument to the constructor, be sure that it respects
 * the same rules as the argv one. It's almost always better to use the
 * `StringInput` when you want to provide your own input.
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @see    http://www.gnu.org/software/libc/manual/html_node/Argument-Syntax.html
 * @see    http://www.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap12.html#tag_12_02
 *
 * @api

    """


    def __init__(self, argv = None, definition = None):
        """Constructor.
     *
     * @param list            argv       A list of parameters from the CLI (in the argv format)
     * @param InputDefinition definition A InputDefinition instance
     *
     * @api

        """
        if definition:
            assert isinstance(definition, InputDefinition);

        self.__tokens = None;
        self.__parsed = None;

        if (None is argv) :
            argv = sys.argv;
        else:
            assert isinstance(argv, list);


        # strip the application name
        argv = argv[1:];

        self.__tokens = argv;

        Input.__init__(self, definition);


    def _setTokens(self, tokens):
        assert isinstance(tokens, list);

        self.__tokens = tokens;


    def _parse(self):
        """Processes command line arguments.

        """

        parseOptions = True;
        self.__parsed = self.__tokens[:];
        try:
            token = self.__parsed.pop(0);
            while (None is not token) :
                if (parseOptions and '' == token) :
                    self.__parseArgument(token);
                elif (parseOptions and '--' == token) :
                    parseOptions = False;
                elif parseOptions and token.startswith('--') :
                    self.__parseLongOption(token);
                elif parseOptions and token.startswith('-') :
                    self.__parseShortOption(token);
                else :
                    self.__parseArgument(token);
                token = self.__parsed.pop(0);
        except IndexError:
            pass;




    def __parseShortOption(self, token):
        """Parses a short option.
     *
     * @param string token The current token.

        """

        name = token[1:];

        if (len(name) > 1) :
            if (self._definition.hasShortcut(name[0]) and self._definition.getOptionForShortcut(name[0]).acceptValue()) :
                # an option with a value (with no space)
                self.__addShortOption(name[0], name[1:]);
            else :
                self.__parseShortOptionSet(name);

        else :
            self.__addShortOption(name, None);



    def __parseShortOptionSet(self, name):
        """Parses a short option set.
     *
     * @param string name The current token
     *
     * @raise RuntimeException When option given doesn't exist

        """

        lenght = len(name);
        for i in range(lenght):
            if ( not self._definition.hasShortcut(name[i])) :
                raise RuntimeException(
                    'The "-{0}" option does not exist.'.format(name[i])
                );


            option = self._definition.getOptionForShortcut(name[i]);
            if (option.acceptValue()) :
                if i == lenght - 1:
                    self.__addLongOption(option.getName(), None);
                else:
                    self.__addLongOption(option.getName(), name[i+1:]);

                break;
            else :
                self.__addLongOption(option.getName(), True);




    def __parseLongOption(self, token):
        """Parses a long option.
     *
     * @param string token The current token

        """

        name = token[2:];
        try:
            pos = name.index("=");
        except ValueError:
            pass;
        if '=' in name :
            self.__addLongOption(name[0:pos], name[pos + 1:]);
        else :
            self.__addLongOption(name, None);



    def __parseArgument(self, token):
        """Parses an argument.
     *
     * @param string token The current token
     *
     * @raise RuntimeException When too many arguments are given

        """

        c = len(self._arguments);

        # if input is expecting another argument, add it:
        if (self._definition.hasArgument(c)) :
            arg = self._definition.getArgument(c);
            if arg.isArray():
                self._arguments[arg.getName()] = [token];
            else:
                self._arguments[arg.getName()] = token;

        # if last argument isArray(), append token to last argument:
        elif (self._definition.hasArgument(c - 1) and self._definition.getArgument(c - 1).isArray()) :
            arg = self._definition.getArgument(c - 1);
            self._arguments[arg.getName()].append(token);

        # unexpected argument
        else :
            raise RuntimeException('Too many arguments.');



    def __addShortOption(self, shortcut, value):
        """Adds a short option value.
     *
     * @param string shortcut The short option key
     * @param mixed  value    The value for the option
     *
     * @raise RuntimeException When option given doesn't exist

        """

        if ( not self._definition.hasShortcut(shortcut)) :
            raise RuntimeException(
                'The "-{0}" option does not exist.'.format(shortcut));


        self.__addLongOption(self._definition.getOptionForShortcut(shortcut).getName(), value);


    def __addLongOption(self, name, value):
        """Adds a long option value.
     *
     * @param string name  The long option key
     * @param mixed  value The value for the option
     *
     * @raise RuntimeException When option given doesn't exist

        """

        if ( not self._definition.hasOption(name)) :
            raise RuntimeException(
                'The "--{0}" option does not exist.'.format(name));


        option = self._definition.getOption(name);

        if (None is value and option.acceptValue() and len(self.__parsed)) :
            # if option accepts an optional or mandatory argument:
            # let's see if there is one provided:
            nextv = self.__parsed.pop(0);
            if nextv and not nextv.startswith('-') :
                value = nextv;
            elif not nextv :
                value = '';
            else :
                self.__parsed.insert(0, nextv);



        if (None is value) :
            if (option.isValueRequired()) :
                raise RuntimeException(
                    'The "--{0}" option requires a value.'.format(name));

            if option.isValueOptional():
                value = option.getDefault();
            else:
                value = True;


        if (option.isArray()) :
            if name not in self._options:
                self._options[name] = list();
            self._options[name].append(value);
        else :
            self._options[name] = value;



    def getFirstArgument(self):
        """Returns the first argument from the raw parameters (not parsed).
     *
     * @return string The value of the first argument or None otherwise

        """

        for token in self.__tokens:
            if (token and token.startswith('-')) :
                continue;


            return token;



    def hasParameterOption(self, values):
        """Returns True if the raw parameters (not parsed) contain a value.:
     *
     * This method is to be used to introspect the input parameters
     * before they have been validated. It must be used carefully.
     *
     * @param string|list values The value(s) to look for in the raw parameters (can be an list)
     *
     * @return Boolean True if the value is contained in the raw parameters:

        """

        if isinstance(values, dict):
            values = values.values();
        elif not isinstance(values, list):
            values = [values];

        for v in self.__tokens:
            if v in values:
                return True;



        return False;


    def getParameterOption(self, values, default = False):
        """Returns the value of a raw option (not parsed).
     *
     * This method is to be used to introspect the input parameters
     * before they have been validated. It must be used carefully.
     *
     * @param string|list values  The value(s) to look for in the raw parameters (can be an list)
     * @param mixed        default The default value to return if no result is found:
     *
     * @return mixed The option value

        """

        if isinstance(values, dict):
            values = values.values();
        elif not isinstance(values, list):
            values = [values];

        tokens = self.__tokens[:];
        token = tokens.pop(0);
        while (token) :
            for value in values:
                if token.startswith(value) :
                    try:
                        pos = token.index("=");
                    except ValueError:
                        pass;
                    if '=' in token :
                        return token[pos + 1:];

                    return tokens.pop(0);
            token = tokens.pop(0);

        return default;



class StringInput(ArgvInput):
    """StringInput represents an input provided as a string.
 *
 * Usage:
 *
 *     input = StringInput('foo --bar="foobar"');
 *
 * @author Fabien Potencier <fabien@symfony.com>
 *
 * @api

    """

    REGEX_STRING = '([^ ]+?)(?: |(?<!\\\\)"|(?<!\\\\)\'|$)';
    REGEX_QUOTED_STRING = '(?:"([^"\\\\]*(?:\\\\.[^"\\\\]*)*)"|\'([^\'\\\\]*(?:\\\\.[^\'\\\\]*)*)\')';

    def __init__(self, inputString, definition = None):
        """Constructor.
     *
     * @param string          inputString      A string of parameters from the CLI
     * @param InputDefinition definition A InputDefinition instance
     *
     * @api

        """
        if definition is not None:
            assert isinstance(definition, InputDefinition);

        ArgvInput.__init__(self, list(), definition);

        self._setTokens(self.__tokenize(inputString));


    def __tokenize(self, inputString):
        """Tokenizes a string.
     *
     * @param string inputString The input to tokenize
     *
     * @return array An array of tokens
     *
     * @raise InvalidArgumentException When unable to parse input (should never happen)

        """

        inputString = re.sub('(\r\n|\r|\n|\t)', ' ', inputString);

        tokens = list();
        length = len(inputString);
        cursor = 0;
        while (cursor < length):
            s = inputString[cursor:];
            match = re.match('\s+', s);
            if (match) :
                cursor += len(match.group(0));continue;
            match = re.match('([^="\' ]+?)(=?)('+self.REGEX_QUOTED_STRING+'+)', s);
            if (match) :
                tokens.append(match.group(1)+match.group(2)+Tool.stripcslashes(match.group(3)[1:1+len(match.group(3)) - 2].replace('"\'', '').replace('\'"', '').replace('\'\'', '').replace('""', '')));
                cursor += len(match.group(0));continue;
            match = re.match(''+self.REGEX_QUOTED_STRING+'', s);
            if (match) :
                tokens.append(Tool.stripcslashes(match.group(0)[1:1+len(match.group(0)) - 2]));
                cursor += len(match.group(0));continue;
            match = re.match(''+self.REGEX_STRING+'', s);
            if (match) :
                tokens.append(Tool.stripcslashes(match.group(1)));
            else :
                # should never happen
                # @codeCoverageIgnoreStart
                raise InvalidArgumentException(
                    'Unable to parse input near "... {0} ..."'.format(input[cursor:cursor+10])
                );
                # @codeCoverageIgnoreEnd


            cursor += len(match.group(0));


        return tokens;


