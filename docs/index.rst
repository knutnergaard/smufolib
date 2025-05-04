SMufoLib: Where SMuFL meets UFO
===============================

**Find glyphs and their alternates**::

   >>> glyph = font.smufl.findGlyph("flag8thUp")
   >>> glyph.smufl.alternateGlyphs
   (<Glyph 'uniE240.salt01' ('public.default') at 4377042592>,
    <Glyph 'uniE240.ss02' ('public.default') at 4377044992>, 
    <Glyph 'uniE240.ss03' ('public.default') at 4377046672>)

**Work with values in staff spaces**::

   >>> glyph.smufl.anchors
   {"graceNoteSlashNE": (321, -199)}
   >>> font.smufl.spaces = True
   >>> glyph.smufl.anchors
   {"graceNoteSlashNE": (1.284, -0.796)}

**Check content against metadata**::

   >>> glyphnamesJson = Request.glyphnames()
   >>> glyph.smufl.name in glyphnamesJson
   True

**And much more!**

SMufoLib is a lightweight Python library for working with fonts that follow the
`Standard Music Font Layout <https://w3c.github.io/smufl/latest/>`_ (SMuFL). Built on
top of the `FontParts <https://fontparts.robotools.dev/en/stable/index.html>`_ API, it
extends the `Unified Font Object <https://unifiedfontobject.org>`_ (UFO) format with
SMuFL-aware tools for music font design, scripting and metadata management — all from the command line, without requiring a GUI font editor.

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
