import click
import re
import os
import pytest
from click_config_file import configuration_option


@pytest.fixture
def cfgfile(tmpdir):
    cfgfile = tmpdir.join('config')
    cfgfile.write('who = "Universe"')
    return cfgfile


def test_defaults(runner):
    @click.command()
    @configuration_option()
    def cli():
        click.echo("Hello")

    result = runner.invoke(cli)
    assert not result.exception
    assert result.output == 'Hello\n'

    result = runner.invoke(cli, ('--help', ))
    assert re.search(r'--config PATH\s+Read configuration from PATH\.',
                     result.output) is not None


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


def test_custom_default_value(runner, tmpdir):
    cfgfile = tmpdir.join('config')

    @click.command()
    @configuration_option(default=str(cfgfile), expose_value=True)
    def cli(config):
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
    @configuration_option()
    def cli(who):
        click.echo("Hello {}".format(who))

    result = runner.invoke(cli)
    assert not result.exception
    assert result.output == 'Hello World\n'


def test_config_precedence_unset(runner, cfgfile):
    @click.command()
    @click.option('--whom', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option()
    def cli(whom):
        click.echo("Hello {}".format(whom))

    result = runner.invoke(cli, (
        '--config',
        str(cfgfile),
    ))
    assert not result.exception
    assert result.output == 'Hello World\n'


def test_config_precedence_cli(runner, cfgfile):
    @click.command()
    @click.option('--who', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option()
    def cli(who):
        click.echo("Hello {}".format(who))

    result = runner.invoke(cli, (
        '--who',
        'Multiverse',
        '--config',
        str(cfgfile),
    ))
    assert not result.exception
    assert result.output == 'Hello Multiverse\n'


def test_config_precedence_envvar_not_set(runner, cfgfile):
    @click.command()
    @click.option('--who', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option()
    def cli(who):
        click.echo("Hello {}".format(who))

    result = runner.invoke(
        cli, (
            '--config',
            str(cfgfile),
        ), env={})
    assert not result.exception
    assert result.output == 'Hello Universe\n'


@pytest.mark.xfail(reason="""This is a bug in click,
              see https://github.com/pallets/click/issues/873""")
def test_config_precedence_envvar_set(runner, cfgfile):
    @click.command()
    @click.option('--who', default='World', envvar='CLICK_TEST_WHO')
    @configuration_option()
    def cli(who):
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


def test_broken_config(runner, tmpdir):
    @click.command()
    @configuration_option()
    def cli():
        pass

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
        click.echo("Hello {}".format(who))

    result = runner.invoke(cli)

    assert not result.exception
    assert result.output == 'Hello World\n'


def test_custom_provider_raises_exception(runner):
    def mock_provider(path, name):
        assert name == 'cli'
        raise click.BadOptionUsage('Provider')

    @click.command()
    @click.option('--who')
    @configuration_option(provider=mock_provider)
    def cli(who):
        click.echo("Hello {}".format(who))

    result = runner.invoke(cli)

    assert result.exception
    assert re.search(r'Provider', result.output) is not None


def test_custom_provider(runner, cfgfile):
    def mock_provider(path, name):
        assert path == str(cfgfile.realpath())
        assert name == 'cli'
        return {'who': 'World'}

    @click.command()
    @click.option('--who')
    @configuration_option(provider=mock_provider)
    def cli(who):
        click.echo("Hello {}".format(who))

    result = runner.invoke(cli, (
        '--config',
        str(cfgfile),
    ))
    assert not result.exception
    assert result.output == 'Hello World\n'


def test_custom_callback(runner):
    def mock_callback(ctx, param, value):
        assert value == 'foo'
        return 'bar'

    @click.command()
    @configuration_option(
        expose_value=True, resolve_path=False, callback=mock_callback)
    def cli(config):
        click.echo(config)

    result = runner.invoke(cli, (
        '--config',
        'foo',
    ))
    assert not result.exception
    assert result.output == 'bar\n'


def test_path_params_dir_okay_default(runner, tmpdir):
    @click.command()
    @configuration_option()
    def cli():
        pass

    result = runner.invoke(cli, (
        '--config',
        str(tmpdir),
    ))
    assert result.exception
    assert result.exit_code != 0


def test_path_params_dir_okay_true(runner, tmpdir):
    @click.command()
    @configuration_option(dir_okay=True)
    def cli():
        pass

    result = runner.invoke(cli, (
        '--config',
        str(tmpdir),
    ))
    assert not result.exception
    assert result.exit_code == 0

def test_argument_string(runner):
    def mock_provider(f, n):
        return {'arg': 'foo'}

    @click.command()
    @click.argument('arg')
    @configuration_option(provider=mock_provider)
    def cli(arg):
        click.echo(arg)

    result = runner.invoke(cli)

    assert not result.exception
    assert result.exit_code == 0
    assert result.output == ''.join(('foo', '\n',))
