#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of the pymfony package.
#
# (c) Alexandre Quercia <alquerci@email.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
from __future__ import absolute_import;

import os;
from distutils.core import setup;

"""
"""

realpathfile = os.path.realpath(os.path.dirname(__file__));
os.chdir(realpathfile);

f = open("README.md");
long_description = "\n"+f.read();
f.close();

def find_packages():
    return [
        'pymfony',
        'pymfony.bundle',
        'pymfony.bundle.framework_bundle',
        'pymfony.bundle.framework_bundle.dependency',
        'pymfony.component',
        'pymfony.component.config',
        'pymfony.component.config.definition',
        'pymfony.component.console',
        'pymfony.component.console_kernel',
        'pymfony.component.console_routing',
        'pymfony.component.dependency',
        'pymfony.component.event_dispatcher',
        'pymfony.component.httpkernel',
        'pymfony.component.kernel',
        'pymfony.component.system',
        'pymfony.component.system.py2',
        'pymfony.component.system.py2.minor6',
        'pymfony.component.system.py3',
        'pymfony.component.yaml',
    ];

def find_package_data():
    return {
        '': [
            "Resources/config/*.*",
        ]
    };

setup(
    name="pymfony",
    version="0.1.0",
    package_dir={'': 'src'},
    packages=find_packages(),
    package_data=find_package_data(),
    author="Alexandre Quercia",
    author_email="alquerci@email.com",
    url="http://github.com/alquerci/pymfony",
    description='An implementation of "Symfony2 PHP Framework" into Python',
    long_description=long_description,
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
        "Topic :: Software Development :: Libraries :: PHP Classes",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
);
