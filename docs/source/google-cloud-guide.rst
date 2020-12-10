Using Google Cloud Compute
==========================

Introduction
^^^^^^^^^^^^

Google cloud compute deployment feature will let users run their experiments in the cloud and stores all experiment results in the cloud bucket (a data storage in the cloud). This feature allows user to deploy a docker image to the cloud using command line interface, then users can use the GPU in the cloud to train and predict.

This following steps will outline the steps to prepare your MacOS environment to use the google cloud compute deployment feature in Surround.

Google Cloud Setup
^^^^^^^^^^^^^^^^^^

Create account
^^^^^^^^^^^^^^

This feature requires the use of a Google Cloud Platform account. If you do not already have an account, follow the steps under Getting Started at cloud.google.com to create an account for free.

Create project
^^^^^^^^^^^^^^

Create a new project from the `Google Cloud Console <https://console.cloud.google.com/>`_. Alternatively, you can use the project that was automatically generated when you created your account.

Navigate to the `APIs and Services Dashboard <https://console.cloud.google.com/apis/>`_ and click the button at the top of the screen to enable APIs. Search for and enable the following APIs:

1. AI Platform Training & Prediction API
2. Compute Engine API
3. Container Registry API

Create service account
^^^^^^^^^^^^^^^^^^^^^^

To connect your Surround project to your Google Cloud project, you will need to provide a credentials file. Follow the steps below to create the file.

1. From the Google Cloud Console, navigate to the `Google Cloud Credentials <https://console.cloud.google.com/apis/credentials>`_ page.
2. Click on Create credentials and select the option to create a service account key.
3. Select “Compute Engine default service account” as your service account and select JSON as the key type.
4. Locate the file in your downloads and move it to a suitable location.

Open terminal and set an environment variable ``GOOGLE_APPLICATION_CREDENTIALS`` to the filepath of the credentials file. This will tell Surround where to look for the file. Use the following command to set the environment variable for the current terminal session, replacing ``<path_to_credentials_json>`` with the file path of the credentials file::

    $ export GOOGLE_APPLICATION_CREDENTIALS=<path_to_credentials_json>

If you want to permanently set this environment variable so that it is saved between terminal sessions, complete the following steps for MacOS:

1.Change directory into your home directory:
    
    $ cd ~

2. Edit ``.bash_profile`` in terminal (or edit using your preferred text editor) to include the file path::
    
    $ nano .bash_profile
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/json/credentials.json

3. Restart terminal and check that the environment variable is set::

    $ echo $GOOGLE_APPLICATION_CREDENTIALS

Create bucket for experiment data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To view your experiment data with Surround’s experiment explorer, you will have to create a bucket to store the experiment data. From the Google Cloud Console Dashboard, navigate to Storage (under Resources). 

Click the button near the top of the screen to create a new bucket. Follow the steps to create the bucket and remember the name for later steps.

Local Environment Setup
^^^^^^^^^^^^^^^^^^^^^^^

Install Python and Pip
^^^^^^^^^^^^^^^^^^^^^^

Surround is installed using pip and the projects are written in python.
Follow the steps to install python `here <https://docs.python.org/3/using/mac.html>`_.
Follow the steps to install pip `here <https://pip.pypa.io/en/stable/installing/>`_.

Install Docker
^^^^^^^^^^^^^^

Docker is used to create images of your Surround project. The image of your project is submitted as a cloud compute job.

Follow the steps to install Docker Desktop `here <https://docs.docker.com/docker-for-mac/install/>`_.

Install Surround
^^^^^^^^^^^^^^^^

Run the following command to install Surround::

    $ pip3 install surround

To ensure that Surround installed properly, run the following command to test::
    
    $ surround --version

The bucket you created earlier will be used to store your cloud compute job experiment data. Surround’s experiment explorer will pull the data from that bucket. Set the path to that bucket with the following command, replacing ``<exp_data_bucket_name>`` with the name of the bucket you created earlier::
    
    $ surround config experiment.url gs://<exp_data_bucket_name>

Deploy Job to Cloud
^^^^^^^^^^^^^^^^^^^

Generate project
^^^^^^^^^^^^^^^^

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

Build and deploy
^^^^^^^^^^^^^^^^

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
    
Monitor jobs
^^^^^^^^^^^^

Surround command line
^^^^^^^^^^^^^^^^^^^^^

After submitting the job with the commands in the previous section, the final two lines printed would have the following format, where ``<job_id>`` is replaced with the ID assigned to the job that you just created:

To check the status, run::

    $ surround run statusCompute <job_id>

Run that command to check the status of that individual job. To see a list of all jobs and their status for this project, run the following command::
    
    $ surround run listCompute 

To cancel a job that has not yet run/completed, run the following replacing ``<job_id>`` with the ID of the job you want to cancel ::
    
    $ surround run killCompute <job_id>

Surround experiment explorer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The surround experiment explorer presents a web interface for viewing experiment data from your jobs. Run the following command to launch the experiment explorer::

    $ surround experimentation

This will land you onto the Project Explorer page. Select your project to view the associated experiments. The table displayed will show data for each of the jobs that you created.
Google cloud console
^^^^^^^^^^^^^^^^^^^^

The Google cloud console also provides an interface for monitoring jobs. From the navigation menu in the top left corner of the screen, scroll down to AI Platform and select Jobs. This will list all of the jobs associated with your project.

Further reading
^^^^^^^^^^^^^^^

For more detailed instructions on getting started with creating pipelines in Surround, check out the `Surround documentation <https://surround.readthedocs.io/en/latest/>`_.