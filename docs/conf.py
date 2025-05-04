# Configuration file for the Sphinx documentation builder.

# pylint: disable=all

import os
import sys
import importlib.metadata

sys.path.insert(0, os.path.abspath(".."))

# -- Project information ------------------------------------------------------

project = "SMufoLib"
copyright = "2022, Knut Nergaard"
author = "Knut Nergaard"
release = importlib.metadata.version("smufolib")

# -- General configuration ----------------------------------------------------

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
]

intersphinx_mapping = {
    "fontParts": ("https://fontparts.robotools.dev/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "setuptools": ("https://setuptools.readthedocs.io/en/latest", None),
}

autodoc_typehints = "signature"
autodoc_default_options = {
    "member-order": "groupwise",
}


exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
templates_path = ["_templates"]
highlight_language = "python3"
add_module_names = False
nitpicky = True
default_role = "code"

# -- Options for HTML output --------------------------------------------------

html_theme = "sphinx_rtd_theme"

html_context = {
    "display_github": True,
    "github_user": "knutnergaard",
    "github_repo": "smufolib",
}

html_css_files = ["css/custom.css"]
html_static_path = ["_static"]
