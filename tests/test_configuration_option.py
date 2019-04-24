import click
import re
import os
import pytest
from click_config_file import configuration_option


def test_default_value(runner, tmpdir):
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


