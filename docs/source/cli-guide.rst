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

Run a Surround project assembler and task.

Without any arguments, all tasks will be listed.

Assemblers are defined in the ``__main__.py`` file of the current project. The default assembler that comes
with every project is called ``baseline``.

Tasks are defined in the ``dodo.py`` file of the current project. Each project comes with a set of default tasks listed below.

**Containerised Tasks**:

- ``build`` - Build a Docker image for your Surround project.
- ``dev`` - Run the specified assembler in a Docker container with the current source code (via drive mount, no build neccessary).
- ``prod`` - Build the Docker image and run the specified assembler inside a container (no drive mounting).
- ``batch`` - Run the specified assembler in a Docker container (mounting ``input`` and ``output`` folders) set to batch mode.
- ``train`` - Run the specified assembler in a Docker container (mounting ``input`` and ``output`` folders) set to train mode.
- ``web`` - Serve the specified assembler via HTTP endpoints inside a Docker container.
- ``remove`` - Remove the Docker image built for this project (if any).
- ``jupyter`` - Run a jupyter notebook server in a Docker container (mounting the whole project).

**Local Tasks**:

- ``batchLocal`` - Run the specified assembler locally set to batch-predict mode.
- ``trainLocal`` - Run the specified assembler locally set to train mode.
- ``webLocal`` - Serve the specified assembler via HTTP endpoints locally. 

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

data
^^^^

.. argparse::
    :module: surround.cli
    :func: execute_cli
    :prog: surround
    :path: data

split
^^^^^

Tool to randomly split data into test, train, and validation sets.

Supports splitting:

- Directory of files
- CSV files
- Text files (just ensure you use the ``--no-header`` flag)

Example - Split a directory of images into train/test/validate::

    $ surround split -d images -e png

Example - Reset a split directory::

    $ surround spit --reset images

Example - Splitting and resetting a CSV file::

    $ surround split -t test.csv
    $ surround split --reset .

.. argparse::
    :module: surround.cli
    :func: execute_cli
    :prog: surround
    :path: split