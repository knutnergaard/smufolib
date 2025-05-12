=======
Objects
=======

Base Objects
============

SMufoLib's lowest-level classes subclass the reference implementation of the FontParts API. Only those objects and members that are explicitly overridden are documented here. For a complete reference to all inherited attributes and methods, see the `FontParts documentation <https://fontparts.robotools.dev/en/stable/index.html>`_.

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

.. caution:: 
   
   These classes use :class:`fontParts.base.BaseLib` to store
   property settings. Editing these keys directly may cause problems.

.. automodule:: smufolib.objects.smufl
   :members:

.. automodule:: smufolib.objects.engravingDefaults
   :members:

.. automodule:: smufolib.objects.range
   :members: