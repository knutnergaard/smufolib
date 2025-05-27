.. _configuration:

=============
Configuration
=============

User defined default settings for SMufoLib are set in the configuration file :ref:`smufolib.cfg` and parsed by the :mod:`.config` module. Detailed information on how SMufoLib handles configuration is provided in the following sections.

.. automodule:: smufolib.config
    :members:

.. _smufolib.cfg:

smufolib.cfg
============

The SMufoLib configuration file `smufolib.cfg` contains default settings for SMufoLib.
It contains three main sections, with sub-sections denoted by a preceding dot, and
settings for warnings, URL and file paths and colors.

.. _request:

request
-------

This section contains configuration for the :class:`.Request` class.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [request]
    :end-before: [metadata.paths]

.. confval:: request.encoding
    :type: ``str``
    :default: ``utf-8``

    The default encoding used for :class:`.Request`.

.. confval:: request.warn
    :type: ``bool``
    :default: ``true``

    Whether to issue warnings for :class:`.Request`.

.. _metadata.paths:

metadata.paths
--------------

Primary metadata paths are configured in this section.


.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [metadata.paths]
    :end-before: [metadata.fallbacks]

.. confval:: metadata.paths.directory
    :type: ``str``
    :default: ``https://raw.githubusercontent.com/w3c/smufl/gh-pages/metadata/``

    The base directory for metadata paths. This may be used to construct the full paths
    for metadata files using :class:`configparser.ExtendedInterpolation` (``${directory}``).

.. confval:: metadata.paths.classes
    :type: ``str``
    :default: ``${directory}classes.json``

    The primary path to the classes metadata file.

.. confval:: metadata.paths.glyphnames
    :type: ``str``
    :default: ``${directory}glyphnames.json``

    The primary path to the glyph names metadata file.

.. confval:: metadata.paths.ranges
    :type: ``str``
    :default: ``${directory}ranges.json``

    The primary path to the ranges metadata file.

.. confval:: metadata.paths.font
    :type: ``str``
    :default: ``${directory}font.json``

    The primary path to the font metadata file.

.. _metadata.fallbacks:

metadata.fallbacks
------------------

Metadata fallback paths are configured in this section.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [metadata.fallbacks]
    :end-before: [cli.shortFlags]

.. confval:: metadata.fallbacks.directory
    :type: ``str``
    :default: ``./metadata/``

    The base directory for metadata fallbacks. This may be used to construct the full
    paths for metadata files using :class:`configparser.ExtendedInterpolation`
    (``${directory}``).

.. confval:: metadata.fallbacks.classes
    :type: ``str``
    :default: ``${directory}classes.json``

    The fallback path to the classes metadata file.

.. confval:: metadata.fallbacks.glyphnames
    :type: ``str``
    :default: ``${directory}glyphnames.json``

    The fallback path to the glyph names metadata file.

.. confval:: metadata.fallbacks.ranges
    :type: ``str``
    :default: ``${directory}ranges.json``

    The fallback path to the ranges metadata file.

.. confval:: metadata.fallbacks.font
    :type: ``str``
    :default: ``${directory}font.json``

    The fallback path to the font metadata file.

.. _cli.shortFlags:

cli.shortFlags
--------------

Short flags for :ref:`cli-framework` options to be used with
:func:`~smufolib.cli.commonParser` are configured in this section.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [cli.shortFlags]
    :end-before: [color.marks]


.. confval:: cli.shortFlags.attributes
    :type: ``str``
    :default: ``-a``

    Short flag equivalent to the ``--attributes`` option in the :ref:`cli-framework`.
    
.. confval:: cli.shortFlags.classesData
    :type: ``str``
    :default: ``-C``

    Short flag equivalent to the ``--classes-data`` option in the :ref:`cli-framework`.
    
.. confval:: cli.shortFlags.clear
    :type: ``str``
    :default: ``-x``

    Short flag equivalent to the ``--clear`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.color
    :type: ``str``
    :default: ``-c``

    Short flag equivalent to the ``--color`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.colors
    :type: ``str``
    :default: ``-c``

    Short flag equivalent to the ``--colors`` option in the :ref:`cli-framework`.
    
