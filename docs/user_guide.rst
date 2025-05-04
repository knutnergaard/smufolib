============
Installation
============

SMufoLib requires `Python <http://www.python.org/download/>`__ 3.10 or
later. It is listed in the `Python Package Index
<https://pypi.org/project/smufolib>`_ (PyPI) and can be installed with
`pip <https://pip.pypa.io/>`__:

.. code:: zsh

    $ python -m pip install smufolib

===========
First Steps
===========

Start by importing SMufoLib::

   >>> from smufolib import Font

Then instantiate a font object::

   >>> font = Font("path/to/myFont.ufo")

==================
Setting attributes
==================

SMufoLib provides easy storage of SMuFL-specific font and glyph metadata within the font
file itself. Attributes can be set individually during the design process, and are
accessed through the :class:`.Smufl` object::

   >>> font.smufl.name = "myFont"
   >>> font.smufl.version = 1.0
   >>> font.smufl.designSize = 20
   >>> font.smufl.sizeRange = (16, 24)
   >>> glyph = font["uniE000"]
   >>> glyph.smufl.name = "gClef"
   >>> glyph.smufl.description = "G clef"
   >>> glyph.smufl.classes = (clefs,)

.. note::

   Some attributes, like :attr:`.Smufl.name`, will be different depending
   on whether they are accessed through :class:`.Font` or :class:`.Glyph`.

   Font-specific :class:`.Smufl` attributes are generally available from either the
   font or any of it's glyphs.

The essential glyph identification attributes (:attr:`.Smufl.name`,
:attr:`.Smufl.description` and :attr:`.Smufl.classes`) may also be imported from preexisting metadata files using the :mod:`~bin.importID` script. See
:ref:`running-scripts` from more information.

.. _working-with-metadata:

=====================
Working with metadata
=====================

Once SMuFL specific glyph names and other attributes have been set, SMufoLib provides useful features like:

Glyph Ranges
============

The SMuFL-specific glyph ranges covered are available for an entire font or any
specific glyph:: 
   
   >>> font.smufl.ranges
   (<Range 'stringTechniques' ('U+E610-U+E62F') at 4449982528>,
   <Range 'multiSegmentLines' ('U+EAA0-U+EB0F') at 4449981712>,
   <Range 'harpTechniques' ('U+E680-U+E69F') at 4449981376>, ...)

::

   >>> glyph = font["uniE000"] # brace
   >>> glyph.smufl.ranges
   (<Range 'staffBracketsAndDividers' ('U+E000-U+E00F') at 4339747808>,)


These are particularly useful when working with multiple glyphs by type::

   >>> for glyph in font:
   ...     if glyph.smufl.ranges[0].name == "staffBracketsAndDividers":
   ...         glyph.moveBy = (12, 0)


Coloring glyphs by range is also really easy with this feature::

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

The :class:`.Range` object provides the values for any SMuFL range's 
:attr:`~.Range.name`, :attr:`~.Range.description`, :attr:`~.Range.glyphs`, 
:attr:`~.Range.start` and :attr:`~.Range.end` attributes.

.. _engraving-defaults:

Engraving Defaults
==================

Engraving defaults are managed by their own appropriately named
:class:`.EngravingDefaults` object, accessed with the :attr:`.Smufl.engravingDefaults` attribute::

   >>> font.smufl.engravingDefaults
   <EngravingDefaults in font 'MyFont' path='/path/to/myFont.ufo'
   auto=True at 4425372944>

Each setting has it's own attribute within this object::
   
   >>> ed = font.smufl.engravingDefaults
   >>> ed.stemThickness
   None
   >>> ed.stemThickness = 30
   >>> ed.stemThickness
   30

.. versionadded:: 0.5.0

   Engraving defaults are calculated automatically from corresponding glyphs by default
   -- provided these glyphs exist. See :ref:`engraving-defaults-mapping` for a full
   list of attributes and their corresponding glyphs.

   To override the automatic calculations, simply set the attributes to a value other
   than :obj:`None`.

   To turn the feature off entirely, disable `auto` in the :ref:`[engravingDefaults]`
   section of `smufolib.cfg`. See :ref:`configuring-smufolib` for more information
   about how to customize SMufoLib's behavior.

Engraving defaults are available in either font units or staff spaces. See
:ref:`changing-measurement-units` for more information.

Anchors
=======

