Installation
============

There is more than one way to install SMufoLib, the most common being
via pip from `PyPi <https://pypi.org/project/smufolib>`_.

pip install
-----------

To install SMufoLib with pip, enter the following code in your favorite terminal:

.. code-block:: console

    $ python -m pip install smufolib

Running Scripts
===============

SMufoLib scripts may be run either via the Python interpreter or
directly from the console, passing in any arguments in the familiar
manner to each platform.

As an example, check for missing or superflous SMuFL anchors
with *checkAnchors* directly from console as follows:

.. code:: zsh

   $ checkAnchors --mark

Or with regular python:

.. code:: Py3

   from bin import checkAnchors

   checkAnchors(mark=True)
