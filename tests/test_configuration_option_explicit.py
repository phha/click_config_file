import click
import re
import os
import pytest
from click_config_file import configuration_option

def test_help(runner):
    @click.command()
    @configuration_option(implicit=False)
    def cli():
        click.echo("Hello")

    result = runner.invoke(cli)
    assert not result.exception
    assert result.output == 'Hello\n'

    result = runner.invoke(cli, ('--help', ))
    assert re.search(r'--config FILE\s+Read configuration from FILE\.',
                     result.output) is not None

def test_defaults(runner):
    @click.command()
    @configuration_option(implicit=False, expose_value=True)
    def cli(config):
        assert config is None

    result = runner.invoke(cli)
    assert not result.exception
    assert result.exit_code == 0


def test_custom_default_value(runner, cfgfile):
    @click.command()
    @configuration_option(implicit=False, default=str(cfgfile), expose_value=True)
    def cli(config):
        assert config == str(cfgfile)
        click.echo(config)

    result = runner.invoke(cli)
    assert not result.exception
    assert result.output == ''.join((
        str(cfgfile.realpath()),
        '\n',
    ))


def test_config_precedence_no_config(runner):
    @click.command()
    @click.option('--who', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option(implicit=False)
    def cli(who):
        assert who == "World"
        click.echo("Hello {}".format(who))

    result = runner.invoke(cli)
    assert not result.exception
    assert result.output == 'Hello World\n'


def test_config_value_no_replacement(runner, cfgfile):
    """Test that config does not replace variable of other name."""
    @click.command()
    @click.option('--whom', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option(implicit=False)
    def cli(whom):
        assert whom == "World"
        click.echo("Hello {}".format(whom))

    result = runner.invoke(cli, (
        '--config',
        str(cfgfile),
    ))
    assert not result.exception
    assert result.output == 'Hello World\n'

def test_broken_config(runner, tmpdir):
    @click.command()
    @configuration_option(implicit=False)
    def cli():
        pytest.fail("Callback should not be called if config is broken")

    cfgfile = tmpdir.join('config')
    cfgfile.write("Ceci n'est pas une config.")

    result = runner.invoke(cli, (
        '--config',
        str(cfgfile),
    ))
    assert re.search(r'Error reading configuration file',
                     result.output) is not None
    assert result.exception
    assert result.exit_code != 0



def test_config_precedence_override_default(runner, cfgfile):
    @click.command()
    @click.option('--who', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option(implicit=False)
    def cli(who):
        assert who == 'Universe'
        click.echo("Hello {}".format(who))

    result = runner.invoke(
        cli, (
            '--config',
            str(cfgfile),
        ), env={})
    assert not result.exception
    assert result.output == 'Hello Universe\n'


def test_config_precedence_cli_option(runner, cfgfile):
    @click.command()
    @click.option('--who', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option(implicit=False)
    def cli(who):
        assert who == 'Multiverse'
        click.echo("Hello {}".format(who))

    result = runner.invoke(cli, (
        '--who',
        'Multiverse',
        '--config',
        str(cfgfile),
    ))
    assert not result.exception
    assert result.output == 'Hello Multiverse\n'

def test_config_precedence_envvar(runner, cfgfile):
    @click.command()
    @click.option('--who', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option(implicit=False)
    def cli(who):
        assert who == 'You'
        click.echo("Hello {}".format(who))

    result = runner.invoke(
        cli, (
            '--config',
            str(cfgfile),
        ), env={
            'CLICK_TEST_WHO': 'You'
        })
    assert not result.exception
    assert result.output == 'Hello You\n'


def test_exists_true(runner, tmpdir):
    @click.command()
    @configuration_option(exists=True, implicit=False)
    def cli():
        pass

    path = tmpdir.join('config')
    result = runner.invoke(cli, ('--config', str(path),))
    assert result.exception
    assert result.exit_code != 0
    assert re.search(r'File "{}" does not exist'.format(path),
                     result.output) is not None

    path.write("\n")
    result = runner.invoke(cli, ('--config', str(path),))
    assert not result.exception
    assert result.exit_code == 0


def test_custom_callback(runner):
    def mock_callback(ctx, param, value):
        assert value == 'foo'
        return 'bar'

    @click.command()
    @configuration_option(
        implicit=False, expose_value=True,
        resolve_path=False, callback=mock_callback)
    def cli(config):
        assert config == 'bar'
        click.echo(config)

    result = runner.invoke(cli, (
        '--config',
        'foo',
    ))
    assert not result.exception
    assert result.output == 'bar\n'


def test_path_params_dir_okay_default(runner, tmpdir):
    @click.command()
    @configuration_option(implicit=False)
    def cli():
        pytest.fail('Callback should not be invoked')

    result = runner.invoke(cli, (
        '--config',
        str(tmpdir),
    ))
    assert result.exception
    assert result.exit_code != 0


def test_path_params_dir_okay_true(runner, tmpdir):
    @click.command()
    @configuration_option(dir_okay=True, implicit=False)
    def cli():
        pass

    result = runner.invoke(cli, (
        '--config',
        str(tmpdir),
    ))
    assert not result.exception
    assert result.exit_code == 0



def test_value(runner, tmpdir):
    cfgfile = tmpdir.join('cfg')

    @click.command()
    @configuration_option(implicit=False, expose_value=True)
    def cli(config):
        assert str(config) == str(cfgfile)
        click.echo(config)

    result = runner.invoke(cli, (
        '--config',
        str(cfgfile),
    ))
    assert not result.exception
    assert result.output == ''.join((
        str(cfgfile.realpath()),
        '\n',
    ))
    assert result.exit_code == 0


def test_no_callback_when_unset(runner, cfgfile):
    def mock_provider(path, name):
        assert False

    @click.command()
    @click.option('--who', default='World')
    @configuration_option(implicit=False, provider=mock_provider)
    def cli(who):
        assert who == 'World'

    result = runner.invoke(cli)
    assert not result.exception
    assert result.exit_code == 0

def test_custom_callback_when_unset(runner):
    def mock_callback(ctx, param, value):
        assert value == 'foo'
        return 'bar'

    @click.command()
    @configuration_option(
        implicit=False, expose_value=True, callback=mock_callback)
    def cli(config):
        assert config == 'bar'
        click.echo(config)

    result = runner.invoke(cli, (
        '--config',
        'foo',
    ))
    assert not result.exception
    assert result.output == 'bar\n'
    assert result.exit_code == 0

def test_custom_provider(runner, cfgfile):
    def mock_provider(path, name):
        assert path == str(cfgfile.realpath())
        assert name == 'cli'
        return {'whom': 'World'}

    @click.command()
    @click.option('--whom')
    @configuration_option(implicit=False, provider=mock_provider)
    def cli(whom):
        assert whom == 'World'
        click.echo("Hello {}".format(whom))

    result = runner.invoke(cli, (
        '--config',
        str(cfgfile),
    ))
    assert not result.exception
    assert result.output == 'Hello World\n'


def test_argument_basic(runner, cfgfile):
    cfgfile.write('arg = "foo"')

    @click.command()
    @click.argument('arg')
    @configuration_option(implicit=False)
    def cli(arg):
        assert arg == 'foo'
        click.echo(arg)

    result = runner.invoke(cli, ['--config', str(cfgfile)])

    assert not result.exception
    assert result.exit_code == 0
    assert result.output == ''.join(('foo', '\n',))


def test_argument_variadic(runner, cfgfile):
    cfgfile.write('arg = ["foo", "bar"]')

    @click.command()
    @click.argument('arg', nargs=2)
    @configuration_option(implicit=False)
    def cli(arg):
        assert arg == ('foo', 'bar')
        for a in arg:
            click.echo(a)

    result = runner.invoke(cli, ['--config', str(cfgfile)])

    assert not result.exception
    assert result.exit_code == 0
    assert result.output == ''.join(('foo', '\n', 'bar', '\n',))


def test_argument_file(runner, cfgfile):
    @click.command()
    @click.argument('arg', type=click.File())
    @configuration_option(implicit=False)
    def cli(arg):
        assert arg.read() == cfg

    cfg = 'arg = "{}"'.format(cfgfile)
    cfgfile.write(cfg)
    result = runner.invoke(cli, ['--config', str(cfgfile)])
    assert not result.exception
    assert result.exit_code == 0

def test_read_cfg_from_file(runner, cfgfile):
    """Test returning config file handle directly.

    Note: configobj.Configobj works both with file paths and file handles (so does the default configobj_provider).
    """
    @click.command()
    @click.argument('arg')
    @configuration_option(type=click.File(), implicit=False)
    def cli(arg):
        click.echo(arg)
        assert arg == 'foo'

    cfg = 'arg = "foo"'
    cfgfile.write(cfg)
    result = runner.invoke(cli, ['--config', str(cfgfile)])
    assert not result.exception, result.exception
    assert result.exit_code == 0