.. confval:: cli.shortFlags.exclude
    :type: ``str``
    :default: ``-e``

    Short flag equivalent to the ``--exclude`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.font
    :type: ``str``
    :default: ``-f``

    Short flag equivalent to the ``--font`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.fontData
    :type: ``str``
    :default: ``-F``

    Short flag equivalent to the ``--font-data`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.glyphnamesData
    :type: ``str``
    :default: ``-G``

    Short flag equivalent to the ``--glyphnames-data`` option in the
    :ref:`cli-framework`.

.. confval:: cli.shortFlags.include
    :type: ``str``
    :default: ``-i``

    Short flag equivalent to the ``--include`` option in the :ref:`cli-framework`.
    
.. confval:: cli.shortFlags.includeOptionals
    :type: ``str``
    :default: ``-O``

    Short flag equivalent to the ``--include-optionals`` option in the :ref:`cli-framework`.
    
.. confval:: cli.shortFlags.mark
    :type: ``str``
    :default: ``-m``

    Short flag equivalent to the ``--mark`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.overwrite
    :type: ``str``
    :default: ``-o``

    Short flag equivalent to the ``--overwrite`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.rangesData
    :type: ``str``
    :default: ``-r``

    Short flag equivalent to the ``--ranges-data`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.sourcePath
    :type: ``str``
    :default: ``-S``

    Short flag equivalent to the ``--source-path`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.spaces
    :type: ``str``
    :default: ``-s``

    Short flag equivalent to the ``--spaces`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.targetPath
    :type: ``str``
    :default: ``-T``

    Short flag equivalent to the ``--target-path`` option in the :ref:`cli-framework`.

.. confval:: cli.shortFlags.verbose
    :type: ``str``
    :default: ``-v``

    Short flag equivalent to the ``--verbose`` option in the :ref:`cli-framework`.


.. _color.marks:

color.marks
-----------

:ref:`type-color` values for glyph marks are configured in this section.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [color.marks]
    :end-before: [color.anchors]

.. confval:: color.marks.mark1
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(1.0, 0.0, 0.0, 1.0)``

    The primary mark color.

.. confval:: color.marks.mark2
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.0, 1.0, 0.0, 1.0)``

    The secondary mark color.

.. confval:: color.marks.mark3
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.0, 0.0, 1.0, 1.0)``

    The tertiary mark color.



.. _color.anchors:

color.anchors
-------------

:ref:`type-color` values for glyph anchors are configured in this section.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [color.anchors]
    :end-before: [engravingDefaults]

.. confval:: color.anchors
    :type: ``dict[str, tuple[int | float, int | float, int | float, int | float]]``
    :default: ``{<anchorName>: (r, g, b, a)}``

    A dictionary mapping anchor names to their corresponding RGBA color values.
    Each key is the name of an anchor (e.g., `cutOutNE`, `graceNoteSlashNW`),
    and each value is a 4-tuple representing red, green, blue, and alpha channel values.

    Individual anchor colors may also be referenced as distinct configuration values
    (e.g., :confval:`color.anchors.cutOutNE`) for documentation or override purposes.


.. confval:: color.anchors.cutOutNE
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(1.0, 1.0, 0.0, 1.0)``

    The default color for anchor `cutOutNE`, used in :confval:`color.anchors`. 

.. confval:: color.anchors.cutOutNW
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(1.0, 0.0, 1.0, 1.0)``

    The default color for anchor `cutOutNW`, used in :confval:`color.anchors`.

.. confval:: color.anchors.cutOutSE
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.0, 1.0, 1.0, 1.0)``

    The default color for anchor `cutOutSE`, used in :confval:`color.anchors`.

.. confval:: color.anchors.cutOutSW
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.5, 0.0, 0.0, 1.0)``

    The default color for anchor `cutOutSW`, used in :confval:`color.anchors`.

.. confval:: color.anchors.graceNoteSlashNE
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.0, 0.5, 0.0, 1.0)``

    The default color for anchor `graceNoteSlashNE`, used in :confval:`color.anchors`.

