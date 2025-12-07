.. include:: ../README.rst
    :start-after: .. _installation:

First Steps
===========

Start by importing SMufoLib:

    >>> from smufolib import Font

Then instantiate a font object:

    >>> font = Font("path/to/MyFont.ufo")  # doctest: +SKIP

A font may also be instantiated from another :class:`fontParts.base.BaseFont` object.
This allows SMufoLib to be used seamlessly within other FontParts-based environments,
such as `RoboFont <https://robofont.com>`_::
   
    from smufolib import Font
    from mojo.roboFont import CurrentFont

    font = Font(CurrentFont())


Before going further, it's a good idea to review the FontParts :fontParts:`Object
Reference <objectref/index.html>`. SMufoLib's :class:`.Font`, :class:`.Layer`, and
:class:`.Glyph` classes extend FontPart's `defcon
<https://defcon.robotools.dev/en/stable/>`_-based reference implementation and serve as
the foundation for the features described below.

.. note::

    SMufoLib is designed to work with the default layer of a UFO font. SMuFL metadata is
    stored in the font-level and glyph-level :class:`Lib <fontParts.base.BaseLib>`
    objects, which are shared across all layers. As such, SMufoLib does not interact
    with or expose any layer-specific functionality.

.. _configuring-smufolib:

Configuring SMufoLib
====================

SMufoLib supports customization through a configuration file, allowing you to tailor the
library's behavior to project- or user-specific needs.

Configuration File Structure
----------------------------

The configuration file uses an `INI-style
<https://docs.python.org/3/library/configparser.html#supported-ini-file-structure>`_
format with sections and key-value pairs. 

A minimal example:

.. code-block:: ini

    [color.marks]
    mark1 = (1.0, 0.0, 1.0, 1.0)

    [engravingDefaults]
    auto = false

This example changes the primary mark color and disables automatic calculation of
:class:`.EngravingDefaults`.

For a complete list of sections, options, and default values, see the
:ref:`sections-and-options` section of the API documentation.

Configuration File Discovery
----------------------------

SMufoLib reads configuration files in layers, allowing local project or user-specific
settings to override the default package configuration.

You can pass a specific `path` argument when calling :func:`.config.load`, which will
take ultimate precedence over any other sources (see :ref:`reading-configurations`). Otherwise, the following locations are checked in order of increasing precedence:

1. Current working directory (`./smufolib.cfg`)
2. Home directory (`~/.smufolib.cfg`) as returned by :func:`os.path.expanduser`
3. Environment variable :envvar:`SMUFOLIB_CFG`

Files found later in the list override values from earlier files. You only need to
include the keys you want to change; all unspecified values are inherited from the
defaults.

To define the environment variable :envvar:`SMUFOLIB_CFG`:

- On macOS or Linux:

    .. code-block:: console

        export SMUFOLIB_CFG=/path/to/smufolib.cfg

  Add this to your shell startup file (e.g., `~/.zshrc` or `~/.bashrc`) to make it persistent.

- On Windows, use the `set` command:

    .. code-block:: bat

        set SMUFOLIB_CFG=C:\path\to\smufolib.cfg

.. seealso::

   For details on which filenames are auto-discovered, see :ref:`About Configuration File Naming <about-configuration-file-naming>`.

.. _reading-configurations:

Reading Configurations
----------------------

If you want to access the configurations in your scripts, the :func:`.config.load`
function will return a parsed instance of it as a :class:`dict`:

    >>> from smufolib import config
    >>> cfg = config.load()
    >>> cfg["request"]
    {'encoding': 'utf-8', 'warn': True}

See the :mod:`argparse` documentation for more info on working with configuration files.

.. _glyph-management:

Glyph Management
================

