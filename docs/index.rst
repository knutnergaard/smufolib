SMufoLib: Where SMuFL meets UFO
===============================

**Find glyphs**:

.. doctest::
   :options: +ELLIPSIS, +NORMALIZE_WHITESPACE

   >>> glyph = font.smufl.findGlyph("flag8thUp")
   >>> glyph.smufl.alternateGlyphs
   (<Glyph 'uniE240.ss02' ...>, <Glyph 'uniE240.ss03' ...>)

   >>> ligature = font.smufl.findGlyph("accidentalFlatParens")
   >>> ligature.smufl.componentGlyphs
   (<Glyph 'uniE26A' ...>, <Glyph 'uniE260' ...>, <Glyph 'uniE26B' ...>)

**Work with glyph groups**:

.. doctest::
   :options: +ELLIPSIS, +NORMALIZE_WHITESPACE

   >>> glyph.smufl.classMembers("accidentalsStandard")
   (<Glyph 'uniE260' ...>, <Glyph 'uniE266' ...>, <Glyph 'uniE267' ...>)

   >>> glyph = font["uniE050"]  # gClef
   >>> glyph.smufl.ranges
   (<Range 'clefs' ('U+E050-U+E07F') at ...>,)
   >>> smuflRange = glyph.smufl.ranges[0]
   >>> for g in smuflRange.glyphs:
   ...   g.width += 10

**Access and generate metadata**::

   >>> Request.glyphnames()
   {
      "4stringTabClef": {
         "codepoint": "U+E06E",
         "description": "4-string tab clef"
      },
      "6stringTabClef": {
         "codepoint": "U+E06D",
         "description": "6-string tab clef"
      }, ...

   >>> generateMetadata("path/to/MyFont.ufo") 

**And much more!**

SMufoLib is a lightweight Python library for working with fonts that follow the
`Standard Music Font Layout <https://w3c.github.io/smufl/latest/>`_ (SMuFL). It builds
on the reference implementation of the `FontParts
<https://fontparts.robotools.dev/en/stable/index.html>`_ API and operates directly on
the `Unified Font Object <https://unifiedfontobject.org>`_ (UFO) format.
SMufoLib enhances these foundations with SMuFL-aware tools for music font design,
scripting and metadata management -- all from the command line, without requiring a GUI
font editor.

.. toctree::
   :maxdepth: 1
   :caption: User Guide

   user_guide

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api/objects
   api/request
   api/cli
   api/configuration

.. toctree::
   :maxdepth: 1
   :caption: Utility Modules

   utils

.. toctree::
   :maxdepth: 1
   :caption: Scripts

   scripts

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
