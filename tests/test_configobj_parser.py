import pytest
from click_config_file import configobj_parser


def test_init_defaults():
    parser = configobj_parser()
    assert parser.unrepr is True
    assert parser.section is None


def test_init_kwargs():
    parser = configobj_parser(unrepr=False, section='Test')
    assert parser.unrepr is False
    assert parser.section == 'Test'


def test_call_missing_file(tmpdir):
    nofile = tmpdir.join("nosuchfile")
    parser = configobj_parser()
    with pytest.raises(Exception):
        parser(nofile, 'name')


def test_call_broken_file(tmpdir):
    conffile = tmpdir.join('config')
    conffile.write("Ceci n'est pas un ConfigObj.")
    parser = configobj_parser()
    with pytest.raises(Exception):
        parser(conffile, 'name')


def test_call_nosection(tmpdir):
    conffile = tmpdir.join('config')
    conffile.write("testvalue = True")
    parser = configobj_parser()
    rv = parser(conffile, 'name')
    assert 'testvalue' in rv
    assert rv['testvalue'] is True


def test_call_section(tmpdir):
    conffile = tmpdir.join('config')
    conffile.write("""
                   [mysection]
                   testvalue = True
                   """)
    parser = configobj_parser(section='mysection')
    rv = parser(conffile, 'name')
    assert 'testvalue' in rv
    assert rv['testvalue'] is True
