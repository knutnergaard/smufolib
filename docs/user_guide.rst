Installation
============

SMufoLib requires `Python <http://www.python.org/download/>`_ 3.10 or
later. It is listed in the `Python Package Index
<https://pypi.org/project/smufolib>`_ (PyPI) and can be installed with
`pip <https://pip.pypa.io/>`__:

.. code-block:: zsh

    $ python -m pip install smufolib

First Steps
===========

Start by importing SMufoLib::

   >>> from smufolib import Font

Then instantiate a font object::

   >>> font = Font("path/to/myFont.ufo")

A font may also be instantiated from another :class:`fontParts.base.BaseFont` object.
This allows SMufoLib to be used seamlessly within other FontParts-based environments,
such as `RoboFont <https://robofont.com>`_::
   
   from smufolib import Font
   from mojo.roboFont import CurrentFont

   font = Font(CurrentFont())


Before going further, it's a good idea to review the FontParts `Object Reference
<https://fontparts.robotools.dev/en/stable/objectref/index.html>`_. SMufoLib's
:class:`.Font`, :class:`.Layer`, and :class:`.Glyph` classes extend FontPart's `defcon
<https://defcon.robotools.dev/en/latest/>`_-based reference implementation and serve as
the foundation for the features described below.

.. _configuring-smufolib:

Configuring SMufoLib
====================

SMufoLib supports customization through a configuration file named `smufolib.cfg`.
This allows you to tailor the library's behavior to specific project needs, such as
disabling automatic engraving calculation or changing default colors for mark glyphs.

Configuration File Structure
----------------------------

The configuration file uses an INI-style format with sections and key-value pairs.

Here is a minimal example:

.. code-block:: ini

   [color.marks]
   mark1 = (1.0, 0.0, 1.0, 1.0)

   [engravingDefaults]
   auto = false

This example changes the primary mark color and disables automatic calculation of
:class:`.EngravingDefaults`.

For a complete list of sections, options, and default values, see the
:ref:`configuration` section of the API documentation.

Configuration File Location
---------------------------

SMufoLib will search for the configuration file in the following order:

   #. The user's home directory (as returned by :func:`os.path.expanduser`)
   #. The current working directory
   #. The path specified by the :envvar:`SMUFOLIB_CFG` environment variable
   #. The SMufoLib installation directory

The first valid file found will be used.

To set a custom configuration path, define the environment variable :envvar:`SMUFOLIB_CFG`:

- On macOS or Linux:

  .. code-block:: zsh

     export SMUFOLIB_CFG=/path/to/smufolib.cfg

  Add this to your shell startup file (e.g., `~/.zshrc` or `~/.bashrc`) to make it persistent.

- On Windows, use the `set` command:

  .. code-block:: bat

     set SMUFOLIB_CFG=C:\path\to\smufolib.cfg

.. note::

   If no valid configuration file is found, SMufoLib falls back to the default
   `smufolib.cfg` located in the library's installation directory.


Setting attributes
==================

SMufoLib provides easy storage of SMuFL-related font and glyph metadata within the font
file itself. Attributes [#]_ can either be set individually during the design process or
imported from metadata files.

Manually Setting Attributes
---------------------------

Attributes are accessed through the :class:`.Smufl` object, and may be set for the font
and individual glyphs::

   >>> font.smufl.name = "myFont"
   >>> font.smufl.version = 1.0
   >>> font.smufl.designSize = 20
   >>> font.smufl.sizeRange = (16, 24)
   >>> glyph = font["uniE050"]
   >>> glyph.smufl.name = "gClef"
   >>> glyph.smufl.description = "G clef"
   >>> glyph.smufl.classes = ("clefs",)

.. note::

   - Some attributes, like :attr:`.Smufl.name`, will return different values depending
     on whether they are accessed through :attr:`.Font.smufl` or :attr:`.Glyph.smufl`.
   - FontParts maintains consistent references to parent-level objects. As a result,
     font-specific :class:`.Smufl` attributes remain accessible from both the font
     itself and any of its glyphs.

Importing Attributes
--------------------

The essential glyph identification attributes (:attr:`.Smufl.name`,
:attr:`.Smufl.description` and :attr:`.Smufl.classes`) may be imported from preexisting
metadata files using the :mod:`~bin.importID` script. See :ref:`running-scripts` for
more information.

.. _working-with-metadata:

Working with metadata
=====================

Once SMuFL specific glyph names and other attributes have been set, SMufoLib provides useful features like:

Glyph Ranges
------------

The SMuFL glyph ranges covered by the entire font -- or by a specific glyph -- can be
accessed via the :attr:`.ranges` attribute on the :class:`.Font` or :class:`.Glyph`
object, respectively::
   
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


Coloring glyphs by range is also really easy with this feature:

.. code-block:: python

   import random
   
   def get_random_color():
      r = random.random()
      g = random.random()
      b = random.random()
      return (r, g, b, 1)
   
   for range in font.smufl.ranges:
       color = get_random_color()
       for glyph in range.glyphs:
           glyph.mark = color

The :class:`.Range` object provides the values for any SMuFL range's 
:attr:`~.Range.name`, :attr:`~.Range.description`, :attr:`~.Range.glyphs`, 
:attr:`~.Range.start` and :attr:`~.Range.end` attributes.

.. _engraving-defaults:

Glyph Classes
-------------

Another way to work with groups of glyphs in SMufoLib is by using SMuFL classes. When imported or set, the :attr:`.Smufl.classes` attribute stores the class names associated
with each glyph::

   >>> glyph = font['uniE260'] # accidentalFlat
   >>> glyph.smufl.classes
   ('accidentals', 'accidentalsSagittalMixed', 
   'accidentalsStandard', 'combiningStaffPositions')

This information can be used to collect glyphs based on their combined class
membership:

.. code-block:: python

   for glyph in font:
      classes = glyph.smufl.classes
      if 'accidentalsStandard' in classes and 'accidentalsSagittalMixed' in classes:
         # do something

The :meth:`.Smufl.classMembers` method provides a convenient way to collect all glyph
members of the specified class::

   >>> glyph.smufl.classMembers("accidentalsStandard")
   (<Glyph 'uniE266' ('public.default') at 4344651664>, 
   <Glyph 'uniE267' ('public.default') at 4349094128>, 
   <Glyph 'uniE264' ('public.default') at 4351472640>, ...)

Engraving Defaults
------------------

Engraving defaults are managed by their own appropriately named
:class:`.EngravingDefaults` object, accessed with the :attr:`.Smufl.engravingDefaults` attribute::

   >>> font.smufl.engravingDefaults
   <EngravingDefaults in font 'MyFont' path='/path/to/myFont.ufo'
   auto=True at 4425372944>
 
Each setting has its own attribute within this object::
   
   >>> ed = font.smufl.engravingDefaults
   >>> ed.stemThickness
   None
   >>> ed.stemThickness = 30
   >>> ed.stemThickness
   30

Engraving defaults are calculated automatically from corresponding glyphs by default --
provided that these glyphs exist. As an example, the value for :attr:`.hairpinThickness`
is based on the shape of the glyph ``'uniE53E'`` (``'dynamicCrescendoHairpin'``). See
:ref:`engraving-defaults-mapping` for a full list of attributes and their corresponding
glyphs.

Override the automatic calculations by setting the attributes to a value other than
:obj:`None`.

To turn the feature off entirely, disable `auto` in the :ref:`[engravingDefaults]`
section of `smufolib.cfg`. See :ref:`configuring-smufolib` for more information
about how to customize SMufoLib's behavior.

Engraving defaults are available in either font units or staff spaces. See
:ref:`changing-measurement-units` for more information.

Anchors
-------

SMufoLib does not currently provide its own anchor object, but a SMuFL specific
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
:mod:`~bin.checkAnchors` to keep track of missing or superfluous SMuFL glyph
anchors in a font. See :ref:`running-scripts` for more information.

.. note::

   Only anchors with names specific to SMuFL are accessible through the :class:`.Smufl`
   object's :attr:`~.Smufl.anchors` attribute. See :py:data:`.ANCHOR_NAMES` for a full
   :class:`set` of available SMuFL anchors.

Glyph Metrics and Dimensions
----------------------------

Similarly to :attr:`~.Smufl.anchors`, the :class:`.Smufl` class also provides a SMuFL-specific
:class:`dict` representation of the glyph bounding box::

   >>> glyph.smufl.bBox
   {'bBoxSW': (0.0, -0.5), 'bBoxNE': (1.18, 0.5)}

Even the glyph advance width is available as :attr:`.Smufl.advanceWidth`::
   
   >>> glyph.smufl.advanceWidth
   671 
   
It differs from the usual :attr:`.Glyph.width` in optionally providing
the value in staff spaces (see :ref:`changing-measurement-units`).

Ligatures and Stylistic Alternates
----------------------------------

Ligatures have their component glyphs readily available with the
:attr:`.componentGlyphs` attribute::

   >>> ligature = font['uniE09E_uniE083_uniE09F_uniE084']
   >>> ligature.smufl.componentGlyphs
   (<Glyph 'uniE09E' ('public.default') at 4399803376>,
   <Glyph 'uniE083' ('public.default') at 4399803184>,
   <Glyph 'uniE09F' ('public.default') at 4399797952>,
   <Glyph 'uniE084' ('public.default') at 4399797760>)

Alternately, components can be listed by their canonical SMuFL names with the
:attr:`.componentNames` attribute::
   
   >>> glyph.smufl.componentNames
   ('timeSigCombNumerator', 'timeSig3',
   'timeSigCombDenominator', 'timeSig4')
   
The :attr:`.alternateGlyphs` and :attr:`.alternateNames` attribute similarly provide
convenient access to a glyph's stylistic alternates, by :class:`.Glyph` object and
SMuFL name respectively. 

A SMuFL-specific metadata representation of the same alternates can be retrieved with
the :attr:`.alternates` attribute::

   >>> glyph = font['uniE050'] # gClef
   >>> glyph.smufl.alternates
   ({'codepoint': 'U+F472', 'name': 'gClefSmall'},)

The inverse base glyph is also accessible through the :attr:`.base` attribute::

   >>> alternate = font['uniE050.ss01']
   >>> alternate.smufl.base
   <Glyph 'uniE050' ('public.default') at 4373577008>

The glyph name suffix is a common characteristic of different types of OpenType
alternates and sets, and may therefore sometimes be necessary to isolate. This is what
the :attr:`.suffix` attribute is for::

   >>> glyph = font['uniE050.ss01']
   >>> glyph.smufl.suffix
   ss01

.. important::

   The attributes in this section demand strict adherence to SMuFL's glyph naming
   standards. See :ref:`this note about glyph naming <about-glyph-naming>` for details.

Status Indicators
-----------------

The :class:`.Smufl` class includes a set of convenient boolean checks to
determine a glyph's membership status:

.. autosummary::
   :nosignatures:

   ~smufolib.objects.smufl.Smufl.isLigature
   ~smufolib.objects.smufl.Smufl.isMember
   ~smufolib.objects.smufl.Smufl.isOptional
   ~smufolib.objects.smufl.Smufl.isRecommended
   ~smufolib.objects.smufl.Smufl.isSalt
   ~smufolib.objects.smufl.Smufl.isSet

For instance, checking if a glyph is within the accepted range for recommended glyphs in
SMuFL is as easy as::

   >>> if glyph.smufl.isRecommended:
   ...   # do something

.. _changing-measurement-units:

Changing Measurement Units
--------------------------

You can get or set engraving defaults, anchor coordinates, glyph bounds and
advance widths in either font units or staff spaces -- whatever suits your workflow. By default, all values are expressed in font units unless changed. To
switch to staff spaces, set either :attr:`.EngravingDefaults.spaces` or
:attr:`.Smufl.spaces` to :obj:`True`, e.g.::

   >>> ed.spaces = True
   >>> ed.stemThickness
   0.12
   >>> ed.stemThickness = 0.14
   >>> ed.spaces = False
   >>> ed.stemThickness
   35
   
.. note::

   - Setting ``font.smufl.engravingDefaults.spaces = True`` is equivalent to setting
     ``font.smufl.spaces = True``, so either one will affect all relevant
     attributes across the entire library.
   
   - This setting is stored in the font's metadata and will persist when saving the font.

The :class:`.Smufl` class also provides methods to convert a given value between the
different units of measurement. Use the :meth:`.toSpaces` method to convert a font units
value to staff spaces, and the :meth:`.toUnits` to do the opposite::

   >>> font.smufl.toSpaces(250)
   1.0
   >>> font.smufl.toUnits(1.0)
   250

.. important::

   Conversion to staff spaces depends on the font's units-per-em (UPM) value. Make sure ``font.info.unitsPerEm`` is set correctly for the conversion to work as expected.

Finding glyphs
--------------

You can search for a glyph by its canonical SMuFL name with the :meth:`.Smufl.findGlyph`
method::

   >>> font.smufl.findGlyph('barlineSingle')
   <Glyph 'uniE030' ('public.default') at 4393557200>
   >>> font.smufl.findGlyph('missingSmuflName')
   None

.. _running-scripts:

Running Scripts
===============

SMufoLib comes bundled with several useful scripts for building SMuFL metadata files, calculating engraving defaults from glyphs, importing identification attributes and more.

Scripts may be run either directly from the command line or imported as regular python modules, passing in any arguments in the familiar manner to each platform.

As an example, check for missing or superfluous SMuFL anchors and mark discrepant glyphs by running the :mod:`~bin.checkAnchors` script with the ``--mark`` flag directly from the command line:

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
                           path to font metadata file (default: <Request '/url/path
                           /to/reference/font/metadata.json' ('/file/path/to/refere
                           nce/font/metadata.json') at 4536666000>)
      -m, --mark           apply defined color values to objects (default: False)
      -c COLOR COLOR COLOR COLOR, --color COLOR COLOR COLOR COLOR
                           list of RGBA color values (default: None)
      -v, --verbose        make output verbose (default: False)


Alternatively, scripts can be imported as modules in Python::

   >>> from bin.checkAnchors import checkAnchors
   >>> checkAnchors(mark=True)

This imports and executes the script's program function,
:func:`~bin.checkAnchors.checkAnchors`, from the script module of the same name.

Making Metadata Requests
========================

SMufoLib provides a :mod:`.request` module to handle web requests and metadata file
operations, facilitating access to updated SMuFL data. Most of this functionality is
handled by the module's :class:`.Request` class.

Standard Metadata Requests
--------------------------

The different metadata support files published under the SMuFL standard, as well as the
metadata file for SMuFL's reference font, Bravura, can be easily retrieved using the
appropriately named :class:`.Request` class methods:

.. autosummary::
   :nosignatures:

   ~smufolib.request.Request.classes
   ~smufolib.request.Request.glyphnames
   ~smufolib.request.Request.ranges
   ~smufolib.request.Request.font

By default, these methods return a parsed Python :class:`dict`. Retrieve a raw
:class:`str` response instead by setting ``decode=False``::

   >>> text = Request.classes(decode=False)
   

Paths and Fallbacks
-------------------

:class:`.Request` can handle both URL and filesystem paths. Pass the path as the first
argument::

   >>> file = Request("path/to/file.json")
   >>> file = Request("https://path/to/file.json")

You can also combine a remote URL with a local fallback file. This enables automatic
fallback to a local copy if the remote request fails due to a connection error::

   >>> file = Request("https://path/to/file.json", "path/to/file.json")

.. note::

   A fallback will only be attempted if a :class:`~urllib.error.URLError` is raised.
   If the primary `path` points to a local file and it fails, the error will be raised
   immediately.

Raw Output
----------

Similarly to the well known HTTP library `Requests
<https://requests.readthedocs.io/en/latest/>_`, SMufoLib's :class:`.Request` object
provides two properties for accessing raw response data:

- Use the :attr:`.text` attribute to get a decoded :class:`str`::

    >>> data = Request("path/to/file.json").text

- Use the :attr:`.content` attribute to get the raw :class:`bytes` content::

    >>> data = Request("path/to/file.json").content

Unless an `encoding` is explicitly specified, text responses will be decoded using UTF-8.

Parsing JSON Files
------------------

If the file is a JSON file, use the built-in :meth:`~.Request.json` method to parse it::

   >>> data = Request("https://path/to/file.json").json()


Writing JSON Files
------------------

The :mod:`.request` module also provides a helper function to simplify the logic
concerned with writing JSON data to a file. Using the :func:`.writeJson` function this is
as simple as::

   >>> jsonDict = {'font': 'MyFont'}
   >>> writeJson('path/to/file.json', jsonDict)

Building Command Line Interfaces
================================

The :mod:`.cli` module provides a flexible and developer-friendly framework,
based on Python's :mod:`argparse` module, for building command-line tools that operate
on SMuFL-based font data and metadata. It is designed to streamline the development of
scripts by offering consistent argument definitions, reusable parsing logic, and
integration with the rest of the smufolib ecosystem.

By using the :func:`.commonParser` utility and the pre-configured
:data:`.CLI_ARGUMENTS`, you can easily construct robust and consistent parsers for your
own scripts.

See the :ref:`command-line-interface` section of the API documentation for a complete
list of available arguments and their default flags.

Features
--------

- A shared set of standardized CLI arguments covering common SMuFL workflows.
- :func:`.commonParser` utility to quickly construct a parser with selected arguments.
- Support for custom help messages and default values.
- Compatibility with extended help formatters for improved :option:`--help` output.
- Type-safe conversions for inputs like JSON strings, RGBA colors, or font file paths.

Creating A Parser
-----------------

To create a simple parser using only predefined arguments:

.. code-block:: python

   from smufolib import cli
   
   parser = cli.commonParser(
       'font', 'clear', includeOtionals=False,
       description="My SMuFL utility", addHelp=True
   )
   
   args = parser.parse_args()
   print(args.font)  # Automatically loaded as a Font object
   print(args.clear)  # Boolean flag (True if --clear is passed)
   print(args.includeOptionals)  # Boolean (False unless --include-optionals is passed))

.. note::

   :func:`.commonParser` automatically converts argument names from camelCase to kebab-case (e.g. ``includeOptionals`` becomes ``--include-optionals``)
   to maintain consistency with common command-line interfaces.

.. _combining-parsers:

Combining Parsers
-----------------

If you want to define your own additional custom arguments, you can combine
:func:`.commonParser` with a separate :class:`argparse.ArgumentParser` object by passing
the function output as a :class:`list` to the `parents` parameter of the class:

.. code-block:: python

   import argparse
   from smufolib import cli

   args = cli.commonParser('font', clear=True, addHelp=False)
   parser = argparse.ArgumentParser(parents=[args],
               description='showcase commonParser')
   parser.add_argument(
       '-m', '--my-argument',
       action='store_true',
       help="do something",
       dest='myArgument'
   )  

.. important::

   When cobining parsers, the `addHelp` argument must be sett to :obj:`False`, otherwise
   the parser will fail (see the `parents
   <https://docs.python.org/3/library/argparse.html#parents>`_ section of the
   :class:`argparse.ArgumentParser` documentation).
   

To avoid conflicts between standard and custom arguments, you can modify the short flag
definitions for each argument in the :ref:`[cli.shortFlags]` section of `smufolib.cfg`.

Creating Help Formatters
------------------------

The CLI framework also supports custom help formatting by combining the different help
fromatters available in the :mod:`argparse` module:

- :class:`~argparse.RawDescriptionHelpFormatter`
- :class:`~argparse.RawTextHelpFormatter`
- :class:`~argparse.ArgumentDefaultsHelpFormatter`
- :class:`~argparse.MetavarTypeHelpFormatter`

Use the :func:`.createHelpFormatter` function to combine the formatters you want when creating your parser:

.. code-block:: python

   import argparse
   from smufolib import cli
   
   formatter = cli.createHelpFormatter(
      ('RawTextHelpFormatter', 'ArgumentDefaultsHelpFormatter')
   )
   parser = argparse.ArgumentParser(
      formatter_class=formatter,
      description='Process SMuFL metadata'
   )

Using the Utility Modules
=========================

SMufoLib includes a whole host of utility functions, spread across several modules.
The sections below provide a summary of some of the most useful features for
external use.

Conversion
----------

The :mod:`.converters` module provides helper functions for converting between different
measurement formats, Unicode codepoints, and naming styles. Functions include:

.. autosummary::
   :nosignatures:

   ~smufolib.utils.converters.convertMeasurement
   ~smufolib.utils.converters.toDecimal
   ~smufolib.utils.converters.toUniHex
   ~smufolib.utils.converters.toUniName
   ~smufolib.utils.converters.toNumber
   ~smufolib.utils.converters.toIntIfWhole
   ~smufolib.utils.converters.toKebab

Errors and Warnings
-------------------

The :mod:`.error` module  provides functions to generate error messages, check types,
and suggest corrections for invalid values. It includes a dictionary of
:data:`.ERROR_TEMPLATES` to ensure streamlined and consistent error reporting. Functions
include:

.. autosummary::
   :nosignatures:

   ~smufolib.utils.error.generateErrorMessage
   ~smufolib.utils.error.generateTypeError
   ~smufolib.utils.error.validateType
   ~smufolib.utils.error.suggestValue

Contours and Measuring
----------------------

The :mod:`.rulers` module provides functions to extract glyph contours, segments and
points and calculate glyph geometry used in engraving analysis. Functions include:

Contour Tools
^^^^^^^^^^^^^

.. autosummary::
   :nosignatures:

   ~smufolib.utils.rulers.getGlyphContours
   ~smufolib.utils.rulers.getGlyphSegments
   ~smufolib.utils.rulers.getGlyphPoints
   ~smufolib.utils.rulers.getParentSegment
   ~smufolib.utils.rulers.combineBounds

Rulers
^^^^^^

.. autosummary::
   :nosignatures:

   ~smufolib.utils.rulers.glyphBoundsHeight
   ~smufolib.utils.rulers.glyphBoundsWidth
   ~smufolib.utils.rulers.glyphBoundsXMinAbs
   ~smufolib.utils.rulers.xDistanceStemToDot
   ~smufolib.utils.rulers.xDistanceBetweenContours
   ~smufolib.utils.rulers.yDistanceBetweenContours
   ~smufolib.utils.rulers.xStrokeWidthAtOrigin
   ~smufolib.utils.rulers.yStrokeWidthAtMinimum
   ~smufolib.utils.rulers.wedgeArmStrokeWidth

Boolean Checks
^^^^^^^^^^^^^^

.. autosummary::
   :nosignatures:

   ~smufolib.utils.rulers.areAlligned
   ~smufolib.utils.rulers.hasHorizontalOffCurve
   ~smufolib.utils.rulers.hasVerticalOffCurve

Footnotes
=========

.. [#] Most of the objects referred to as "attributes" in this user guide are
   technically implemented as Python properties, but referred to as attributes for
   clarity and consistency with general terminology.