.. confval:: color.anchors.graceNoteSlashNW
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.0, 0.0, 0.5, 1.0)``

    The default color for anchor `graceNoteSlashNW`, used in :confval:`color.anchors`.

.. confval:: color.anchors.graceNoteSlashSE
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.5, 0.5, 0.0, 1.0)``

    The default color for anchor `graceNoteSlashSE`, used in :confval:`color.anchors`.

.. confval:: color.anchors.graceNoteSlashSW
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.5, 0.0, 0.5, 1.0)``

    The default color for anchor `graceNoteSlashSW`, used in :confval:`color.anchors`.

.. confval:: color.anchors.nominalWidth
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.0, 0.5, 0.5, 1.0)``

    The default color for anchor `nominalWidth`, used in :confval:`color.anchors`.

.. confval:: color.anchors.noteheadOrigin
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(1.0, 0.5, 0.0, 1.0)``

    The default color for anchor `noteheadOrigin`, used in :confval:`color.anchors`.

.. confval:: color.anchors.numeralBottom
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.5, 1.0, 0.0, 1.0)``

    The default color for anchor `numeralBottom`, used in :confval:`color.anchors`.

.. confval:: color.anchors.numeralTop
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.0, 0.5, 1.0, 1.0)``

    The default color for anchor `numeralTop`, used in :confval:`color.anchors`.

.. confval:: color.anchors.opticalCenter
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.5, 0.0, 1.0, 1.0)``

    The default color for anchor `opticalCenter`, used in :confval:`color.anchors`.

.. confval:: color.anchors.repeatOffset
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(1.0, 0.0, 0.5, 1.0)``

    The default color for anchor `repeatOffset`, used in :confval:`color.anchors`.

.. confval:: color.anchors.splitStemDownNE
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.0, 1.0, 0.5, 1.0)``

    The default color for anchor `splitStemDownNE`, used in :confval:`color.anchors`.

.. confval:: color.anchors.splitStemDownNW
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.5, 0.5, 0.5, 1.0)``

    The default color for anchor `splitStemDownNW`, used in :confval:`color.anchors`.

.. confval:: color.anchors.splitStemUpSE
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.75, 0.75, 0.75, 1.0)``

    The default color for anchor `splitStemUpSE`, used in :confval:`color.anchors`.

.. confval:: color.anchors.splitStemUpSW
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.25, 0.25, 0.25, 1.0)``

    The default color for anchor `splitStemUpSW`, used in :confval:`color.anchors`.

.. confval:: color.anchors.stemDownNW
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.8, 0.6, 0.4, 1.0)``

    The default color for anchor `stemDownNW`, used in :confval:`color.anchors`.

.. confval:: color.anchors.stemDownSW
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.6, 0.4, 0.2, 1.0)``

    The default color for anchor `stemDownSW`, used in :confval:`color.anchors`.

.. confval:: color.anchors.stemUpNW
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.2, 0.4, 0.6, 1.0)``

    The default color for anchor `stemUpNW`, used in :confval:`color.anchors`.

.. confval:: color.anchors.stemUpSE
    :type: ``tuple[int | float, int | float, int | float, int | float]``
    :default: ``(0.4, 0.6, 0.8, 1.0)``

    The default color for anchor `stemUpSE`, used in :confval:`color.anchors`.

.. _engravingDefaults:

engravingDefaults
-----------------

This section contains configuration for the :class:`~smufolib.objects.engravingDefaults.EngravingDefaults` class.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [engravingDefaults]

.. confval:: engravingDefaults.auto
    :type: ``bool``
    :default: ``true``

    Whether to automatically calculate engraving defaults automatically.
    

.. envvar:: SMUFOLIB_CFG

   If set, this environment variable overrides the default configuration file path.
   Use it to specify a custom configuration file location. The value should be an
   absolute or relative path to the `.cfg` configuration file.

For example:

.. code-block:: console

   export SMUFOLIB_CFG=/path/to/custom/smufolib.cfg