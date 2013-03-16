Yaml Component
==============

YAML implements most of the YAML 1.2 specification.

    from pymfony.component.yaml import Yaml;

    array = Yaml.parse(filename);

    print(Yaml.dump(array));

Resources
---------

You can run the unit tests with the following command:

    $ cd path/to/pymfony/component/yaml/
    $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python virtualenv.py vendor
    $ vendor/bin/pip install -r requirements.txt
    $ vendor/bin/pip install nose
    $ vendor/bin/nosetests
