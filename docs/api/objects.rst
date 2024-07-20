=======
Objects
=======

Base Objects
============

SMufoLib's most low-level classes are simply implementations of
the :mod:`fontParts.base` equivalents. As such, SMufoLib provides easy
access to an entire common font development API in addition to
functionality specific to SMuFL. Please see the `FontParts
documentation <https://fontparts.robotools.dev/en/stable/index.html>`_
for further reference.

.. automodule:: smufolib.objects.font
   :members:
   :exclude-members: layerClass

.. automodule:: smufolib.objects.glyph
   :members:

.. automodule:: smufolib.objects.layer
   :members:
   :exclude-members: glyphClass

Core Objects
============

The following classes handle SMufoLib's metadata collection, storage and
manipulation.

.. caution:: These classes use :class:`fontParts.base.BaseLib` to store
   property settings. Editing these keys directly may cause problems.

.. automodule:: smufolib.objects.smufl
   :members: Smufl

.. automodule:: smufolib.objects.engravingDefaults
   :members: EngravingDefaults

.. automodule:: smufolib.objects.range
   :members:

Constants
=========

The core object modules contain the following convenience constants
which may be imported directly from the main module.

.. automodule:: smufolib.objects.smufl
   :members: ANCHOR_NAMES, FONT_ATTRIBUTES, GLYPH_ATTRIBUTES
   :noindex:

.. automodule:: smufolib.objects.engravingDefaults
   :members: ENGRAVING_DEFAULTS_KEYS
   :noindex:

