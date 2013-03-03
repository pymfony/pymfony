EventDispatcher Component
=========================

EventDispatcher implements a lightweight version of the Observer design
pattern.

    from pymfony.component.event_dispatcher import EventDispatcher;
    from pymfony.component.event_dispatcher import Event;

    dispatcher = EventDispatcher();

    def func(event):
        assert isinstance(event, Event);

        # ...

    dispatcher.addListener('event_name', func);

    dispatcher.dispatch('event_name');

Resources
---------

You can run the unit tests with the following command:

    $ cd path/to/pymfony/component/yaml/
    $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python virtualenv.py vendor
    $ vendor/bin/pip install -r requirements.txt -e . nose
    $ vendor/bin/nosetests
