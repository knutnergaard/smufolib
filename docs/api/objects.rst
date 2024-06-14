.. module:: smufolib.objects

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

.. automodule:: smufolib.objects.glyph
   :members:

.. automodule:: smufolib.objects.layer
   :members:

Core Objects
============

The following classes represent SMufoLib's metadata collection classes.

.. caution:: These classes use :class:`fontParts.base.BaseLib` to store
   property settings. Editing these keys directly may cause problems.

.. automodule:: smufolib.objects.smufl
   :members:

.. automodule:: smufolib.objects.engravingDefaults
   :members:

.. automodule:: smufolib.objects.range
   :members:
