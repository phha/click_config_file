Click config file
=================

Easily add configuration file support to your
`Click <http://click.pocoo.org/5/>`_ applications by adding a single
no-arguments decorator.

Basic usage
-----------

click-config-file is designed to be a usable by simply adding the
appropriate decorator to your command without having to supply any
mandatory arguments. It comes with a set of sensible defaults that
should just work for most cases.

Given this application:

.. code-block:: python

    @click.command()
    @click.option('--name', default='World', help='Who to greet.')
    @click_config_file.configuration_option()
    def hello(name):
        click.echo('Hello {}!'.format(name))

Running ``hello --help`` will give you this::

    Usage: hello [OPTIONS]

    Options:
      --name TEXT    Who to greet.
      --config PATH  Read configuration from PATH.
      --help         Show this message and exit.

If the configuration file does not exist, running ``hello`` will do what
you expect::

    Hello World!

With this configuration file::

    name="Universe"

Calling ``hello`` will also do what you expect::

    Hello Universe!

Calling ``hello --name Multiverse`` will override the configuration file
setting, as it should::

    Hello Multiverse!

The default name for the configuration file option is ``--config``. If no
``--config`` option is provided either via CLI or an environment variable,
the module will search for a file named `config` in the appropriate
directory for your OS.

Command line and environment options will override the configuration
file options. Configuration file options override default options. So
the resolution order for a given option is: CLI > Environment >
Configuration file > Default.

Supported file formats
----------------------

By default click-config-file supports files formatted according to
`Configobj's unrepr
mode <http://configobj.readthedocs.io/en/latest/configobj.html#unrepr-mode>`_.

You can add support for additional configuration providers by setting
the `provider` keyword argument. This argument expects a callable that
will take the configuration file path and command name as arguments and
returns a dictionary with the provided configuration options.

The command name is passed in order to allow for a shared configuration
file divided by sections for each command.

For example, this will read the configuration options from a shared JSON
file:

.. code-block:: python

    def myprovider(file_path, cmd_name):
        with open(file_path) as config_data:
            return json.load(config_data)[cmd_name]
    
    @click.command()
    @click.option('--name', default='World')
    @click_config_file.configuration_option(provider=myprovider)
    def hello(name):
        click.echo('Hello {}!'.format(name))


Installation
------------

``pip install click-config-file``

Why?
----

There are several existing implementations of config file support for
Click, however they seem to lack one or more of the following features:

-   Sensible defaults
-   Proper handling of resolution order
-   Support for multi value options, multiple options or a combination
    of both

In contrast this module may lack some more sophisticated features of the
other implementations. This is a deliberate choice as this module is
intended to be a simple option that Just Works with sensible defaults.
