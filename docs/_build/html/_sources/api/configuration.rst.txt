.. module:: smufolib
    :noindex:

=============
Configuration
=============

User defined default settings for SMufoLib are set in the configuration
file :ref:`smufolib.cfg` and parsed by the :mod:`~smufolib.config`
module. Detailed information on how SMufoLib handles configuration
is provided in the following sections.

.. automodule:: smufolib.config
    :members:

.. _smufolib.cfg:

smufolib.cfg
============

The SMufoLib configuration file `smufolib.cfg` contains default
settings for SMufoLib. It contains three main sections, with
sub-sections denoted by a preceding dot, and settings for warnings, URL
and file paths and colors.

.. _[request]:

[request]
---------

This section contains configuration for
the :class:`smufolib.request.Request` class.

.. code-block:: cfg

    [request]
    encoding = utf-8
    warn = true

.. _[metadata.paths]:

[metadata.paths]
----------------

Primary metadata paths are configured in this section.


.. code-block:: cfg

    [metadata.paths]
    directory = https://raw.githubusercontent.com/w3c/smufl/gh-pages/metadata/
    classes = ${directory}classes.json
    glyphnames = ${directory}glyphnames.json
    ranges = ${directory}ranges.json
    referenceFont = https://raw.githubusercontent.com/steinbergmedia/
        bravura/master/redist/bravura_metadata.json

.. _[metadata.fallbacks]:

[metadata.fallbacks]
--------------------

Metadata fallback paths are configured in this section.

.. code-block:: cfg

    [metadata.fallbacks]
    directory = ./smufolib/metadata/
    classes = ${directory}classes.json
    glyphnames = ${directory}glyphnames.json
    ranges = ${directory}ranges.json
    referenceFont = ${directory}bravura_metadata.json

.. _[cli.shortFlags]:

[cli.shortFlags]
----------------

Short flags for :ref:`Command Line Interface` options to be used
with :func:`~smufolib.cli.commonParser` are configured in this section.

.. code-block:: cfg

    [cli.shortFlags]
    classData = -C
    clear = -x
    color = -c
    exclude = -e
    font = -f
    fontData = -F
    glyphnameData = -G
    include = -i
    mark = -m
    overwrite = -o
    rangeData = -r
    sourcePath = -S
    spaces = -s
    targetPath = -T

.. _[color.marks]:

[color.marks]
-------------

:ref:`type-color` values for glyph marks are configured in this section.

.. code-block:: cfg

    [color.marks]
    mark1 =
    mark2 =
    mark3 =

.. _[color.anchors]:

[color.anchors]
---------------

:ref:`type-color` values for glyph anchors are configured in this section.

.. code-block:: cfg

    [color.anchors]
    cutOutNE =
    cutOutNW =
    cutOutSE =
    cutOutSW =
    graceNoteSlashNE =
    graceNoteSlashNW =
    graceNoteSlashSE =
    graceNoteSlashSW =
    nominalWidth =
    noteheadOrigin =
    numeralBottom =
    numeralTop =
    opticalCenter =
    repeatOffset =
    splitStemDownNE =
    splitStemDownNW =
    splitStemUpSE =
    splitStemUpSW =
    stemDownNW =
    stemDownSW =
    stemUpNW =
    stemUpSE =
