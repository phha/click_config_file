import click
import re
import os
import pytest
from click_config_file import configuration_option_base


def test_defaults(runner):
    @click.command()
    @configuration_option_base(expose_value=True)
    def cli(config):
        assert config is None

    result = runner.invoke(cli)
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
    assert result.exit_code != 0

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
