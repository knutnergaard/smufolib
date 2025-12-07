.. _cli-framework:

=============
CLI Framework
=============

To simplify the creation of command-line options and streamline script
interfaces, the :mod:`.cli` module provides a set of predefined argument definitions as
well as accompanying tools utilizing the standard library :mod:`argparse` module.

.. _Available Options:

Available Options
-----------------

.. csv-table::
    :file: ../options.csv
    :header-rows: 1

.. note::

    Short flags for options may be redefined in the :ref:`cli.shortFlags`
    configuration section.

.. automodule:: smufolib.cli
    :members:

.. class:: argparse.HelpFormatter

   Formatter for generating usage messages and argument help strings.
