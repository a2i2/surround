.. _getting-started:

Getting Started
===============

Installation
************

Prerequisites
^^^^^^^^^^^^^

- Python 3+ (Tested on 3.6.5)
- Docker
- Supports MacOS, Linux, and Windows

Install via Pip
^^^^^^^^^^^^^^^
Run the following command to install the latest version of Surround::
    
    $ pip3 install surround

.. note:: If this doesn't work make sure you have pip installed. See `here <https://pip.pypa.io/en/stable/installing/>`_ on how to install it.

Now the Surround library and command-line tool should be installed! To make sure run the following command to test::

    $ surround

If it works then you are ready for the :ref:`project-setup` stage.

Install via Source
^^^^^^^^^^^^^^^^^^
If for some reason the above isn't working for you, or you plan to extend Surround, then you can install via the source.
So first clone the repository like so::

    $ git clone https://github.com/a2i2/surround.git
    $ cd surround

Then install the package using the ``setup.py`` script::

    $ python3 setup.py install

.. note:: This step requires the module ``setuptools`` to be installed. See `here <https://pypi.org/project/setuptools/>`_ on how to install it.

Then test the installation by running the tests and trying the surround CLI::

    $ python3 setup.py test

    $ surround

.. _project-setup:

Project Setup
*************

Before we can create our first pipeline, we need to generate an empty Surround project. 
Use the following command to generate a new project::

    $ surround init -p testproject -d "Our first pipeline"

This will create a new folder called ``testproject`` with the following file structure::

    testproject
    ├── Dockerfile
    ├── README.md
    ├── data
    ├── testproject
    │   ├── __main__.py
    │   ├── config.yaml
    │   ├── wrapper.py
    │   └── stages.py
    ├── docs
    ├── dodo.py
    ├── models
    ├── notebooks
    ├── output
    ├── requirements.txt
    ├── scripts
    ├── spikes
    └── tests

The generated project comes with an example pipeline that can be ran straight away using the command::

    $ cd testproject
    $ python3 -m testproject

Which should output the following::

    INFO:surround.surround:Stage ValidateData took 0:00:00.000007 secs
    INFO:surround.surround:Surround took 0:00:00.000802 secs
    INFO:root:{'output': 'TODO: Validate input data assumptions here'}

Now you are ready for :ref:`create-first-pipeline`. 

.. seealso:: Not sure what a pipeline is? Checkout our :ref:`about` section first!

.. _create-first-pipeline:

Creating your first pipeline
****************************

For our first Surround pipeline, we are going to do some very basic data transformation and convert the input string
from lower case to upper case. This pipeline is going to consist of two stages, ``ValidateData`` and ``MakeUpperCase``.

Open the script ``stages.py`` and you should see the following code already generated::

    from surround import Stage, SurroundData

    class TestprojectData(SurroundData):
        output_data = None

        def __init__(self, input_data):
            self.input_data = input_data
            self.errors = []

    class ValidateData(Stage):
        def operate(self, surround_data, config):
            surround_data.output_data = "TODO: Validate input data assumptions here"

As you can see we are already given the ``ValidateData`` stage, we just need to edit the ``operate`` method to
check if the input data is the correct data type (:class:`str`)::

    def operate(self, surround_data, config):
        if not isinstance(surround_data.input_data, str):
            # Create an error sine the data is wrong, this will stop the pipeline
            surround_data.errors.append('Input is not a string!')

Now we need to create the ``MakeUpperCase`` stage which will perform the data transformation::

    class MakeUpperCase(Stage):
        def operate(self, surround_data, config):
            # Convert the input into upper case
            surround_data.output_data = surround_data.input_data.upper()

Now we just need to add this new stage into the actual pipeline, so first open the ``wrapper.py`` script, you should see the following::

    import json
    from surround import Surround, Wrapper, AllowedTypes
    from stages import ValidateData, TestprojectData

    class PipelineWrapper(Wrapper):
        def __init__(self):
            surround = Surround([ValidateData()], __name__)
            super().__init__(surround)

        def run(self, input_data):
            text = json.loads(input_data)["data"]
            data = TestprojectData(text)
            self.surround.process(data)
            return {"output": data.output_data}

Edit this script to first import the new stage like so::

    from stages import ValidateData, MakeUpperCase, TestprojectData

Then append an instance of the stage in the :class:`list` being passed to the ``Surround`` constructor::

    def __init__(self):
        surround = Surround([ValidateData(), MakeUpperCase()], __name__)
        super().__init__(surround)

That's it for the pipeline! To test the pipeline with default input (``"hello"`` string) just run the following command::

    $ python3 -m testproject

The output should be the following::

    INFO:surround.surround:Stage ValidateData took 0:00:00.000004 secs
    INFO:surround.surround:Stage MakeUpperCase took 0:00:00.000029 secs
    INFO:surround.surround:Surround took 0:00:00.001610 secs
    INFO:root:{'output': 'HELLO'}

.. note:: To modify what happens when ``python3 -m testproject`` is executed, edit the ``__main__.py`` script.

Running your first pipeline in a container
******************************************

First you must build an image for your container. To do this just run the following command::

    $ surround run build

Then to run the container in dev mode just use the following command::

    $ surround run dev

This will run the container linking the folder ``testproject/testproject`` with the working directory in the
container. So during development when you make small changes, there is no need to build the image again.

Then when you are ready for production testing you use the following command::

    $ surround run prod

Which will first build the image and then run the container without any linking to the host machine.

.. note:: Both methods of running will use the equivalent command to ``python3 -m testproject`` inside the container.

Serving your first pipeline via Web Endpoint
********************************************

Using Surround we can also host a web-server which can receive data, pass it through our pipeline
and return the result. All via HTTP endpoints, making your pipeline accessible by any application!

Before we can run the web-server, we need to install a dependency called ``tornado``, do this like so::

    $ pip3 install tornado==6.0.1

To start the web-server run the following command::

    $ surround run --web

Which should output the following::

    testproject is running on http://localhost:8888
    Available endpoints:
    * GET  /                 # Health check
    * POST /predict          # Send data to the Surround pipeline

Now you can send data to your pipeline via HTTP POST to the ``/predict`` endpoint like so::

    $ curl -d "{ \"data\": \"mAkE aLL upper CASE\" }" http://localhost:8888/predict

Which should output the following if succssful::

    {"output": "MAKE ALL UPPER CASE"}