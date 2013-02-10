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

from pymfony.component.system.exception import RuntimeException
from pymfony.component.system import Object;
from pymfony.component.system import interface

@interface
class CliExceptionInterface(Object):
    """Interface for CLI error exceptions.
 *
 * @author Kris Wallsmith <kris@symfony.com>

    """

    def getStatusCode(self):
        """Returns the status code.
     *
     * @return integer An CLI response status code

        """

class CliException(RuntimeException, CliExceptionInterface):
    """CliException.
 *
 * @author Kris Wallsmith <kris@symfony.com>

    """


    def __init__(self, statusCode, message = None, previous = None, code = 0):
        assert isinstance(previous, Exception);

        self.__statusCode = None;

        self.__statusCode = statusCode;

        RuntimeException.__init__(self, message, code, previous);


    def getStatusCode(self):

        return self.__statusCode;




class NotFoundCliException(CliException):
    """NotFoundCliException.
 *
 * @author Fabien Potencier <fabien@symfony.com>

    """

    def __init__(self, message = None, previous = None, code = 0):
        """Constructor.
     *
     * @param string     message  The internal exception message
     * @param Exception previous The previous exception
     * @param integer    code     The internal exception code

        """
        assert isinstance(previous, Exception);

        CliException.__init__(self, 1, message, previous, code);

