from click.testing import CliRunner

import pytest


@pytest.fixture(scope='function')
def runner(request):
    return CliRunner()


@pytest.fixture
def cfgfile(tmpdir):
    cfgfile = tmpdir.join('config')
    cfgfile.write('who = "Universe"')
    return cfgfile
