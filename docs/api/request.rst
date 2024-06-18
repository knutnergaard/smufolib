.. _metadata requests:

=================
Metadata Requests
=================

Requests for `SMuFL metadata
<https://w3c.github.io/smufl/latest/specification/smufl-metadata.html>`_
files are handled in the :mod:`~smufolib.request` module.
The :class:`~smufolib.request.Request` class allows simultanous URL and
filepath requests for maximum reliability and access to updated data.

.. automodule:: smufolib.request

.. autoclass:: smufolib.request.Request(path=None, fallback=None, encoding=CONFIG['request']['encoding'], warn=CONFIG['request']['warn'])

.. autoclass:: smufolib.request.URLWarning

.. autofunction:: writeJson
