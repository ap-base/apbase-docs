SPHINXBUILD ?= sphinx-build
SOURCEDIR = docs
BUILDDIR = _build

.PHONY: html clean translations

html:
	$(SPHINXBUILD) -b html -W --keep-going $(SOURCEDIR) $(BUILDDIR)/html

clean:
	rm -rf $(BUILDDIR) $(SOURCEDIR)/_build

# Lists translated pages that are missing or older than their English source (see TRANSLATING.md).
translations:
	python3 scripts/check-translations.py
