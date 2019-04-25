test: build
	pipenv run pytest --cov=click_config_file tests/
	pipenv run twine check dist/*

tox:
	pipenv run tox

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf click_config_file.egg-info
	rm -rf __pycache__
	rm -f coverage.xml
	pipenv run coverage erase

build: clean
	pipenv run python setup.py sdist bdist_wheel

upload: test
	pipenv run twine upload dist/*

.PHONY: test clean tox upload build
