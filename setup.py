#!/usr/bin/python
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

from distutils.core import setup;
import os;

realpathfile = os.path.realpath(os.path.dirname(__file__));
os.chdir(realpathfile);

f = open("README.md");
long_description = f.read();
f.close();

packages = [
    'pymfony',
    'pymfony.component',
    'pymfony.component.config',
    'pymfony.component.config.definition',
    'pymfony.component.dependency',
    'pymfony.component.kernel',
    'pymfony.component.system',
];

classifiers = [
    'Framework :: Pymfony',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python 2.6',
    'Programming Language :: Python 2.7',
];

setup(
    name='Pymfony',
    packages=packages,
    package_dir = {'': 'src'},
    version="0.1.0",
    long_description=long_description,
    description="The Symfony2 PHP Framework with Python language",
    license="MIT",
    url="http://alquerci.github.com/pymfony",
    download_url="https://github.com/alquerci/pymfony/tarball/master",
    author="Alexandre Quercia",
    author_email="alquerci@email.com",
    maintainer="Alexandre Quercia",
    maintainer_email="alquerci@email.com",
    platforms="all",
    provides=packages,
    keywords="framework",
    classifiers=classifiers,
);
