# Configuration file for the Sphinx documentation builder.

# pylint: disable=all

import sys
import importlib.metadata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# -- Project information ------------------------------------------------------

project = "SMufoLib"
copyright = "2022, Knut Nergaard"
author = "Knut Nergaard"
release = importlib.metadata.version("smufolib")

# -- General configuration ----------------------------------------------------

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
]

intersphinx_mapping = {
    "fontParts": ("https://fontparts.robotools.dev/en/stable/", None),
    "defcon": ("https://defcon.robotools.dev/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "setuptools": ("https://setuptools.readthedocs.io/en/stable", None),
}

autodoc_default_options = {
    "member-order": "groupwise",
}

doctest_global_setup = (Path(__file__).parent / "doctest_setup.py").read_text()


exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
templates_path = ["_templates"]
highlight_language = "python3"
add_module_names = False
nitpicky = True
default_role = "code"

extlinks = {
    "smufl": ("https://w3c.github.io/smufl/latest/%s", "%s"),
    "fontParts": ("https://fontparts.robotools.dev/en/stable/%s", "%s"),
}

# -- Options for HTML output --------------------------------------------------

html_theme = "sphinx_rtd_theme"

html_context = {
    "display_github": True,
    "github_user": "knutnergaard",
    "github_repo": "smufolib",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

html_css_files = ["css/custom.css"]
html_static_path = ["_static"]
