test:
	py.test tests

tox:
	tox

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf click_config_file.egg-info
	rm -rf __pycache__

release: tox
	python setup.py sdist bdist_wheel upload

upload: clean release
	twine upload dist/*

.PHONY: test clean tox upload
