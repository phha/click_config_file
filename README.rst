Click config file
=================

Easily add configuration file support to your
`Click <http://click.pocoo.org/5/>`_ applications by adding a single
no-arguments decorator.

.. image:: https://img.shields.io/pypi/v/click-config-file.svg?style=flat-square
    :target: https://pypi.org/project/click-config-file/
.. image:: https://img.shields.io/conda/vn/conda-forge/click-config-file.svg?style=flat-square
    :target: https://anaconda.org/conda-forge/click-config-file
.. image:: https://img.shields.io/travis/phha/click_config_file/master.svg?style=flat-square
    :target: https://travis-ci.org/phha/click_config_file
.. image:: https://img.shields.io/codacy/grade/a5f6262609314683bf2b2bc546bdaffe/master.svg?style=flat-square
    :target: https://www.codacy.com/app/phha/click_config_file

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

The default name for the configuration file option is ``--config``.

Command line and environment options will override the configuration
file options. Configuration file options override default options. So
the resolution order for a given option is: CLI > Environment >
Configuration file > Default.

Options
-------

Although ``configuration_option`` is designed to work without any mandatory
arguments, some optional parameters are supported:

``implicit``
  Default: ``True``

  By default ``configuration_option`` will look for a configuration file
  even if no value for the configuration option was provided either via
  a CLI argument or an environment variable. In this case the value will
  be set implicitly from ``cmd_name`` and ``config_file_name`` as
  described below.

  If set to ``False`` the configuration file settings will only be applied
  when a configuration file argument is provided.

``cmd_name``
  Default: ``ctx.info_name``

  The name of the decorated command. When implicitly creating a
  configuration file argument, the application directory containing the
  configuration file is resolved by calling ``click.get_app_dir(cmd_name)``.

  This defaults to the name of the command as determined by click.

``config_file_name``
  Default: ``config``

  When ``implicit`` is set to ``True``, this argument provides the name of the
  configuration file inside the application directory.

In addition to the arguments above, all arguments for ``click.option()`` and
``click.File()`` are supported.

Supported file formats
----------------------

By default click-config-file supports files formatted according to
`Configobj's unrepr
mode <http://configobj.readthedocs.io/en/latest/configobj.html#unrepr-mode>`_.

You can add support for additional configuration providers by setting
the ``provider`` keyword argument. This argument expects a callable that
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
