"""
This module defines the tasks that can be executed using `surround run [task name]`
"""

import os
import sys
import subprocess

from surround import load_config
from web_runner_sample.config import Config

CONFIG = load_config(name="config", config_class=Config)
DOIT_CONFIG = {'verbosity':2, 'backend':'sqlite3'}
PACKAGE_PATH = os.path.basename(CONFIG["package_path"])
IMAGE = "%s/%s:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])
IMAGE_JUPYTER = "%s/%s-jupyter:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])
DOCKER_JUPYTER = "Dockerfile.Notebook"

PARAMS = [
    {
        'name': 'args',
        'long': 'args',
        'type': str,
        'default': ""
    }
]

def task_status():
    """Show information about the project such as available runners and assemblers"""
    return {
        'actions': ["%s -m %s status=1" % (sys.executable, PACKAGE_PATH)]
    }

def task_build():
    """Build the Docker image for the current project"""
    cmd = ['poetry install &&',    # Installing dependencies
           'poetry export -f requirements.txt --output requirements.txt --dev --without-hashes &&',
           'docker build --tag=%s .' % IMAGE]
    return {
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_remove():
    """Remove the Docker image for the current project"""
    return {
        'actions': ['docker rmi %s -f' % IMAGE],
        'params': PARAMS
    }

def task_dev():
    """Run the main task for the project"""
    cmd = [
        "docker",
        "run",
        "-p 8081:8081",
        "--volume",
        "\"%s/\":/app" % CONFIG["volume_path"],
        "%s" % IMAGE,
        "python3 -m %s %s" % (PACKAGE_PATH, "%(args)s")
    ]
    return {
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_interactive():
    """Run the Docker container in interactive mode"""
    def run():
        cmd = [
            'docker',
            'run',
            '-p',
            '8081:8081',
            '-it',
            '--rm',
            '-w',
            '/app',
            '--volume',
            '%s/:/app' % CONFIG['volume_path'],
            IMAGE,
            'bash'
        ]
        process = subprocess.Popen(cmd, encoding='utf-8')
        process.wait()

    return {
        'actions': [run]
    }

def task_prod():
    """Run the main task inside a Docker container for use in production """
    cmd = [
        "docker",
        "run",
        "-p 8081:8081",
        IMAGE,
        "python3 -m %s" % PACKAGE_PATH,
        "%(args)s"
    ]

    return {
        'actions': [" ".join(cmd)],
        'task_dep': ["build"],
        'params': PARAMS
    }

def task_train():
    """Run training mode inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"

    cmd = [
        "docker run",
        "--volume \"%s\":/app/output" % output_path,
        "--volume \"%s\":/app/input" % data_path,
        "%s" % IMAGE,
        "python3 -m web_runner_sample mode=train runner=1 %(args)s"
    ]

    return {
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_batch():
    """Run batch mode inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"

    cmd = [
        "docker run",
        "--volume \"%s\":/app/output" % output_path,
        "--volume \"%s\":/app/input" % data_path,
        "%s" % IMAGE,
        "python3 -m web_runner_sample mode=batch runner=1 %(args)s"
    ]

    return {
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_train_local():
    """Run training mode locally"""
    cmd = [
        "poetry install &&",                                # Installing dependencies
        "source `poetry env info --path`/bin/activate &&",  # Entering virtual env
        sys.executable,
        "-m %s" % PACKAGE_PATH,
        "mode=train",
        "runner=1",
        "%(args)s",
        "&& deactivate"                                     # Exiting virtual env
    ]

    return {
        'basename': 'trainLocal',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_batch_local():
    """Run batch mode locally"""
    cmd = [
        "poetry install &&",                                # Installing dependencies
        "source `poetry env info --path`/bin/activate &&",  # Entering virtual env
        sys.executable,
        "-m %s" % PACKAGE_PATH,
        "mode=batch",
        "runner=1",
        "%(args)s",
        "&& deactivate"                                     # Exiting virtual env
    ]

    return {
        'basename': 'batchLocal',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_web():
    """Run web mode inside the container"""
    cmd = [
        "docker",
        "run",
        "-p",
        "8081:8081",
        IMAGE,
        "python3 -m %s" % PACKAGE_PATH,
        "runner=WebRunner",
        "%(args)s"
    ]

    return {
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_web_local():
    """Run web mode locally"""
    cmd = [
        "poetry install &&",                                # Installing dependencies
        "source `poetry env info --path`/bin/activate &&",  # Entering virtual env
        sys.executable,
        "-m %s" % PACKAGE_PATH,
        "runner=WebRunner",
        "%(args)s",
        "&& deactivate"                                     # Exiting virtual env
    ]

    return {
        'basename': 'webLocal',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_build_jupyter():
    """Build the Docker image for a Jupyter Lab notebook"""
    cmd = ['poetry install &&',                                # Installing dependencies
           'poetry export -f requirements.txt --output requirements.txt --dev --without-hashes &&',
           'docker build --tag=%s . -f %s' % (IMAGE_JUPYTER, DOCKER_JUPYTER)]
    return {
        'basename': 'buildJupyter',
        'actions': [" ".join(cmd)],
        'task_dep': ['build'],
        'params': PARAMS
    }

def task_jupyter():
    """Run a Jupyter Lab notebook"""
    cmd = [
        "docker",
        "run",
        "-itp",
        "8888:8888",
        '-w',
        '/app',
        "--volume",
        "\"%s/\":/app" % CONFIG["volume_path"],
        IMAGE_JUPYTER
    ]
    return {
        'actions': [" ".join(cmd)],
    }
