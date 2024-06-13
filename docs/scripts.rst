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

.. autofunction:: bin.checkAnchors.main(font, fontData=Request(CONFIG['metadata.paths']['referenceFont'], CONFIG['metadata.fallbacks']['referenceFont']), mark=False, color=None)


:mod:`generateMetadata`
-----------------------

.. automodule:: bin.generateMetadata

.. autofunction:: bin.generateMetadata.main(font, targetDir, fontData=Request(CONFIG['metadata.paths']['referenceFont'], CONFIG['metadata.fallbacks']['referenceFont']))


:mod:`importAnchors`
--------------------

.. automodule:: bin.importAnchors

.. autofunction:: bin.importAnchors.main(font, fontData=Request(CONFIG['metadata.paths']['referenceFont'], CONFIG['metadata.fallbacks']['referenceFont']), mark=True, colors=CONFIG['color.anchors'], clear=False)


:mod:`importID`
---------------

.. automodule:: bin.importID

.. autofunction:: bin.importID.main(font, attributes, classesData=Request(CONFIG['metadata.paths']['classes'], CONFIG['metadata.fallbacks']['classes']), glyphnamesData=Request(CONFIG['metadata.paths']['glyphnames'], CONFIG['metadata.fallbacks']['glyphnames']), fontData=Request(CONFIG['metadata.paths']['referenceFont'], CONFIG['metadata.fallbacks']['referenceFont']), includeOptionals=False, overwrite=False)
