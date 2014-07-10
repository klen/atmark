VENV=$(shell echo "$${VENV:-'.env'}")

all: $(VENV)

$(VENV): requirements.txt
	[ -d $(VENV) ] || virtualenv --no-site-packages $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

.PHONY: clean
# target: clean - Display callable targets
clean:
	rm -rf build/ dist/ docs/_build *.egg-info
	find $(CURDIR) -name "*.py[co]" -delete
	find $(CURDIR) -name "*.orig" -delete

.PHONY: register
# target: register - Register module on PyPi
register:
	@python setup.py register

.PHONY: upload
# target: upload - Upload module on PyPi
release: clean
	@git push --all
	@git push --tags
	@python setup.py sdist upload || echo 'Skip sdist upload'
	# @python setup.py bdist_wheel upload || echo 'Skip bdist upload'

.PHONY: test
# target: test - Runs tests
test: clean
	@python setup.py test

.PHONY: t
t: test

.PHONY: audit
# target: audit - Audit code
audit:
	@pip install pylama
	@pylama $(MODULE)

.PHONY: doc
doc: docs
	@pip install sphinx
	@pip install sphinx-pypi-upload
	python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files
	python setup.py upload_sphinx --upload-dir=docs/_build/html
