test:
	pipenv run py.test tests

tox:
	pipenv run tox

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf click_config_file.egg-info
	rm -rf __pycache__

release: tox
	pipenv run python setup.py sdist bdist_wheel upload

upload: clean release
	pipenv run twine upload dist/*

.PHONY: test clean tox upload
