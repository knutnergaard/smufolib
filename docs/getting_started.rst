Installation
============

SMufoLib requires `Python <http://www.python.org/download/>`__ 3.10 or
later. It is listed in the `Python Package Index
<https://pypi.org/project/smufolib>`_ (PyPI) and can be installed with
`pip <https://pip.pypa.io/>`__:

.. code:: zsh

    $ python -m pip install smufolib

First Steps
===========

Start by importing SMufoLib::

   >>> from smufolib import Font

Then instanciate a font object::

   >>> font = Font("path/to/myFont.ufo")

Setting attributes
==================

SMufoLib provides easy storage of SMuFL-specific font and glyph metadata attributes within the font file itself. Attributes can be set individually during the design process::

   >>> font.smufl.name = "myFont"
   >>> font.smufl.version = 1.0
   >>> font.smufl.designSize = 20
   >>> font.smufl.sizeRange = (16, 24)
   >>> glyph = font["uniE000"]
   >>> glyph.smufl.name = "gClef"
   >>> glyph.smufl.description = "G clef"
   >>> glyph.smufl.classes = (clefs,)

Attribute values may also be imported from preexisting metadata files using the various provided scripts like :mod:`~bin.importID` , :mod:`calculateEngravingDefaults` and :mod:`importAnchors`, either from the command line or by importing them into Python (see :ref:`running-scripts`).

Working with metadata
=====================

Once SMuFL sepcific glyph names and other attributes have been set, SMufoLib provides useful features like:

Accessing SMuFL ranges and their attributes
-------------------------------------------

   >>> glyph = font["uniE000"]
   >>> glyph.smufl.ranges
   (<Range 'staffBracketsAndDividers' ('U+E000-U+E00F') at 4339747808>,)

These are useful when working with particular types of glyphs::

   >>> for glyph in font:
   ...     if glyph.smufl.ranges[0].name == "staffBracketsAndDividers":
   ...         glyph.moveBy = (12, 0)


For example, coloring glyphs by range is really easy::

   >>> import random
   >>> def get_random_color():
   ...    r = random.random()
   ...    g = random.random()
   ...    b = random.random()
   ...    return (r, g, b, 1)
   ...
   >>> for range in font.smufl.ranges:
   ...     color = get_random_color()
   ...     for glyph in range.glyphs:
   ...         glyph.mark = color

.. _running-scripts

Running Scripts
===============

SMufoLib comes bundled with several useful scripts for building SMuFL
metadata files, calculating engraving defaults from glyphs, importing
identification attributes and more.

Scripts may be run either directly from the command line or imported as
regular python modules, passing in any arguments in the familiar manner
to each platform.

As an example, check for missing or superflous SMuFL anchors and mark
discrepant glyphs by running the :mod:`~bin.checkAnchors` script with
the ``--mark`` flag directly from the command line:

.. code:: zsh

   $ check-anchors path/to/my/font.ufo --mark

Positional arguments and available options can be listed by running the
help command on the script:

.. code:: zsh

   $ check-anchors --help

   usage: check-anchors [-h] [-F FONTDATA] [-m] [-c COLOR COLOR COLOR COLOR] [-v]
                        font

   Find missing or superfluous SMuFL anchors.

   positional arguments:
      font                  path to UFO file

   options:
      -h, --help           show this help message and exit
      -F FONTDATA, --font-data FONTDATA
                           path to font metadata file (default: <Request '/url/path
                           /to/reference/font/metadata.json' ('/file/path/to/refere
                           nce/font/metadata.json') at 4536666000>)
      -m, --mark           apply defined color values to objects (default: False)
      -c COLOR COLOR COLOR COLOR, --color COLOR COLOR COLOR COLOR
                           list of RGBA color values (default: None)
      -v, --verbose        make output verbose (default: False)


Alternatively, scripts can be imported as modules in Python:

.. code:: Py3

   from bin.checkAnchors import checkAnchors

   checkAnchors(mark=True)

This imports and executes the script's program
function, :func:`~bin.checkAnchors.checkAnchors`, from the script module of the same
name. The documentation for either one is accessible via :func:`help`.
