from __future__ import annotations

project = "APbase"
copyright = "APbase"
author = "APbase"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.mathjax",
    "sphinxcontrib.bibtex",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_sitemap",
]

copybutton_prompt_text = r"\$ "
copybutton_prompt_is_regexp = True

napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_ivar = True

autodoc_typehints = "description"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

bibtex_bibfiles = ["references.bib"]
bibtex_default_style = "unsrt"

myst_enable_extensions = ["colon_fence", "deflist", "dollarmath", "amsmath"]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

language = "en"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "APbase"
html_baseurl = "https://apbase.io/"
sitemap_url_scheme = "{link}"
sitemap_locales = [None]
html_logo = "img/apbase.jpg"
templates_path = ["_templates"]
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/pypi-version.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
        "sidebar/variant-selector.html",
    ],
}
html_static_path = ["_static"]
html_extra_path = ["robots.txt"]
html_css_files = ["custom.css"]
