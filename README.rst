SMufoLib
========

SMufoLib is a small Python library designed to aid in
font development specific to the `Standard Music Font Layout
<https://github.com/w3c/smufl>`_ (SMuFL).

The objects in SMufoLib are wrapped around `FontParts
<https://fontparts.robotools.dev/en/stable/index.html>`_, the
replacement for RoboFab, still in development.

Documentation
-------------

SMufoLib’s documentation is presently limited to its docstrings.
However, the library should be easy to grasp for anyone familiar with
FontParts and SMuFL in addition to Python.

Installation
------------

SMufoLib requires `Python <http://www.python.org/download/>`__ 3.7 or
later. It is listed in the Python Package Index (PyPI) and can be
installed with `pip <https://pip.pypa.io/>`__:

.. code:: bash

   $ python -m pip install smufolib

Configuration
-------------

Project specific settings are defined in ``smufolib.cfg``. This file is
located inside the `smufolib` folder in python site packages by
default, but can be moved to the home folder or a specific location
defined in the environment variable ``SMUFOLIB_CFG`` or as
``INI_FILEPATH`` inside ``config.py``.

The file is divided between the following sections:

Font Paths
^^^^^^^^^^

Filesystem (or URL) paths to various font-related files.

SMuFL Paths
^^^^^^^^^^^

Filesystem (or URL) paths to various SMuFL-related files.

The options in this section are primarily intended to serve as fallback
values for **SMuFL URLs**.

SMuFL URLs
^^^^^^^^^^

Specific URL paths to various SMuFL-related files.

As mentioned above, fallback values for this section (e.g., in the event
of a connection failure) can be provided in the **SMuFL Paths** section.

A note about interpolation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Interpolation strings ``${option}`` and ``${section:option}`` may be
used to refer to an option in the current or specific foreign section
respectively. This is particularly useful when specifying pathnames:

::

   [Font Paths]
   directory = ~/Documents/UFO
   ufo = ${directory}/my_font.ufo (result: ~/Documents/UFO/my_font.ufo)
   ...
   [SMuFL Paths]
   ...
   classes.json = ${Font Paths:directory}/classes.json
   (result: ~/Documents/UFO/classes.json)

For more information, see:
https://docs.python.org/3/library/configparser.html#interpolation-of-values

Engraving Defaults
^^^^^^^^^^^^^^^^^^

Values for SMuFLs *engravingDefaults* metadata structure. Values left
empty will be calculated automatically. See ``help`` for
``smufolib.engraving.getEngravingDefaults.``

Mark Color
^^^^^^^^^^

Color values for glyph.rGlyph.markColor.

Scripts
-------

SMufoLib comes bundled with several useful functions and scripts for
building SMuFL metadata files, extracting engraving defaults,
exporting/importing annotation and more.

Scripts may be run via the Python interpreter or directly from the
console, passing in any arguments in the familiar manner to each
platform.

As an example, check for missing or superflous SMuFL anchors
with *checkAnchors* directly from console as follows:

.. code:: bash

   $ checkAnchors --mark True

Or with regular python:

.. code:: Py3

   from bin import checkAnchors

   checkAnchors(mark=True)
