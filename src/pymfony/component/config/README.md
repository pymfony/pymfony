Config Component
================

Config provides the infrastructure for loading configurations from different
data sources and optionally monitoring these data sources for changes. There
are additional tools for validating, normalizing and handling of defaults that
can optionally be used to convert from different formats to arrays.

Resources
---------

You can run the unit tests with the following command:

    $ cd path/to/pymfony/component/yaml/
    $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python virtualenv.py vendor
    $ vendor/bin/pip install -r requirements.txt -e . nose
    $ vendor/bin/nosetests
