.. module:: bin
   :noindex:

Installation
============

SMufoLib requires `Python <http://www.python.org/download/>`__ 3.10 or
later. It is listed in the `Python Package Index
<https://pypi.org/project/smufolib>`_ (PyPI) and can be installed with
`pip <https://pip.pypa.io/>`__:

.. code:: zsh

    $ python -m pip install smufolib

Running Scripts
===============

SMufoLib comes bundled with several useful functions and scripts for
building SMuFL metadata files, calculating engraving defaults from
glyphs, importing identification attributes and more.

Scripts may be run either via the Python interpreter or
directly from the console, passing in any arguments in the familiar
manner to each platform.

As an example, check for missing or superflous SMuFL anchors by running
the :mod:`~bin.checkAnchors` script directly from console:

.. code:: zsh

   $ check-anchors --mark

Or import it as a module in Python:

.. code:: Py3

   from bin import checkAnchors

   checkAnchors.main(mark=True)
