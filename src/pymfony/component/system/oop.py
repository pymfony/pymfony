# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

from __future__ import absolute_import;

import sys;
import abc;
import inspect;

"""
"""

__all__ = [
    'abstract',
    'interface',
    'final',
];

class OOPMeta(abc.ABCMeta):
    def __new__(cls, name, bases, namespace):
        cls = abc.ABCMeta.__new__(cls, name, bases, namespace);
        abstracts = set(cls.__abstractmethods__);
        # Compute set of abstract method names
        for name, value in namespace.items():
            if getattr(value, "__isabstractmethod__", False):
                abstracts.add(name);
        for base in bases:
            for name in getattr(base, "__interfacemethods__", set()):
                value = getattr(cls, name, None);
                if getattr(value, "__isabstractmethod__", False):
                    abstracts.add(name);
        cls.__abstractmethods__ = frozenset(abstracts);

        finals = set();
        for name, value in namespace.items():
            if getattr(value, "__isfinalmethod__", False):
                finals.add(name);
        for base in bases:
            if getattr(base, "__isfinalclass__", False):
                raise TypeError(
                    "Class {0} may not inherit from final class ({1})"
                    "".format(
                        cls.__module__+'.'+cls.__name__,
                        base.__module__+'.'+base.__name__
                    )
                );
            for name in getattr(base, "__finalmethods__", set()):
                if name in namespace:
                    raise TypeError(
                        "Cannot override final method {0}.{1}()"
                        "".format(base.__module__+'.'+base.__name__, name)
                    );

        cls.__finalmethods__ = frozenset(finals);

        return cls

def abstractclass(obj):
    """Decorator"""
    obj.__abstractclass__ = obj;
    return obj;

def interface(obj):
    """Decorator"""
    if not isinstance(obj, type(OOPMeta)):
        return obj;

    absMethods = set();

    for name, method in obj.__dict__.items():
        if inspect.isfunction(method):
            absMethods.add(name);
            setattr(obj, name, abc.abstractmethod(method));

    obj.__interfacemethods__ = frozenset(absMethods);

    return abstractclass(obj);

def abstract(obj):
    """Decorator"""
    if inspect.isfunction(obj):
        return  abc.abstractmethod(obj);
    elif isinstance(obj, type(OOPMeta)):
        return abstractclass(obj);
    return obj;

def finalclass(obj):
    """Decorator"""
    obj.__isfinalclass__ = True;
    return obj;

def finalmethod(obj):
    """Decorator"""
    obj.__isfinalmethod__ = True;
    return obj;

def final(obj):
    """Decorator"""
    if inspect.isfunction(obj):
        return  finalmethod(obj);
    elif isinstance(obj, type(OOPMeta)):
        return finalclass(obj);
    return obj;
