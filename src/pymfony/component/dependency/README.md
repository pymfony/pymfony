Dependency Component
====================

DependencyInjection manages your services via a robust and flexible Dependency
Injection Container.

Here is a simple example that shows how to register services and parameters:

    from pymfony.component.dependency import ContainerBuilder;
    from pymfony.component.dependency.definition import Reference;

    sc = ContainerBuilder();
    sc.register('foo', '%foo.class%');
    sc.addArgument(Reference('bar'));
    sc.setParameter('foo.class', 'Foo');

    sc.get('foo');

Method Calls (Setter Injection):

    sc = ContainerBuilder();

    sc.register('bar', '%bar.class%');
    sc.addMethodCall('setFoo', [Reference('foo')]);
    sc.setParameter('bar.class', 'Bar');

    sc.get('bar');

Factory Class:

If your service is retrieved by calling a static method:

    sc = ContainerBuilder();

    sc.register('bar', '%bar.class%');
    sc.setFactoryClass('%bar.class%');
    sc.setFactoryMethod('getInstance');
    sc.addArgument('Aarrg!!!');

    sc.setParameter('bar.class', 'Bar');

    sc.get('bar');

File Include:

For some services, especially those that are difficult or impossible to
autoload, you may need the container to include a file before
instantiating your class.

    sc = ContainerBuilder();

    sc.register('bar', '%bar.class%');
    sc.setFile('/path/to/file');
    sc.addArgument('Aarrg!!!');

    sc.setParameter('bar.class', 'Bar');

    sc.get('bar');

Resources
---------

You can run the unit tests with the following command:

    $ cd path/to/pymfony/component/dependency/
    $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python virtualenv.py vendor
    $ vendor/bin/pip install -r requirements.txt -e . nose
    $ vendor/bin/nosetests
