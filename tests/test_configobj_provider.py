import pytest
from click_config_file import configobj_provider


def test_init_defaults():
    provider = configobj_provider()
    assert provider.unrepr is True
    assert provider.section is None


def test_init_kwargs():
    provider = configobj_provider(unrepr=False, section='Test')
    assert provider.unrepr is False
    assert provider.section == 'Test'


def test_call_missing_file(tmpdir):
    nofile = tmpdir.join("nosuchfile")
    provider = configobj_provider()
    with pytest.raises(Exception):
        provider(nofile, 'name')


def test_call_broken_file(tmpdir):
    conffile = tmpdir.join('config')
    conffile.write("Ceci n'est pas un ConfigObj.")
    provider = configobj_provider()
    with pytest.raises(Exception):
        provider(conffile, 'name')


def test_call_nosection(tmpdir):
    conffile = tmpdir.join('config')
    conffile.write("testvalue = True")
    provider = configobj_provider()
    rv = provider(conffile, 'name')
    assert 'testvalue' in rv
    assert rv['testvalue'] is True


def test_call_section(tmpdir):
    conffile = tmpdir.join('config')
    conffile.write("""
                   [mysection]
                   testvalue = True
                   """)
    provider = configobj_provider(section='mysection')
    rv = provider(conffile, 'name')
    assert 'testvalue' in rv
    assert rv['testvalue'] is True
