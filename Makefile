SPHINXBUILD ?= sphinx-build
SOURCEDIR = docs
BUILDDIR = _build

.PHONY: html clean

html:
	$(SPHINXBUILD) -b html -W --keep-going $(SOURCEDIR) $(BUILDDIR)/html
	cp CNAME .nojekyll $(BUILDDIR)/html/

clean:
	rm -rf $(BUILDDIR) $(SOURCEDIR)/_build
