import click
import re
import os
import pytest
from click_config_file import configuration_option


def test_value(runner, tmpdir):
    @click.command()
    @configuration_option(expose_value=True)
    def cli(config):
        click.echo(config)

    result = runner.invoke(cli)
    assert not result.exception
    expected = os.path.join(click.get_app_dir('cli'), 'config')
    assert result.output == ''.join((
        expected,
        '\n',
    ))

    cfgfile = tmpdir.join('cfg')
    result = runner.invoke(cli, (
        '--config',
        str(cfgfile),
    ))
    assert not result.exception
    assert result.output == ''.join((
        str(cfgfile.realpath()),
        '\n',
    ))


def test_config_precedence_envvar_not_set(runner, cfgfile):
    @click.command()
    @click.option('--who', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option()
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


def test_broken_config(runner, tmpdir):
    @click.command()
    @configuration_option()
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


def test_custom_provider_nofile(runner):
    def mock_provider(path, name):
        assert name == 'cli'
        return {'who': 'World'}

    @click.command()
    @click.option('--who')
    @configuration_option(provider=mock_provider)
    def cli(who):
        assert who == 'World'
        click.echo("Hello {}".format(who))

    result = runner.invoke(cli)

    assert not result.exception
    assert result.output == 'Hello World\n'


def test_custom_provider_raises_exception(runner):
    def mock_provider(path, name):
        assert name == 'cli'
        raise click.BadOptionUsage('--config', 'Provider')

    @click.command()
    @click.option('--who')
    @configuration_option(provider=mock_provider)
    def cli(who):
        pytest.fail(
            'Callback should not be invoked if provider raises exception')

    result = runner.invoke(cli)

    assert result.exception
    assert re.search(r'Provider', result.output) is not None


def test_custom_provider(runner, cfgfile):
    def mock_provider(path, name):
        assert path == str(cfgfile.realpath())
        assert name == 'cli'
        return {'whom': 'World'}

    @click.command()
    @click.option('--whom')
    @configuration_option(provider=mock_provider)
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
    @configuration_option()
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
    @configuration_option()
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
    @configuration_option()
    def cli(arg):
        assert arg.read() == cfg

    cfg = 'arg = "{}"'.format(cfgfile)
    cfgfile.write(cfg)
    result = runner.invoke(cli, ['--config', str(cfgfile)])
    assert not result.exception
    assert result.exit_code == 0
