:mod:`.converters`
------------------

.. automodule:: smufolib.utils.converters
    :members:

:mod:`.error`
-------------

.. automodule:: smufolib.utils.error
    :members:
    :exclude-members: ERROR_TEMPLATES

    .. py:data:: ERROR_TEMPLATES
        :type: dict[str, str]
        
        Dictionary of error message templates.

        .. csv-table::
            :file: error_templates.csv
            :header-rows: 1

:mod:`.normalizers`
-------------------

.. automodule:: smufolib.utils.normalizers
    :members:

:mod:`.pointUtils`
------------------

.. automodule:: smufolib.utils.pointUtils
    :members:
    :exclude-members: contourIndex, position, type, x, y

:mod:`.rulers`
--------------

.. automodule:: smufolib.utils.rulers
    :members:
    :exclude-members: ENGRAVING_DEFAULTS_MAPPING

    .. py:data:: ENGRAVING_DEFAULTS_MAPPING
        :type: dict[str, dict[str, str]]
        
        Default mapping of rulers and glyphs to :class:`.EngravingDefaults` attributes.

        .. csv-table::
            :file: engraving_defaults_mapping.csv
            :header-rows: 1

:mod:`.scriptUtils`
-------------------

.. automodule:: smufolib.utils.scriptUtils
    :members:
    
:mod:`.stdUtils`
----------------

.. automodule:: smufolib.utils.stdUtils
    :members:


.. toctree::
   :hidden:
   :glob:

   _autosummary/smufolib.utils.rulers.*