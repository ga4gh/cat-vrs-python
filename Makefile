# Makefile for Python project

.DELETE_ON_ERROR:
.PHONY: FORCE
.PRECIOUS:
.SUFFIXES:

SHELL:=/bin/bash -e -o pipefail
SELF:=$(firstword $(MAKEFILE_LIST))

UNAME = $(shell uname)
ifeq (${UNAME},Darwin)
    _XRM_R:=
else
    _XRM_R:=r
endif
XRM=xargs -0${_XRM_R} rm

PKG=ga4gh.cat_vrs
PKGD=$(subst .,/,${PKG})
PYV:=3.12
VEDIR=venv/${PYV}


############################################################################
#= BASIC USAGE
default: help

#=> help -- display this help message
help:
	@sbin/makefile-extract-documentation "${SELF}"


############################################################################
#= SETUP, INSTALLATION, PACKAGING

#=> venv: make a Python 3 virtual environment
.PHONY: venv/%
venv/%:
	python$* -m venv $@; \
	source $@/bin/activate; \
	python -m ensurepip --upgrade; \
	pip install --upgrade pip setuptools

#=> develop: install package in develop mode
.PHONY: develop setup
develop setup:
	pip install -e .[dev,tests]

#=> devready: create venv, install prerequisites, install pkg in develop mode
.PHONY: devready
devready:
	make ${VEDIR} && source ${VEDIR}/bin/activate && make develop
	@echo '#################################################################################'
	@echo '###  Do not forget to `source ${VEDIR}/bin/activate` to use this environment  ###'
	@echo '#################################################################################'

############################################################################
#= TESTING
# see test configuration in pyproject.toml

#=> test: execute tests
.PHONY: test
test:
	pytest

#=> doctest: execute documentation tests (requires extra data)
.PHONY: doctest
doctest:
	pytest --doctest-modules

############################################################################
#= UTILITY TARGETS

#=> format: reformat code with ruff
.PHONY: format
format:
	ruff format

#=> lint: static analysis check
.PHONY: lint
lint:
	ruff check --fix --exit-zero

############################################################################
#= CLEANUP

#=> clean: remove temporary and backup files
.PHONY: clean
clean:
	find . \( -name \*~ -o -name \*.bak \) -print0 | ${XRM}

#=> cleaner: remove files and directories that are easily rebuilt
.PHONY: cleaner
cleaner: clean
	rm -fr .cache *.egg-info .pytest_cache build dist doc/_build htmlcov
	find . \( -name \*.pyc -o -name \*.orig -o -name \*.rej \) -print0 | ${XRM}
	find . -name __pycache__ -print0 | ${XRM} -fr

#=> cleanest: remove files and directories that require more time/network fetches to rebuild
.PHONY: cleanest
cleanest: cleaner
	rm -fr .eggs venv
