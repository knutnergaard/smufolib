.. _configuration:

=============
Configuration
=============

User defined default settings for SMufoLib are set in the configuration file :ref:`smufolib.cfg` and parsed by the :mod:`~smufolib.config` module. Detailed information on how SMufoLib handles configuration is provided in the following sections.

.. automodule:: smufolib.config
    :members:

.. _smufolib.cfg:

smufolib.cfg
============

The SMufoLib configuration file `smufolib.cfg` contains default settings for SMufoLib.
It contains three main sections, with sub-sections denoted by a preceding dot, and
settings for warnings, URL and file paths and colors.

.. _[request]:

[request]
---------

This section contains configuration for
the :class:`~smufolib.request.Request` class.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [request]
    :end-before: [metadata.paths]

.. _[metadata.paths]:

[metadata.paths]
----------------

Primary metadata paths are configured in this section.


.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [metadata.paths]
    :end-before: [metadata.fallbacks]

.. _[metadata.fallbacks]:

[metadata.fallbacks]
--------------------

Metadata fallback paths are configured in this section.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [metadata.fallbacks]
    :end-before: [cli.shortFlags]

.. _[cli.shortFlags]:

[cli.shortFlags]
----------------

Short flags for :ref:`command-line-interface` options to be used with :func:`~smufolib.cli.commonParser` are configured in this section.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [cli.shortFlags]
    :end-before: [color.marks]

.. _[color.marks]:

[color.marks]
-------------

:ref:`type-color` values for glyph marks are configured in this section.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [color.marks]
    :end-before: [color.anchors]

.. _[color.anchors]:

[color.anchors]
---------------

:ref:`type-color` values for glyph anchors are configured in this section.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [color.anchors]
    :end-before: [engravingDefaults]


.. _[engravingDefaults]:

[engravingDefaults]
-------------------

This section contains configuration for the :class:`~smufolib.objects.engravingDefaults.EngravingDefaults` class.

.. literalinclude:: ../../smufolib/smufolib.cfg
    :language: cfg
    :start-at: [engravingDefaults]

.. envvar:: SMUFOLIB_CFG

   If set, this environment variable overrides the default configuration file path.
   Use it to specify a custom configuration file location. The value should be an
   absolute or relative path to the `.cfg` configuration file.

For example:

.. code-block:: zsh

   export SMUFOLIB_CFG=/path/to/custom/smufolib.cfg