.. _metadata requests:

=================
Metadata Requests
=================

In SMufoLib, web requests and metadata file operations are handled in
the :mod:`~smufolib.request` module. For maximum reliability and access
to updated data, the module facilitates simultanous URL and file system
requests, while simplifying reading, parsing and writing of JSON data.

.. automodule:: smufolib.request

.. autoclass:: smufolib.request.Request(path=None, fallback=None, encoding=CONFIG["request"]["encoding"], warn=CONFIG["request"]["warn"])
    :members:

.. autofunction:: writeJson(filepath, source, encoding=CONFIG["request"]["encoding"])
