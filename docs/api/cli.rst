.. _command-line-interface:

=============
CLI Framework
=============

To simplify the creation of command-line options and streamline script
interfaces, :func:`cli.commonParser` provides a set of predefined argument definitions
for the standard library :mod:`argparse` module. These may be combined
with any script specific definitions by
passing :func:`~cli.commonParser` as a `parent` to :class:`argparse.ArgumentParser` (see
:ref:`combining-parsers` in the User Guide).

.. _Available Options:

Available Options
-----------------

.. csv-table::
    :file: ../options.csv
    :header-rows: 1

.. note:: Short flags for options may be redefined in the
    :ref:`[cli.shortFlags]` section of :ref:`smufolib.cfg`.


.. automodule:: smufolib.cli
    :members:
