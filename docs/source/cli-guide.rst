Command-line Interface
======================

The following is a list of the sub-commands contained in Surround's CLI tool.

surround
^^^^^^^^

.. argparse::
    :module: surround.cli
    :func: execute_cli
    :prog: surround
    :nosubcommands:

init
^^^^

Initialize a new Surround project.

.. argparse::
    :module: surround.cli
    :func: execute_cli
    :prog: surround
    :path: init

run
^^^

Run a Surround project task, witout an argument all tasks will be shown.

Tasks are defined in the ``dodo.py`` file of the current project.
The default tasks that come with every project are:

- ``build`` - Build a Docker image for your Surround project.
- ``dev`` - Run the Docker image with the current source code (via drive mount).
- ``prod`` - Build and run the Docker image (no drive mounting).

.. argparse::
    :module: surround.cli
    :func: execute_cli
    :prog: surround
    :path: run

lint
^^^^

Run the Surround Linter on the current project.

For more information on what this does, see :ref:`linter`.

.. argparse::
    :module: surround.cli
    :func: execute_cli
    :prog: surround
    :path: lint