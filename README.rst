#SMufoLib

SMufoLib is a small library of objects and functions designed to aid in
font development specific to the [Standard Music Font Layout (SMuFL)]
(https://github.com/w3c/smufl).

The objects in SMufoLib are wrapped around [FontParts]
(https://fontparts.robotools.dev/en/stable/index.html), the replacement
for RoboFab, still in development.

##Documentation

SMufoLib’s documentation is presently limited to its docstrings.
However, the library should be easy to grasp for anyone familiar with
FontParts and SMuFL in addition to Python.

##Scripts

SMufoLib comes bundled with several useful functions and scripts for
building SMuFL metadata files, extracting engraving defaults,
exporting/importing annotation and more.

##Installation

SMufoLib requires `Python <http://www.python.org/download/>`__ 3.9 or
later. It is listed in the Python Package Index (PyPI) and can be
installed with `pip <https://pip.pypa.io/>`__:

.. code:: bash

   $ python -m pip install smufolib

##Configuration

Project specific settings are defined in ``smufolib.cfg``. This file is
divided between the following sections:

####Font Paths

Filesystem (or URL) paths to various font-related files.

####SMuFL Paths

Filesystem (or URL) paths to various SMuFL-related files.

####SMuFL URLs

Specific URL paths to various SMuFL-related files.

####About interpolation

In the above sections interpolation strings ``${option}`` and
``${section:option}`` may be used to refer to an option in the current
or specific foreign section respectively. This is particularly useful
when specifying pathnames:

::

   [Font Paths]
   directory = ~/Documents/UFO
   ufo = ${directory}/my_font.ufo (result: ~/Documents/UFO/my_font.ufo)
   ...
   [SMuFL Paths]
   ...
   classes.json = ${Font Paths:directory}/classes.json (result: ~/Documents/UFO/classes.json)

For more information, see:
https://docs.python.org/3/library/configparser.html#interpolation-of-values

####[Engraving Defaults]

Values for SMuFLs *engravingDefaults* metadata structure. Values left
empty will be calculated automatically. See ``help`` for
``smufolib.engraving.getEngravingDefaults``.

####[Mark Color]

Color values for glyph.rGlyph.markColor.
