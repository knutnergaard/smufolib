Installation
============

SMufoLib requires `Python <http://www.python.org/download/>`__ 3.10 or
later. It is listed in the `Python Package Index
<https://pypi.org/project/smufolib>`_ (PyPI) and can be installed with
`pip <https://pip.pypa.io/>`__:

.. code:: zsh

    $ python -m pip install smufolib

Running Scripts
===============

SMufoLib comes bundled with several useful functions and scripts for
building SMuFL metadata files, calculating engraving defaults from
glyphs, importing identification attributes and more.

Scripts may be run either via the Python interpreter or
directly from the console, passing in any arguments in the familiar
manner to each platform.

As an example, check for missing or superflous SMuFL anchors by running
the :mod:`~bin.checkAnchors` script directly from console:

.. code:: zsh

   $ check-anchors --mark

Mandatory arguments and available options can be listed by running the
help command on the script:

.. code:: zsh

   $ generate-metadata --help

   usage: generate-metadata [-h] [-F FONTDATA] [-v] font target-path

   Generate font metadata JSON file.

   positional arguments:
     font                  path to UFO file
     target-path           path to target file or directory

   options:
     -h, --help            show this help message and exit
     -F FONTDATA, --font-data FONTDATA
                           path to font metadata file (default: <Request 'https:/
                           /raw.githubusercontent.com/steinbergmedia/bravura/mast
                           er/redist/bravura_metadata.json' ('/Users/knutnergaard
                           /smufolib/metadata/bravura_metadata.json') at
                           4536272304>)
     -v, --verbose         make output verbose (default: False)


Alternatively each script can be imported as a module in Python:

.. code:: Py3

   from bin.checkAnchors import checkAnchors

   checkAnchors(mark=True)