The :class:`.Smufl` class provides a SMuFL-aware interface to the font, enabling glyph
access and manipulation by canonical SMuFL names, [#]_ using familiar dictionary operations.

To insert the glyph U+E000 (*brace*):

    >>> from smufolib import Glyph
    >>> glyph = Glyph()
    >>> font.smufl["brace"] = glyph

For glyphs in the :smufl:`recommended <about/recommended-chars-optional-glyphs.html>`
SMuFL range, this automatically assigns the correct Unicode and font glyph name:

    >>> glyph = font.smufl["brace"]
    >>> glyph.name
    'uniE000'
    >>> glyph.unicode
    57344

For optional or custom SMuFL glyphs, the given name is used as the glyph name, and no
Unicode value is assigned unless explicitly set.

You can also create new glyphs via the :meth:`.Smufl.newGlyph` method, which represents
a SMuFL-specific equivalent to :meth:`Font.newGlyph <fontParts.base.BaseFont.newGlyph>`, allowing creation by SMuFL name rather than glyph
name:

    >>> glyph = font.smufl.newGlyph("brace")

To remove a SMuFL glyph, use the :keyword:`del` statement:

    >>> del font.smufl["brace"]


Setting Attributes
==================

SMufoLib stores SMuFL-specific font and glyph metadata directly within the font file.
Attributes [#]_ can either be set individually during the design process or imported
from metadata files.

Manually Setting Attributes
---------------------------

Attributes are accessed through the :class:`.Smufl` object, and may be set for the font
and individual glyphs:

    >>> font.smufl.name = "MyFont"
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

Working with Metadata
=====================

Once SMuFL specific glyph names and other attributes have been set, SMufoLib provides useful features like:

Glyph Ranges
------------

You can introspect the SMuFL glyph ranges that apply to the font as a whole or to
individual glyphs are accessible via the following attributes:

- ``font.smufl.ranges`` -- Returns a :class:`tuple` containing all SMuFL ranges in the
  font.
- ``glyph.smufl.ranges`` -- Returns a :class:`tuple` containing the SMuFL range that the
  glyph belongs to.

Like :class:`.Smufl`, the :class:`.Range` object behaves like a collection of
:class:`.Glyph` instances. It is particularly useful when working with multiple glyphs
by type:

    >>> for glyph in font:
    ...     for range in glyph.smufl.ranges:
    ...         if range.name == "staffBracketsAndDividers":
    ...             glyph.moveBy = (12, 0)


Coloring glyphs by range is also straightforward when using this object:

.. testcode::

    import random
   
    def get_random_color():
        r = random.random()
        g = random.random()
        b = random.random()
        return (r, g, b, 1)
   
    for range in font.smufl.ranges:
        color = get_random_color()
        for glyph in range:
            glyph.mark = color

The :class:`.Range` object provides range-specific :ref:`glyph management
<glyph-management>` as well as access to a SMuFL range's :attr:`~.Range.name`,
:attr:`~.Range.description`, :attr:`~.Range.start` and :attr:`~.Range.end` attributes.

The :attr:`.Range.glyphs` attribute returns a :class:`tuple` of :class:`.Glyph`
instances belonging to the range, while :meth:`.Range.keys` returns a :class:`tuple` of
their canonical SMuFL names.

.. note:: 

    Attempting to insert a glyph whose Unicode value is not within the range's bounds will raise a :class:`ValueError`.

Ranges are read-only by default, but may be made editable with the
:confval:`ranges.editable` configuration setting. When enabled, custom ranges may be
added using the :meth:`.Smufl.newRange` method:

    >>> font.smufl.newRange(  # doctest: +SKIP
    ...     "myRange", 0xF500, 0xF50F, "A Range of custom glyphs."
    ... )

.. _engraving-defaults:

Glyph Classes
-------------

Another way to work with groups of glyphs in SMufoLib is by using SMuFL classes. When imported or set, the :attr:`.Smufl.classes` attribute stores the class names associated
with each glyph:

.. doctest::
    :options: +NORMALIZE_WHITESPACE

    >>> glyph = font["uniE260"]  # accidentalFlat
    >>> glyph.smufl.classes
    ('accidentals', 'accidentalsSagittalMixed', 
    'accidentalsStandard', 'combiningStaffPositions')

This information can be used to collect glyphs based on their combined class
membership:

.. testcode::

    for glyph in font:
        classes = glyph.smufl.classes
        if "accidentalsStandard" in classes and "accidentalsSagittalMixed" in classes:
            ...

The :meth:`.Smufl.classMembers` method provides a convenient way to collect all glyph
members of the specified class:

.. doctest::
    :options: +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> glyph.smufl.classMembers("accidentalsStandard")
    (<Glyph 'uniE260' ['accidentalFlat'] ('public.default') at ...>,
    <Glyph 'uniE266' ['accidentalTripleFlat'] ('public.default') at ...>, 
    <Glyph 'uniE267' ['accidentalNaturalFlat'] ('public.default') at ...>)
    
By default class names are limited to those specified in the :smufl:`SMuFL specification
<specification/classes.html>`. To allow custom class names, disable the
:confval:`classes.strict` configuration setting.

Engraving Defaults
------------------

Engraving defaults are managed by their own appropriately named
:class:`.EngravingDefaults` object, accessed with the :attr:`.Smufl.engravingDefaults`
attribute:

.. doctest::
    :options: +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> font.smufl.engravingDefaults
    <EngravingDefaults in font 'MyFont Regular' 
    path='/path/to/MyFont.ufo' auto=True at ...>
 
Each setting has its own attribute within this object:
   
    >>> ed = font.smufl.engravingDefaults
    >>> ed.stemThickness = 30
    >>> ed.stemThickness
    30

Engraving defaults are calculated automatically from corresponding glyphs by default --
provided that these glyphs exist. As an example, the value for :attr:`.hairpinThickness`
is based on the shape of the glyph U+E53E (*dynamicCrescendoHairpin*). See
:data:`.ENGRAVING_DEFAULTS_MAPPING` for a full list of attributes and their corresponding
glyphs.

Override the automatic calculations by setting the attributes to a value other than
:obj:`None`.

To turn the feature off entirely, disable :confval:`engravingDefaults.auto`. See
:ref:`configuring-smufolib` for more information about how to customize SMufoLib's
behavior.

Engraving defaults are available in either font units or staff spaces. See
:ref:`changing-measurement-units` for more information.

Anchors
-------

SMufoLib does not currently provide its own anchor object, but a SMuFL specific
representation of a glyph's anchors is available from the :attr:`.Smufl.anchors`
attribute:

.. doctest::
    :options: +NORMALIZE_WHITESPACE
   
    >>> glyph = font["uniE240"]  # flag8thUp
    >>> glyph.smufl.anchors
    {'graceNoteSlashNE': (321, -199), 
    'graceNoteSlashSW': (-161, -614), 
    'stemUpNW': (0, -10)}

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
:class:`dict` representation of the glyph bounding box:
   
    >>> glyph = font["uniE050"]  # gClef
    >>> glyph.smufl.bBox
    {'bBoxSW': (0, -634), 'bBoxNE': (648, 1167)}

Even the glyph advance width is available as :attr:`.Smufl.advanceWidth`:
   
    >>> glyph.smufl.advanceWidth = 648
    >>> glyph.smufl.advanceWidth
    648 
   
It differs from the usual :attr:`Glyph.width <fontParts.base.BaseGlyph.width>` in
optionally providing the value in staff spaces (see :ref:`changing-measurement-units`).

Ligatures and Stylistic Alternates
----------------------------------

Ligatures have their component glyphs readily available with the
:attr:`.componentGlyphs` attribute:

.. doctest::
    :options: +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> ligature = font["uniE26A_uniE260_uniE26B"]
    >>> ligature.smufl.componentGlyphs
    (<Glyph 'uniE26A' ['accidentalParensLeft'] ('public.default') at ...>,
    <Glyph 'uniE260' ['accidentalFlat'] ('public.default') at ...>,
    <Glyph 'uniE26B' ['accidentalParensRight'] ('public.default') at ...>)

Alternately, components can be listed by their canonical SMuFL names with the
:attr:`.componentNames` attribute:
   
    >>> ligature.smufl.componentNames
    ('accidentalParensLeft', 'accidentalFlat', 'accidentalParensRight')
   
The :attr:`.alternateGlyphs` and :attr:`.alternateNames` attribute similarly provide
convenient access to a glyph's stylistic alternates, by :class:`.Glyph` object and
SMuFL name respectively. 

A SMuFL-specific metadata representation of the same alternates can be retrieved with
the :attr:`.alternates` attribute:

    >>> glyph = font["uniE050"]  # gClef
    >>> glyph.smufl.alternates
    ({'codepoint': 'U+F472', 'name': 'gClefSmall'},)

The inverse base glyph is also accessible through the :attr:`.base` attribute:

    >>> alternate = font["uniE050.ss01"]
    >>> alternate.smufl.base
    <Glyph 'uniE050' ['gClef'] ('public.default') at ...>

The glyph name suffix is a common characteristic of different types of OpenType
alternates and sets, and may therefore sometimes be necessary to isolate. This is what
the :attr:`.suffix` attribute is for:

    >>> glyph = font["uniE050.ss01"]
    >>> glyph.smufl.suffix
    'ss01'

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
SMuFL is as easy as:

    >>> if glyph.smufl.isRecommended:
    ...     ...

.. _changing-measurement-units:

Changing Measurement Units
--------------------------

You can get or set engraving defaults, anchor coordinates, glyph bounds and
advance widths in either font units or staff spaces -- whatever suits your workflow. By default, all values are expressed in font units unless changed. To
switch to staff spaces, set either :attr:`.EngravingDefaults.spaces` or
:attr:`.Smufl.spaces` to :obj:`True`, e.g.:

    >>> ed = font.smufl.engravingDefaults
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
value to staff spaces, and the :meth:`.toUnits` to do the opposite:

    >>> font.smufl.toSpaces(250)
    1.0
    >>> font.smufl.toUnits(1.0)
    250

.. important::

    Conversion to staff spaces depends on the font's units-per-em (UPM) value. Make sure
    :attr:`BaseInfo.unitsPerEm <fontParts.base.BaseInfo.unitsPerEm>` is set correctly
    for the conversion to work as expected, e.g.:
   
        >>> font.info.unitsPerEm = 1000

.. _running-scripts:

Running Scripts
===============

SMufoLib comes bundled with several useful scripts for building SMuFL metadata files,
importing anchors, setting identification attributes and more.

Scripts may be run either directly from the command line or imported as regular python modules, passing in any arguments in the familiar manner to each platform.

As an example, check for missing or superfluous SMuFL anchors and mark discrepant glyphs
by running the :ref:`check-anchors` script with the :option:`check-anchors --mark` flag
directly from the command line:

.. code-block:: console

    $ check-anchors path/to/my/font.ufo --mark

Positional arguments and available options can be listed by running the help command on the script:

.. code-block:: console

    $ check-anchors --help

    usage: check-anchors [-h] [-F FONTDATA] [-m] [-c COLOR COLOR COLOR COLOR] [-v] font
    
    Check SMuFL glyph anchors against reference font metadata.
    
    positional arguments:
      font                  path to UFO file
    
    options:
      -h, --help            show this help message and exit
      -F FONTDATA, --font-data FONTDATA
                            path to font metadata file
      -m, --mark            apply defined color values to objects
      -c COLOR COLOR COLOR COLOR, --color COLOR COLOR COLOR COLOR
                            list of RGBA color values
      -v, --verbose         make output verbose


Alternatively, scripts can be imported as modules in Python:

    >>> from bin.checkAnchors import checkAnchors
    >>> checkAnchors(mark=True)  # doctest: +SKIP

This imports and executes the script's program function,
:func:`~bin.checkAnchors.checkAnchors`, from the script module of the same name.

Making Metadata Requests
========================

SMufoLib provides a :mod:`.request` module to handle web requests and metadata file
operations, facilitating access to updated SMuFL data. Most of this functionality is
handled by the module's :class:`.Request` class, which may be imported directly:

    >>> from smufolib import Request

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
:class:`str` response instead by setting ``decode=False``:

    >>> text = Request.classes(decode=False)
   

Paths and Fallbacks
-------------------

:class:`.Request` can handle both URL and filesystem paths. Pass the path as the first
argument:

    >>> file = Request("path/to/file.json")  # doctest: +SKIP
    >>> file = Request("https://path/to/file.json")  # doctest: +SKIP

You can also combine a remote URL with a local fallback file. This enables automatic
fallback to a local copy if the remote request fails due to a connection error:

    >>> file = Request("https://path/to/file.json", "path/to/file.json")  # doctest: +SKIP

.. note::

    A fallback will only be attempted if a :class:`~urllib.error.URLError` is raised.
    If the primary `path` points to a local file and it fails, the error will be raised
    immediately.

Raw Output
----------

Similarly to the well known HTTP library `Requests
<https://requests.readthedocs.io/en/latest/>_`, SMufoLib's :class:`.Request` object
provides two properties for accessing raw response data:

- Use the :attr:`.text` attribute to get a decoded :class:`str`:

    >>> data = Request("path/to/file.json").text  # doctest: +SKIP

- Use the :attr:`.content` attribute to get the raw :class:`bytes` content:

    >>> data = Request("path/to/file.json").content  # doctest: +SKIP

Unless an `encoding` is explicitly specified, text responses will be decoded using UTF-8.

Parsing JSON Files
------------------

If the file is a JSON file, use the built-in :meth:`~.Request.json` method to parse it:

    >>> data = Request("https://path/to/file.json").json()  # doctest: +SKIP


Writing JSON Files
------------------

The :mod:`.request` module also provides a helper function to simplify the logic
concerned with writing JSON data to a file. Using the :func:`.writeJson` function this
is as simple as:

    >>> from smufolib.request import writeJson  # doctest: +SKIP
    >>> jsonDict = {"font": "MyFont"}  # doctest: +SKIP
    >>> writeJson("path/to/file.json", jsonDict)  # doctest: +SKIP

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

See the :ref:`cli-framework` section of the API documentation for a complete
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

.. testcode::

    from smufolib import commonParser
    
    parser = commonParser(
       "font", "clear", includeOptionals=False,
       description="My SMuFL utility", addHelp=True
       )

.. note::

    :func:`.commonParser` automatically converts argument names from camelCase to kebab-case (e.g., ``includeOptionals`` becomes ``--include-optionals``)
    to maintain consistency with common command-line interfaces.

.. _combining-parsers:

Combining Parsers
-----------------

If you want to define your own additional custom arguments, you can combine
:func:`.commonParser` with a separate :class:`argparse.ArgumentParser` object by passing
the function output as a :class:`list` to the `parents` parameter of the class:

.. testcode::

    import argparse
    from smufolib import commonParser

    args = commonParser("font", clear=True, addHelp=False)
    parser = argparse.ArgumentParser(
        parents=[args],
        description="showcase commonParser"
    )
    parser.add_argument(
        "-m", "--my-argument",
        action="store_true",
        help="do something",
        dest="myArgument"
    )  

.. important::

   When cobining parsers, the `addHelp` argument must be sett to :obj:`False`, otherwise
   the parser will fail (see the `parents
   <https://docs.python.org/3/library/argparse.html#parents>`_ section of the
   :class:`argparse.ArgumentParser` documentation).
   

To avoid conflicts between standard and custom arguments, you can modify the short flag
definitions for each argument in the :ref:`cli.shortFlags` section of `smufolib.cfg`.

Creating Help Formatters
------------------------

The CLI framework also supports custom help formatting by combining the different help
formatters available in the :mod:`argparse` module:

- :class:`~argparse.RawDescriptionHelpFormatter`
- :class:`~argparse.RawTextHelpFormatter`
- :class:`~argparse.ArgumentDefaultsHelpFormatter`
- :class:`~argparse.MetavarTypeHelpFormatter`

Use the :func:`.createHelpFormatter` function to combine the formatters you want when creating your parser:

.. testcode::

    import argparse
    from smufolib import cli
    
    formatter = cli.createHelpFormatter(
        ("RawTextHelpFormatter", "ArgumentDefaultsHelpFormatter")
    )
    parser = argparse.ArgumentParser(
        formatter_class=formatter,
        description="Process SMuFL metadata"
    )

Using the Utility Modules
=========================

SMufoLib includes a whole host of utility functions, spread across several modules. The
sections below summarize some of the most useful features for external use.

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

.. [#] The term *Canonical SMuFL name* refers to the official descriptive glyph names as
   defined in the :smufl:`SMuFL specification <>`.

.. [#] Most of the objects referred to as "attributes" in this user guide are
   technically implemented as Python properties, but referred to as attributes for
   clarity and consistency with general terminology.
   