SMufoLib does not currently provide it's own anchor object, but a SMuFL specific
representation of a glyph's anchors is available from the :attr:`.Smufl.anchors`
attribute::
   
   >>> glyph = font['uniE0A3'] # noteheadHalf
   >>> glyph.smufl.anchors
   {'cutOutNW': (0.204, 0.296), 'cutOutSE':
   (0.98, -0.3), 'splitStemDownNE': (0.956, -0.3), 'splitStemDownNW':
   (0.128, -0.428), 'splitStemUpSE': (1.108, 0.372), 'splitStemUpSW':
   (0.328, 0.38), 'stemDownNW': (0.0, -0.168), 'stemUpSE': (1.18, 0.168)}

Anchor coordinates are available in either font units or staff spaces. See
:ref:`changing-measurement-units` for more information.

Anchors may be imported from another font's metadata file using the
:mod:`~bin.importAnchors` script. SMufoLib also provides the diagnostics script
:mod:`~bin.checkAnchors` to keep track of missing or superfluous SMuFL-specific glyph
anchors in a font. See :ref:`running-scripts` from more information.

.. _changing-measurement-units:

Changing Measurement Units
==========================

You can get or set engraving defaults, anchor coordinates and glyph advance width in
either font units or staff spaces, whatever suits your workflow. To switch to staff
spaces set either :attr:`.EngravingDefaults.spaces` or :attr:`.Smufl.spaces` to
:obj:`True`, e.g.::

   >>> ed.spaces = True
   >>> ed.stemThickness
   0.12
   >>> ed.stemThickness = 0.14
   >>> ed.spaces = False
   >>> ed.stemThickness
   35
   
.. note::

   Setting ``font.smufl.engravingDefaults.spaces=True`` is equivalent to setting
   ``font.smufl.spaces=True``, so either one will affect all relevant
   attributes across the entire library.
   
   The setting will be saved with the font.

The :class:`.SMufl` class also provides methods to convert a given value between the
different units of measurement. Use the :meth:`.toSpaces` method to convert a font units
value to staff spaces, and the :meth:`.toUnits` to do the opposite::

   >>> font.smufl.toSpaces(250)
   1.0
   >>> font.smufl.toUnits(1.0)
   250

.. important::

   The attributes and methods mentioned above depend on the font's units per em value
   which must be set with :attr:`fontParts.base.BaseInfo.unitsPerEm` for measurement
   units conversion to work::

      >>> font.info.unitsPerEm = 1000

Finding glyphs
==============

You can search for a glyph by it's canonical SMuFL name with the
:meth:`Smufl.findGlyph` method::

   >>> font.smufl.findGlyph('barlineSingle')
   <Glyph 'uniE030' ('public.default') at 4393557200>



==============
Other Features
==============

Status Indicators
=================

The :class:`.Smufl` class includes a set of convenient :term:`boolean` checks to
determine a glyph's membership status:

.. list-table::
   
   * - :attr:`~.Smufl.isLigature`
     - Checks if the glyph is a valid ligature
   * - :attr:`~.Smufl.isMember`
     - Checks if the glyph is within the SMuFL glyph range
   * - :attr:`~.Smufl.isOptional`
     - Checks if the glyph is within the optional glyph range
   * - :attr:`~.Smufl.isRecommended`
     - Checks if the glyph is within the recommended glyph range
   * - :attr:`~.Smufl.isSalt`
     - Checks if the glyph is  a stylistic alternate
   * - :attr:`~.Smufl.isSet`
     - Checks if the glyph is a stylistic set glyph

For instance, checking if a glyph is within the accepted range for recommended glyphs in
SMuFL is as easy as::

   >>> if glyph.smufl.isRecommended:
   ...   # do something

.. _running-scripts:

===============
Running Scripts
===============

SMufoLib comes bundled with several useful scripts for building SMuFL metadata files, calculating engraving defaults from glyphs, importing identification attributes and more.

Scripts may be run either directly from the command line or imported as regular python modules, passing in any arguments in the familiar manner to each platform.

As an example, check for missing or superfluous SMuFL anchors and mark discrepant glyphs by running the :mod:`~bin.checkAnchors` script with the ``--mark`` flag directly from the command line:

.. code:: zsh

   $ check-anchors path/to/my/font.ufo --mark

Positional arguments and available options can be listed by running the help command on the script:

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

.. _configuring-smufolib:

====================
Configuring SMufoLib
====================

Content goes here

========================
Making Metadata Requests
========================

Content goes here

================================
Using the Command Line Interface
================================

Content goes here