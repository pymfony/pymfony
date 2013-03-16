System Component
==============

System implements basics utilities.


Resources
---------

You can run the unit tests with the following command:

    $ cd path/to/pymfony/component/system/
    $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python virtualenv.py vendor
    $ vendor/bin/pip install -r requirements.txt -e . nose
    $ vendor/bin/nosetests
