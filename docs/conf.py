# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import importlib.metadata

sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SMufoLib'
copyright = '2022, Knut Nergaard'
author = 'Knut Nergaard'
release = importlib.metadata.version("smufolib")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
]

intersphinx_mapping = {
    'fontParts': ('https://fontparts.robotools.dev/en/stable/', None),
    'python': ('https://docs.python.org/3/', None),
    'setuptools': ('https://setuptools.readthedocs.io/en/latest', None)
}

# highlighting style
# pygments_style = 'sphinx'
highlight_language = 'python3'

# sphinx.ext.autodoc
autodoc_typehints = 'description'
autodoc_member_order = 'groupwise'
autodoc_docstring_signature = True


add_module_names = False

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
default_role = 'strong'


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = [
    'css/custom.css',
]

html_context = {'display_github': True,
                'github_user': 'knutnergaard',
                'github_repo': 'smufolib', }
html_theme_options = {
    'display_version': False,
}
