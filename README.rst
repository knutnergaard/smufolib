SMufoLib: Where SMuFL meets UFO
===============================

SMufoLib is a small Python library designed to aid in font development
and scripting specific to the `Standard Music Font Layout
<https://w3c.github.io/smufl/latest/>`_ (SMuFL). As an extension of the
`FontParts <https://fontparts.robotools.dev/en/stable/index.html>`_
API, SMufoLib relies on the platform and application independent
`Unified Font Object <https://unifiedfontobject.org>`_ (UFO) format and
the command line, rather than any particular font editor.

Documentation
-------------

SMufoLib’s documentation is available at `smufolib.readthedocs.io
<https://smufolib.readthedocs.io/en/latest/index.html>`_.

Installation
------------

SMufoLib requires `Python <http://www.python.org/download/>`__ 3.10 or
later. It is listed in the Python Package Index (PyPI) and can be
installed with `pip <https://pip.pypa.io/>`__:

.. code:: bash

   $ python -m pip install smufolib

Scripts
-------

SMufoLib comes bundled with several useful functions and scripts for
building SMuFL metadata files, calculating engraving defaults from
glyphs, importing identification attributes and more.

Scripts may be run either via the Python interpreter or
directly from the console, passing in any arguments in the familiar
manner to each platform.

As an example, check for missing or superflous SMuFL anchors by running
the checkAnchors script directly from console:

.. code:: zsh

   $ check-anchors --mark

Or import it as a module in Python:

.. code:: Py3

   from bin import checkAnchors

   checkAnchors(mark=True)
