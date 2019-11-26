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

.. _project-setup:

Project Setup
*************

Before we can create our first pipeline, we need to generate an empty Surround project. 
Use the following command to generate a new project::

    $ surround init -p test_project -d "Our first pipeline"

When it asks the following, respond with ``n`` (we'll cover this in later sections)::
    
    Does it require a web runner? (y/n) n

This will create a new folder called ``test_project`` with the following file structure::

    test_project
    ├── test_project/
    │   ├── stages
    │   │   ├── __init__.py
    │   │   ├── input_validator.py
    │   │   ├── baseline.py
    │   │   └── assembler_state.py
    │   ├── __main__.py
    │   ├── __init__.py    
    │   ├── config.yaml
    │   └── file_system_runner.py
    ├── input/
    ├── docs/
    ├── models/
    ├── notebooks/
    ├── output/
    ├── scripts/
    ├── spikes/
    ├── tests/
    ├── __main__.py
    ├── __init__.py    
    ├── dodo.py
    ├── Dockerfile
    ├── requirements.txt
    └── README.md

The generated project comes with an example pipeline that can be ran straight away using the command::

    $ cd test_project
    $ surround run batchLocal

Which should output the following::

    INFO:surround.assembler:Starting 'baseline'
    INFO:surround.assembler:Validator InputValidator took 0:00:00 secs
    INFO:surround.assembler:Estimator Baseline took 0:00:00 secs

Now you are ready for :ref:`create-first-pipeline`. 

.. seealso:: Not sure what a pipeline is? Checkout our :ref:`about` section first!

.. _create-first-pipeline:

Creating your first pipeline
****************************

For our first Surround pipeline, we are going to do some very basic data transformation and convert the input string
from lower case to upper case. This pipeline is going to consist of two stages, ``InputValidator`` and ``MakeUpperCase``.

Open the script ``stages/validator.py`` and you should see the following code already generated::

    from surround import Validator

    class InputValidator(Validator):
        def validate(self, state, config):
            if not state.input_data:
                raise ValueError("'input_data' is None")

As you can see we are already given the ``InputValidator`` stage, we just need to edit the ``operate`` method to
check if the input data is the correct data type (:class:`str`)::

    def validate(self, state, config):
        if not isinstance(state.input_data, str):
            # Raise an exception, this will stop the pipeline
            raise ValueError('Input is not a string!')

Now we need to create our ``MakeUpperCase`` stage, so head to ``stages/baseline.py``, you should see::

    from surround import Estimator

    class Baseline(Estimator):
        def estimate(self, state, config):
            state.output_data = state.input_data

        def fit(self, state, config):
            LOGGER.info("TODO: Train your model here")

Make the following changes::

    class MakeUpperCase(Estimator):
        def estimate(self, state, config):
            # Convert the input into upper case
            state.output_data = state.input_data.upper()

            # Print the output to the terminal (to check its working)
            LOGGER.info("Output: %s" % state.output_data)
        
        def fit(self, state, config):
            # Leave the fit method the same 
            # We aren't doing any training in this guide
            LOGGER.info("TODO: Train your model here")

Since we renamed the estimator, we need to reflect that change when we create the ``Assembler``.

First head to the ``stages/__init__.py`` file and rename ``Baseline`` to ``MakeUpperCase``::

    from .baseline import MakeUpperCase
    from .input_validator import InputValidator
    from .assembler_state import AssemblerState

Then in ``__main__.py`` where the estimator is imported make sure it looks like so::

    from stages import MakeUpperCase, InputValidator

And where the assembler is created, make sure it looks like so::

    assemblies = [
        Assembler("baseline")
            .set_validator(InputValidator())
            .set_estimator(MakeUpperCase())
    ]

That's it for the pipeline! 
To test the pipeline with default input (``"TODO Load raw data here"`` string) just run the following command::

    $ surround run batchLocal

The output should be the following::

    INFO:surround.assembler:Starting 'baseline'
    INFO:stages.baseline:Output: TODO: LOAD RAW DATA HERE
    INFO:surround.assembler:Estimator MakeUpperCase took 0:00:00 secs

To change what input is fed through the pipeline, modify ``batch_runner.py`` and change what is given to ``data.input_data``::

    import logging
    from surround import Runner
    from stages import AssemblyState

    logging.basicConfig(level=logging.INFO)

    class FileSystemRunner(Runner):
        def load_data(self, mode, config):
            state = AssemblyState()

            # Load data to be processed
            raw_data = "This daTa wiLL end UP captializED"

            # Setup input data
            state.input_data = raw_data

            return state

.. note:: To test training mode (``fit`` will be called instead in the estimator), run the following command: 
            ``$ surround run trainLocal``

Running your first pipeline in a container
******************************************

First you must build an image for your container. To do this just run the following command::

    $ surround run build

Then to run the container in dev mode just use the following command::

    $ surround run dev

This will run the container linking the folder ``testproject/testproject`` with the working directory in the
container. So during development when you make small changes, there is no need to build the image, just run
this command again.

Then when you are ready for production you can use the following command::

    $ surround run prod

Which will first build the image and then run the container without any linking to the host machine.
The image created in the build can also then be committed to a Docker Hub repository and shared.

.. note:: Both ``dev`` and ``prod`` will use the default mode of the project, which in non-web projects
        is ``RunMode.BATCH_PREDICT``, otherwise it's ``RunMode.WEB``.

The following commands will force which mode to use::

    $ surround run batch
    $ surround run train

.. note:: To see a list of available tasks, just run the command ``$ surround run``

Serving your first pipeline via Web Endpoint
********************************************

When generating a project, you get asked::
    
    Does it require a web runner? (y/n)
    
If we say yes to this then Surround will generate a generic ``batch_runner.py`` but it will also
generate a new script called ``web_runner.py``. 

This script contains a new ``Runner`` which will use `Tornado <https://www.tornadoweb.org/en/stable/>`_
to host a web server which will allow your pipeline to be accessible via HTTP request. By default the 
``WebRunner`` will host two endpoints:

- ``/info`` - access via GET request, will return ``{'version': '0.0.1'}``
- ``/estimate`` - access via POST request, body must have a JSON document containing input data::

    {
        "message": "this text will be processed" 
    }

So lets create a new pipeline that does the same data processing as the one in :ref:`create-first-pipeline` but
we will send strings via web endpoint and get the results in the response of the request.

First generate a new project, this time saying yes to the require web prompt, and make all the changes we did in
:ref:`create-first-pipeline` and test it is still working locally.

Next we are going to build an image for our pipeline using the command::

    $ surround run build

Then we are going to run our default server using the command::

    $ surround run web

You should get output like so::

    INFO:root:Server started at http://localhost:8080

.. note:: If you would like to run it on the host machine instead of in a container, you must install Tornado using
        this command: ``$ pip3 install tornado==6.0.2``

Now hopefully if you load ``http://localhost:8080/info`` in your preferred browser, you should see the following::

    {"version": "0.0.1"}

.. note:: If you are running this on Windows and don't see the above, try using ``http://192.168.99.100:8080/info`` instead.

Next we are going to test the ``/estimate`` endpoint by using the following command in another terminal:

On Linux/MacOS::

    $ curl -d "{ \"message\": \"test phrase\" }" http://localhost:8080/estimate

On Windows (in Powershell)::

    $ Invoke-WebRequest http://192.168.99.100:8080/estimate -Method POST -Body "{ ""message"": ""test phrase"" }"

You should see the following output in the terminal running the pipeline::

    INFO:surround.assembler:Starting 'baseline'
    INFO:surround.assembler:Estimator MakeUpperCase took 0:00:00 secs
    INFO:root:Message: TEST PHRASE
    INFO:tornado.access:200 POST /estimate (::1) 1.95ms

So our data is successfully being processed! But what if we need the result?

Head to the script ``web_runner.py`` and append the following to the ``post`` method of ``EstimateHandler``::

    # Return the result of the processing
    self.write({"output": self.data.output_data})

Restart the web server, use the same command as before and you should see the following output:

On Linux/MacOS::

    % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                    Dload  Upload   Total   Spent    Left  Speed
    100    53  100    25  100    28    806    903 --:--:-- --:--:-- --:--:--  1709
    {"output": "TEST PHRASE"}

On Windows (in Powershell)::

    StatusCode        : 200
    StatusDescription : OK
    Content           : {"output": "TEST PHRASE"}
    RawContent        : HTTP/1.1 200 OK
                        Content-Length: 25
                        Content-Type: application/json; charset=UTF-8
                        Date: Mon, 17 Jun 2019 06:43:54 GMT
                        Server: TornadoServer/6.0.2

                        {"output": "TEST PHRASE"}
    Forms             : {}
    Headers           : {[Content-Length, 25], [Content-Type, application/json; charset=UTF-8], [Date, Mon, 17 Jun 2019 06:43:54 GMT], [Server, TornadoServer/6.0.2]}
    Images            : {}
    InputFields       : {}
    Links             : {}
    ParsedHtml        : mshtml.HTMLDocumentClass
    RawContentLength  : 25

Thats it, you are now serving a Surround pipeline! Now you could potentially use this pipeline in virtually any
application.

.. note:: Since this project was generated with a web runner, the default mode is ``web``, to run the pipeline
        using the ``FileSystemRunner`` instead, use the command ``$ surround run batch`` or ``$ surround run train``.

Serving your first pipeline via Google Cloud Compute
********************************************

**Introduction**

Google cloud compute deployment feature will let users run their experiments in the cloud and stores all experiment results in the cloud bucket (a data storage in the cloud). This feature allows user to deploy a docker image to the cloud using command line interface, then users can use the GPU in the cloud to train and predict.

This following steps will outline the steps to prepare your MacOS environment to use the google cloud compute deployment feature in Surround.

**Google Cloud Setup**

**Create account**

This feature requires the use of a Google Cloud Platform account. If you do not already have an account, follow the steps under Getting Started at cloud.google.com to create an account for free.

**Create project**

Create a new project from the `Google Cloud Console <https://console.cloud.google.com/>`_. Alternatively, you can use the project that was automatically generated when you created your account.

Navigate to the `APIs and Services Dashboard <https://console.cloud.google.com/apis/>`_ and click the button at the top of the screen to enable APIs. Search for and enable the following APIs:

1. AI Platform Training & Prediction API
2. Compute Engine API
3. Container Registry API

**Create service account**

To connect your Surround project to your Google Cloud project, you will need to provide a credentials file. Follow the steps below to create the file.

1. From the Google Cloud Console, navigate to the `Google Cloud Credentials <https://console.cloud.google.com/apis/credentials>`_ page.
2. Click on Create credentials and select the option to create a service account key.
3. Select “Compute Engine default service account” as your service account and select JSON as the key type.
4. Locate the file in your downloads and move it to a suitable location.

Open terminal and set an environment variable ``GOOGLE_APPLICATION_CREDENTIALS`` to the filepath of the credentials file. This will tell Surround where to look for the file. Use the following command to set the environment variable for the current terminal session, replacing ``<path_to_credentials_json>`` with the file path of the credentials file::

    $ export GOOGLE_APPLICATION_CREDENTIALS=<path_to_credentials_json>

If you want to permanently set this environment variable so that it is saved between terminal sessions, complete the following steps for MacOS:

1.Change directory into your home directory::
    
    $ cd ~

2. Edit ``.bash_profile`` in terminal (or edit using your preferred text editor) to include the file path::
    
    $ nano .bash_profile
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/json/credentials.json

3. Restart terminal and check that the environment variable is set::

    $ echo $GOOGLE_APPLICATION_CREDENTIALS

**Create bucket for experiment data**

To view your experiment data with Surround’s experiment explorer, you will have to create a bucket to store the experiment data. From the Google Cloud Console Dashboard, navigate to Storage (under Resources). 

Click the button near the top of the screen to create a new bucket. Follow the steps to create the bucket and remember the name for later steps.

**Local Environment Setup**

**Install Python and Pip**

Surround is installed using pip and the projects are written in python.
Follow the steps to install python `here <https://docs.python.org/3/using/mac.html>`_.
Follow the steps to install pip `here <https://pip.pypa.io/en/stable/installing/>`_.

**Install Docker**

Docker is used to create images of your Surround project. The image of your project is submitted as a cloud compute job.

Follow the steps to install Docker Desktop `here <https://docs.docker.com/docker-for-mac/install/>`_.

**Install Surround**

Run the following command to install Surround::

    $ pip3 install surround

To ensure that Surround installed properly, run the following command to test::
    
    $ surround --version

The bucket you created earlier will be used to store your cloud compute job experiment data. Surround’s experiment explorer will pull the data from that bucket. Set the path to that bucket with the following command, replacing ``<exp_data_bucket_name>`` with the name of the bucket you created earlier::
    
    $ surround config experiment.url gs://<exp_data_bucket_name>

**Deploy Job to Cloud**

**Generate project**

In order to deploy a job to the cloud, you will first need to have a project to deploy. Generate an empty Surround project with the following command::

    $ surround init -p test_project -d “My first cloud compute project”

When it asks the following, respond with ``n``::
    
    $ Does it require a web runner? (y/n) n

Running the project locally with the command::

    $ cd test_project    
    $ surround run batchLocal

Will output the following::

    .  batchLocal
    INFO:surround.assembler:Starting 'baseline'
    INFO:surround.assembler:Validator InputValidator took 0:00:00.00 secs
    INFO:surround.assembler:Estimator Baseline took 0:00:00.00 secs
    INFO:surround.assembler:Visualiser ReportGenerator took 0:00:00.00 secs

**Build and deploy**

To run the pipeline in the cloud you must first create a Docker image of the project. To ensure that Docker is running run the following command::

    $ docker info

If there was an error message displayed, navigate to your Applications folder and click on Docker to start Docker Desktop.
To create a Docker image of the project, run following command::
    
    $ surround run buildCompute

To prepare the pipeline to run on a GPU, instead run the following command::
    
    $ surround run buildComputeGPU

You now have an image of your pipeline that is ready to run in the cloud. To run your pipeline as a cloud job, call the following::
    
    $ surround run batchCompute

To run your training pipeline, instead call the following::
    
    $ surround run trainCompute

If you created the image to be run on a GPU, the commands are instead::

    $ surround run batchComputeGPU
    $ surround run trainComputeGPU

Your pipeline will now run as a job in the cloud.
    
**Monitor jobs**

**Surround command line**

After submitting the job with the commands in the previous section, the final two lines printed would have the following format, where ``<job_id>`` is replaced with the ID assigned to the job that you just created:

To check the status, run::

    $ surround run statusCompute <job_id>

Run that command to check the status of that individual job. To see a list of all jobs and their status for this project, run the following command::
    
    $ surround run listCompute 

To cancel a job that has not yet run/completed, run the following replacing ``<job_id>`` with the ID of the job you want to cancel ::
    
    $ surround run killCompute <job_id>

**Surround experiment explorer**

The surround experiment explorer presents a web interface for viewing experiment data from your jobs. Run the following command to launch the experiment explorer::

    $ surround experimentation

This will land you onto the Project Explorer page. Select your project to view the associated experiments. The table displayed will show data for each of the jobs that you created.
**Google cloud console**

The Google cloud console also provides an interface for monitoring jobs. From the navigation menu in the top left corner of the screen, scroll down to AI Platform and select Jobs. This will list all of the jobs associated with your project.

**Further reading**

For more detailed instructions on getting started with creating pipelines in Surround, check out the `Surround documentation <https://surround.readthedocs.io/en/latest/>`_.