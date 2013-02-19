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

from pymfony.component.system.exception import StandardException;

class FileLoaderLoadException(StandardException):
    """Exception class for when a resource cannot be loaded or imported.
    """

    def __init__(self, resource, sourceResource=None, code=0, previous=None):
        if sourceResource is None:
            message = 'Cannot load resource "{0}".'.format(repr(resource));
        else:
            message = 'Cannot import resource "{0}" from "{1}".'.format(
                repr(resource), repr(sourceResource)
            );

        # Is the resource located inside a bundle?
        if resource.startswith('@'):
            bundle = str(resource).split('/', 1)[1:];
            message += ' Make sure the "{0}" bundle is correctly registered '
            'and loaded in the application kernel class.'
            ''.format(bundle);

        StandardException.__init__(self, message, code, previous);

class FileLoaderImportCircularReferenceException(FileLoaderLoadException):
    """Exception class for when a circular reference is detected when
    importing resources.
    """
    def __init__(self, resources, code=None, previous=None):
        """
        @param resources: list
        """
        assert isinstance(resources, list);

        message = ('Circular reference detected in "{0}" ("{1}" > "{2}").'
        ''.format(repr(resources[0]), " > ".join(resources), repr(resources[0])
        ));

        StandardException.__init__(self, message, code, previous);
