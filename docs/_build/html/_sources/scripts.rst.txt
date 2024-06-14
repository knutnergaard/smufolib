.. module:: bin
.. module:: smufolib
    :noindex:


:mod:`calculateEngravingDefaults`
---------------------------------

.. automodule:: bin.calculateEngravingDefaults
    :members:


:mod:`checkAnchors`
-------------------

.. automodule:: bin.checkAnchors

.. autofunction:: bin.checkAnchors.checkAnchors(font, fontData=Request(CONFIG['metadata.paths']['referenceFont'], CONFIG['metadata.fallbacks']['referenceFont']), mark=False, color=None, verbose=False)
.. autofunction:: bin.checkAnchors.main


:mod:`generateMetadata`
-----------------------

.. automodule:: bin.generateMetadata

.. autofunction:: bin.generateMetadata.generateMetadata(font, targetDir, fontData=Request(CONFIG['metadata.paths']['referenceFont'], CONFIG['metadata.fallbacks']['referenceFont']))
.. autofunction:: bin.generateMetadata.main


:mod:`importAnchors`
--------------------

.. automodule:: bin.importAnchors

.. autofunction:: bin.importAnchors.importAnchors(font, fontData=Request(CONFIG['metadata.paths']['referenceFont'], CONFIG['metadata.fallbacks']['referenceFont']), mark=True, colors=CONFIG['color.anchors'], clear=False)
.. autofunction:: bin.importAnchors.main


:mod:`importID`
---------------

.. automodule:: bin.importID

.. autofunction:: bin.importID.importID(font, attributes, classesData=Request(CONFIG['metadata.paths']['classes'], CONFIG['metadata.fallbacks']['classes']), glyphnamesData=Request(CONFIG['metadata.paths']['glyphnames'], CONFIG['metadata.fallbacks']['glyphnames']), fontData=Request(CONFIG['metadata.paths']['referenceFont'], CONFIG['metadata.fallbacks']['referenceFont']), includeOptionals=False, overwrite=False)
.. autofunction:: bin.importID.main
