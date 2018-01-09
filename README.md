Click config file
=================

This module provides configuration file support for
[Click](http://click.pocoo.org/5/) applications.

How?
----

In the simplest case, given this application

```python
@click.command()
@click.option('--name', default='World', help='Who to greet.')
@click_config_file.configuration_option()
def hello(name):
  click.echo('Hello {}!'.format(name))
```

Running `hello --help` will give you this:

```
Usage: hello [OPTIONS]

Options:
  --name TEXT    Who to greet.
  --config PATH  Read configuration from PATH.
  --help         Show this message and exit.
```

If the configuration file does not exist, running `hello` will do what you
expect:

```
Hello World!
```

With this configuration file:

```
name="Universe"
```

Calling `hello` will also do what you expect:

```
Hello Universe!
```

Calling `hello --name Multiverse` will override the configuration file
setting, as it should:

```
Hello Multiverse!
```

The default name for the configuration file option is `--config`.
If no `--config` option is provided either via CLI or an environment
variable, the module will search for a file named `config` in the
appropriate directory for your OS.

Command line and environment options will override the configuration
file options. Configuration file options override default options. So
the resolution order for a given option is:
CLI > Environment > Configuration file > Default.

Configuration files should be formatted according to
[Configobj's unrepr mode](http://configobj.readthedocs.io/en/latest/configobj.html#unrepr-mode).

Why?
----

There are several existing implementations of config file support for Click,
however they seem to lack one or more of the following features:

* Sensible defaults
* Proper handling of resolution order
* Support for multi value options, multiple options or a combination of both

In contrast this module may lack some more sophisticated features of the
other implementations. This is a deliberate choice as this module is intended
to be a simple option that Just Works with sensible defaults.
