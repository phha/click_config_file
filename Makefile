test:
	py.test tests

tox:
	tox

release: tox
	python setup.py sdist bdist_wheel upload

.PHONY: test clean tox
