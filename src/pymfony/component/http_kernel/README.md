HttpKernel Component
====================

HttpKernel provides the building blocks to create flexible and fast HTTP-based
frameworks.


Resources
---------

You can run the unit tests with the following command:

    $ cd path/to/pymfony/component/http_kernel/
    $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python virtualenv.py vendor
    $ vendor/bin/pip install -r requirements.txt -e . nose
    $ vendor/bin/nosetests
