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

import sys;
if sys.version_info[0] == 2:
    from pymfony.component.system.py2 import *;
else:
    from pymfony.component.system.py3 import *;

__all__ = [
    'abstract',
    'interface',
    'Object',
    'final',
];


@interface
class SerializableInterface(Object):
    def serialize(self):
        pass;

    def unserialize(self, serialized):
        pass;

@interface
class ArrayAccessInterface(Object):
    """Interface to provide accessing objects as container.
    """
    def __getitem__(self, item):
        """Returns the value at specified item.

        `for` loops expect that an `IndexError` will be raised for illegal
        indexes to allow proper detection of the end of the sequence.

        @param item: mixed The item to retrieve.

        @raise IndexError: If of a value outside the set of indexes for the
                           sequence (after any special interpretation of
                           negative values).
        @raise TypeError: If key is of an inappropriate type.
        @raise KeyError: If key is missing (not in the container).
        """
        pass;

    def __setitem__(self, item, value):
        """Assigns a value to the specified item.

        @param item: mixed The item to assign the value to.
        @param value: mixed The value to set.
        """
        pass;

    def __delitem__(self, item):
        """Deletes an item.

        @param item: mixed The item to delete.
        """
        pass;

    def __contains__(self, item):
        """Whether a item exists

        This method is executed when using `in` and `not in`

        @param item: mixed An item to check for.

        @return: True on success or False on failure.
        """
        pass;

@interface
class TraversableInterface(Object):
    pass;

@interface
class IteratorInterface(TraversableInterface):
    def __iter__(self):
        """Return the iterator object itself.

        This is required to allow both containers and iterators to be used
        with the for and in statements.

        This method corresponds to the tp_iter slot of the type structure
        for Python objects in the Python/C API.

        @return: iterator

        @raise Exception: On failure.
        """
        pass;

    def next(self):
        """Return the next item from the container.

        This method corresponds to the tp_iternext slot of the type structure
        for Python objects in the Python/C API.

        @return: mixed The next item from the container.

        @raise StopIteration: If there are no further items.
        """
        pass;

@interface
class IteratorAggregateInterface(TraversableInterface):
    """Interface to create an external Iterator.
    """
    def __iter__(self):
        """Retrieve an external iterator.

        This method is called when an iterator is required for a container.

        @return: iterator|IteratorInterface|TraversableInterface

        @raise Exception: On failure.
        """
        pass;

@interface
class CountableInterface(Object):
    """Classes implementing CountableInterface can be used with the len()
    function.
    """
    def __len__(self):
        """This method is executed when using the len() function.

        @return: integer The length of the object (>= 0).
        """
        pass;



@abstract
class Array(Object):
    @classmethod
    def toDict(cls, l, strKeys=False):
        assert isinstance(l, list);
        d = dict();
        i = 0;
        for i in range(len(l)):
            if strKeys:
                d[str(i)] = l[i];
            else:
                d[i] = l[i];
            i = i + 1;
        return d;

    @classmethod
    def uniq(cls, iterable):
        assert isinstance(iterable, (list, dict));
        if isinstance(iterable, list):
            d = cls.toDict(iterable);
            result = [];
            def append(k, v):
                result.append(v);
        else:
            d = iterable;
            result = {};
            def append(k, v):
                result[k] = v;

        pairs = list();
        for k, v in d.items():
            pairs.append((k, v));
        seen = {};
        for k, v in pairs:
            marker = v;
            if marker not in seen.keys():
                seen[marker] = 1;
                append(k, v);

        return result;

    @classmethod
    def diff(cls, leftSide, rightSide):
        """Computes the difference of lists

        @param leftSide: list The list to compare from
        @param rightSide: list The list to compare against

        @return: list
        """
        leftSide = list(leftSide);
        rightSide = list(rightSide);
        return [item for item in leftSide if item not in rightSide];
