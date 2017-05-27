# directory where master branch is included
WEBDNN := $(abspath ../webdnn)

# directory where webpage-src branch is included
WEBDNN_HP :=$(abspath ./)

# directory where the build files will be output to
WEBDNN_GH := $(abspath ../webdnn-gh-pages/webdnn)

.PHONY: default build build-webpage build-docs build-cp

default:
	cat Makefile

build:
	$(MAKE) build-webpage
	$(MAKE) build-docs
	$(MAKE) build-cp

build-webpage:
	yarn install
	yarn run webpack

build-docs:
	cd ${WEBDNN}; yarn install
	pip install recommonmark sphinx-rtd-theme
	cd ${WEBDNN}/docs; $(MAKE) html

build-cp:
	mkdir -p ${WEBDNN_GH}
	mkdir -p ${WEBDNN_GH}/docs
	cp -R ${WEBDNN}/docs/build/html/ ${WEBDNN_GH}/docs/
	cp -R ${WEBDNN_HP}/build/webdnn/ ${WEBDNN_GH}