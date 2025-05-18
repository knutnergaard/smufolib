|PyPI| |versions| |license| |docs| |CI| |coverage|

===============================
SMufoLib: Where SMuFL meets UFO
===============================

.. _intro:

SMufoLib is a lightweight Python library for working with fonts that follow the
`Standard Music Font Layout <https://w3c.github.io/smufl/latest/>`_ (SMuFL). It builds
on the reference implementation of the `FontParts
<https://fontparts.robotools.dev/en/stable/index.html>`_ API and operates directly on
the `Unified Font Object <https://unifiedfontobject.org>`_ (UFO) format.
SMufoLib enhances these foundations with SMuFL-aware tools for music font design,
scripting and metadata management -- all from the command line, without requiring a GUI
font editor.

.. _documentation:

Documentation
=============

SMufoLib's documentation is available at `smufolib.readthedocs.io
<https://smufolib.readthedocs.io/en/latest/index.html>`_.

.. _installation:

Installation
============

SMufoLib requires `Python <http://www.python.org/download/>`__ 3.10 or
later. It is listed in the `Python Package Index
<https://pypi.org/project/smufolib>`_ (PyPI) and can be installed with
`pip <https://pip.pypa.io/>`__:

.. code-block:: zsh

   $ python -m pip install smufolib

.. _running-scripts:

Running Scripts
===============

SMufoLib comes bundled with several useful scripts for building SMuFL metadata files,
importing anchors, setting identification attributes and more.

Scripts may be run either directly from the command line or imported as regular python modules, passing in any arguments in the familiar manner to each platform.

.. only:: builder_html

   As an example, check for missing or superfluous SMuFL anchors and mark discrepant
   glyphs by running the :mod:`~bin.checkAnchors` script with the ``--mark`` flag
   directly from the command line:

.. only:: not builder_html

   As an example, check for missing or superfluous SMuFL anchors and mark discrepant
   glyphs by running the ``bin.checkAnchors`` script with the ``--mark`` flag
   directly from the command line:
.. code-block:: zsh

   $ check-anchors path/to/my/font.ufo --mark

Positional arguments and available options can be listed by running the help command on the script:

.. code-block:: zsh

   $ check-anchors --help

   usage: check-anchors [-h] [-F FONTDATA] [-m] [-c COLOR COLOR COLOR COLOR] [-v]
                        font

   Find missing or superfluous SMuFL anchors.

   positional arguments:
      font                  path to UFO file

   options:
      -h, --help           show this help message and exit
      -F FONTDATA, --font-data FONTDATA
                           path to font metadata file (default: <Request '/url/path/to
                           /reference/font/metadata.json' ('/file/path/to/reference/font/metadata.json') at 4536666000>)
      -m, --mark           apply defined color values to objects (default: False)
      -c COLOR COLOR COLOR COLOR, --color COLOR COLOR COLOR COLOR
                           list of RGBA color values (default: None)
      -v, --verbose        make output verbose (default: False)


Alternatively, scripts can be imported as modules in Python::

   >>> from bin.checkAnchors import checkAnchors
   >>> checkAnchors(mark=True)

.. only:: builder_html

   This imports and executes the script's program function,
   :func:`~bin.checkAnchors.checkAnchors`, from the script module of the same name.

.. only:: not builder_html

   This imports and executes the script's program function,
   ``checkAnchors.checkAnchors``, from reStructuredTextreStructuredTextthe script module of the same name.

.. |PyPI| image:: https://img.shields.io/pypi/v/smufolib
   :alt: PyPI - Version
   :target: https://pypi.org/project/smufolib/

.. |versions| image:: https://img.shields.io/pypi/pyversions/smufolib
   :alt: PyPI - Python Version
   :target: https://www.python.org

.. |license| image:: https://img.shields.io/pypi/l/smufolib
   :alt: PyPI - License
   :target: https://opensource.org/license/mit

.. |docs| image:: https://img.shields.io/readthedocs/smufolib
   :alt: Read the Docs
   :target: https://smufolib.readthedocs.io/en/latest/

.. |CI| image:: https://img.shields.io/github/actions/workflow/status/knutnergaard/smufolib/ci.yml?event=push&label=CI
   :alt: GitHub Actions Workflow Status
   :target: https://github.com/knutnergaard/smufolib/actions

.. |coverage| image:: https://img.shields.io/codecov/c/github/knutnergaard/smufolib?labelColor=grey&color=%23FF69B4
   :alt: Codecov
   :target: https://app.codecov.io/github/knutnergaard/smufolib


