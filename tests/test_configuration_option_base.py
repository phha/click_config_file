import click
import re
import os
import pytest
from click_config_file import configuration_option_base

def test_help(runner):
    @click.command()
    @configuration_option_base()
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
    @configuration_option_base(expose_value=True)
    def cli(config):
        assert config is None

    result = runner.invoke(cli)
    assert not result.exception
    assert result.exit_code == 0


def test_custom_default_value(runner, cfgfile):
    @click.command()
    @configuration_option_base(default=str(cfgfile), expose_value=True)
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
    @configuration_option_base()
    def cli(who):
        assert who == "World"
        click.echo("Hello {}".format(who))

    result = runner.invoke(cli)
    assert not result.exception
    assert result.output == 'Hello World\n'


def test_config_value_replacement(runner, cfgfile):
    @click.command()
    @click.option('--whom', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option_base()
    def cli(whom):
        assert whom == "World"
        click.echo("Hello {}".format(whom))

    result = runner.invoke(cli, (
        '--config',
        str(cfgfile),
    ))
    assert not result.exception
    assert result.output == 'Hello World\n'


def test_config_precedence_cli_option(runner, cfgfile):
    @click.command()
    @click.option('--who', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option_base()
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
    @configuration_option_base()
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
    @configuration_option_base(exists=True)
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
    @configuration_option_base(
        expose_value=True, resolve_path=False, callback=mock_callback)
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
    @configuration_option_base()
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
    @configuration_option_base(dir_okay=True)
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
    @configuration_option_base(expose_value=True)
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
    @configuration_option_base(provider=mock_provider)
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
    @configuration_option_base(
        expose_value=True, callback=mock_callback)
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
