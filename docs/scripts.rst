.. _calculate-engraving-defaults:

Calculate Engraving Defaults
============================

.. automodule:: bin.calculateEngravingDefaults

.. _calculate-engraving-defaults-cli:

Command Line Interface
----------------------

.. code-block:: console

    $ calculate-engraving-defaults <font> [-o <override>] [-r <remap>] [-e <attributes> ...] [-s] [-v]


.. program:: calculate-engraving-defaults

Positional Arguments
^^^^^^^^^^^^^^^^^^^^

.. option:: <font>

    Path to font file or font object.

Optional Arguments
^^^^^^^^^^^^^^^^^^

.. option:: -o <override>, --override <override>

    JSON string of attributes and values to manually override, in the format:

    .. code-block:: console

        '{"<attributeName>": <value>, ...}'

.. option:: -r <remap>, --remap <remap>

    JSON string of ruler and glyph remappings, in the format:

    .. code-block:: console

        '{"<attribute name>": {"ruler": "<functionName>", "glyph": "<glyphName>"}, ...}'

.. option:: -e <attributes>..., --exclude <attributes>...

    List of attributes to exclude from calculation.

.. option:: -s, --spaces

    Whether values for overrides are given in staff spaces instead of font units.

.. option:: -v, --verbose

    Make output verbose.

.. _calculate-engraving-defaults-python:

Python API
----------

.. code-block:: python

    >>> from bin.calculateEngravingDefaults import calculateEngravingDefaults
    >>> calculateEngravingDefaults("path/to/MyFont.ufo", override={"staffSpace": 0.25})

.. autofunction:: bin.calculateEngravingDefaults.calculateEngravingDefaults

.. _check-anchors:

Check Anchors
=============

.. automodule:: bin.checkAnchors

.. _check-anchors-cli:

Command Line Interface
----------------------

.. code-block:: console

    $ check-anchors <font> [<fontData>] [-m] [-c <color>] [-v]

.. program:: check-anchors

Positional Arguments
^^^^^^^^^^^^^^^^^^^^

.. option:: <font>

    Path to the font file to check.

Optional Arguments
^^^^^^^^^^^^^^^^^^

.. option:: -F <font-data>, --font-data <font-data>

    Path to the reference font data file. Defaults to :confval:`metadata.paths.font`,
    falling back to :confval:`metadata.fallbacks.font` if the former is unavailable.

.. option:: -m, --mark

    Mark discrepant glyphs in the font with the color specified by :option:`--color`.

.. option:: -c <r> <g> <b> <a>, --color <r> <g> <b> <a>

    RGBA color to use for marking glyphs. Only used when :option:`--mark` is set.
    Defaults to :confval:`color.marks.mark1`.

.. option:: -v, --verbose

    Make output verbose.

.. _check-anchors-python:

Python API
----------

.. code-block:: python

    >>> from bin.checkAnchors import checkAnchors
    >>> checkAnchors("path/to/MyFont.ufo", mark=True)


.. autofunction:: bin.checkAnchors.checkAnchors(font, fontData=Request(CONFIG["metadata.paths"]["font"], CONFIG["metadata.fallbacks"]["font"]), mark=False, color=None, verbose=False)

.. _clean-font:

Clean Font
==========

.. automodule:: bin.cleanFont

.. _clean-font-cli:

Command Line Interface
----------------------

.. code-block:: console

    $ clean-font <font> [-v]

.. program:: clean-font

Positional Arguments
^^^^^^^^^^^^^^^^^^^^

.. option:: <font>

    Path to the font file to clean.

.. option:: <include>...

    Specify items to delete. May be ``*`` (all), or one or more specified attribute or
    anchor names.

Optional Arguments
^^^^^^^^^^^^^^^^^^

.. option:: -e, --exclude <exclude>...

    Specify items to preserve if :option:`--include` is ``*`` (all). If omitted, all
    matching items will be deleted.

.. option:: -v, --verbose
    
    Make output verbose.

Use :option:`--include` and/or :option:`--exclude` to specify which items to delete or
preserve.

To prevent accidental data loss, you must explicitly define what to remove. A wildcard
(``--include *``) will remove all known SMuFL-related data from the font, unless
exclusions are specified.

See the list of valid attribute and anchor names in the :ref:`introduction <clean-font>`
above.

.. _clean-font-python:

Python API
----------

.. code-block:: python

    >>> from bin.cleanFont import cleanFont
    >>> cleanFont("path/to/MyFont.ufo", include=["anchors", "guidelines"])

.. autofunction:: bin.cleanFont.cleanFont

.. _generate-metadata:

Generate metadata
=================

.. automodule:: bin.generateMetadata


.. _generate-metadata-cli:

Command Line Interface
----------------------

.. code-block:: console

    $ generate-metadata <font> [<targetPath>] [-f <fontData>] [-v]

.. program:: generate-metadata

Positional Arguments
^^^^^^^^^^^^^^^^^^^^

.. option:: <font>

    Path to the font file to generate metadata for.

Optional Arguments
^^^^^^^^^^^^^^^^^^

.. option:: <target-path>

    Path to the target file to write the metadata to. Defaults to the font file's path
    with a ``.json`` extension.

.. option:: -f <font-data>, --font-data <font-data>

    Path to the reference font data file. Defaults to :confval:`metadata.paths.font`,
    falling back to :confval:`metadata.fallbacks.font` if the former is unavailable.

.. option:: -v, --verbose

    Make output verbose.

.. _generate-metadata-python:

Python API
----------

.. code-block:: python

    >>> from bin.generateMetadata import generateMetadata
    >>> generateMetadata("path/to/MyFont.ufo", targetPath="path/to/metadata.json")

.. autofunction:: bin.generateMetadata.generateMetadata(font, targetPath, fontData=Request(CONFIG["metadata.paths"]["font"], CONFIG["metadata.fallbacks"]["font"]), verbose=False)

.. _import-anchors:

Import Anchors
==============

.. automodule:: bin.importAnchors

.. _import-anchors-cli:

Command Line Interface
----------------------

.. code-block:: console

    $ import-anchors <font> [<fontData>] [-m] [-c <color>] [-C] [-v]

.. program:: import-anchors

Positional Arguments
^^^^^^^^^^^^^^^^^^^^

.. option:: <font>

    Path to the font file to import anchors into.

Optional Arguments
^^^^^^^^^^^^^^^^^^

.. option:: -F <font-data>, --font-data <font-data>

    Path to the reference font data file. Defaults to :confval:`metadata.paths.font`,
    falling back to :confval:`metadata.fallbacks.font` if the former is unavailable.

.. option:: -m, --mark

    Mark imported anchors in the font with the color specified by :option:`--color`.

.. option:: -c <r> <g> <b> <a>, --color <r> <g> <b> <a>

    RGBA color to use for marking anchors. Only used when :option:`--mark` is set.
    Defaults to :confval:`color.anchors`.

.. option:: -x, --clear

    Clear existing anchors before importing new ones.

.. option:: -v, --verbose

    Make output verbose.

.. _import-anchors-python:

Python API
----------

.. code-block:: python

    >>> from bin.importAnchors import importAnchors
    >>> importAnchors("path/to/MyFont.ufo")

.. autofunction:: bin.importAnchors.importAnchors(font, fontData=Request(CONFIG["metadata.paths"]["font"], CONFIG["metadata.fallbacks"]["font"]), mark=True, colors=CONFIG["color.anchors"], clear=False, verbose=False)

.. _import-id:

Import ID
=========

.. automodule:: bin.importID

.. _import-id-cli:

Command Line Interface
----------------------

.. code-block:: console

    $ import-id <font> [<attributes>] [<classesData>] [<glyphnamesData>] [<fontData>] [-o] [-v]

.. program:: import-id

Positional Arguments
^^^^^^^^^^^^^^^^^^^^

.. option:: <font>

    Path to the font file to import ID data into.

Optional Arguments
^^^^^^^^^^^^^^^^^^

.. option:: -a <attributes>..., --attributes <attributes>...

    ID attributes to be set. Value can be either ``*`` (all),
        ``name``, ``classes``, ``description`` or :class:`tuple` of several. Defaults to
        ``*``.

.. option:: -C <classes-data>, --classes-data <classes-data>

    Path to the classes data file. Defaults to :confval:`metadata.paths.classes`,
    falling back to :confval:`metadata.fallbacks.classes` if the former is unavailable.

.. option:: -G <glyphnames-data>, --glyphnames-data <glyphnames-data>

    Path to the glyph names data file. Defaults to :confval:`metadata.paths.glyphnames`,
    falling back to :confval:`metadata.fallbacks.glyphnames` if the former is unavailable.

.. option:: -F <font-data>, --font-data <font-data>

    Path to the font data file. Defaults to :confval:`metadata.paths.font`,
    falling back to :confval:`metadata.fallbacks.font` if the former is unavailable.

.. option:: -i, --include-optionals
    
    Include optional glyphs in the import.

.. option:: -o, --overwrite

    Overwrite existing attributes with the same name. If not set, existing attributes
    will not be modified.

.. option:: -v, --verbose

    Make output verbose.

Optional glyphs can be included with the :option:`--include-optionals` flag. When this option is used, stylistic alternates and ligatures must be named relative to their base glyph (see :ref:`this note <about-glyph-naming>` for more details).

By default, existing attribute values are preserved. To overwrite them, pass the
:option:`--overwrite` flag. Glyphs are also skipped if they are not part of
the SMuFL range or if lookup fails (e.g., due to missing codepoints or unencoded glyphs
in the metadata). 

.. _import-id-python:

Python API
----------

.. code-block:: python

    >>> from bin.importID import importID
    >>> importID("path/to/MyFont.ufo", attributes=("classes", "description"))

.. autofunction:: bin.importID.importID(font, attributes, classesData=Request(CONFIG["metadata.paths"]["classes"], CONFIG["metadata.fallbacks"]["classes"]), glyphnamesData=Request(CONFIG["metadata.paths"]["glyphnames"], CONFIG["metadata.fallbacks"]["glyphnames"]), fontData=Request(CONFIG["metadata.paths"]["font"], CONFIG["metadata.fallbacks"]["font"]), includeOptionals=False, overwrite=False, verbose=False)

