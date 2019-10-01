import os
import sys
from surround import Config

CONFIG = Config(os.path.dirname(__file__))
DOIT_CONFIG = {'verbosity':2}
PACKAGE_PATH = os.path.basename(CONFIG["package_path"])
IMAGE = "%s/%s:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])

def task_build():
    """Build the Docker image for the current project"""
    return {
        'actions': ['docker build --tag=%s .' % IMAGE]
    }

def task_remove():
    """Remove the Docker image for the current project"""
    return {
        'actions': ['docker rmi %s -f' % IMAGE]
    }

def task_dev():
    """Run the main task for the project"""
    return {
        'actions': ["docker run -p 8080:8080 --volume \"%s/\":/app %s python3 -m %s" % (CONFIG["volume_path"], IMAGE, PACKAGE_PATH)]
    }

def task_prod():
    """Run the main task inside a Docker container for use in production """
    return {
        'actions': ["docker run -p 8080:8080 %s python3 -m %s" % (IMAGE, PACKAGE_PATH)],
        'task_dep': ["build"]
    }

def task_train():
    """Run training mode inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"

    return {
        'actions': ["docker run --volume \"%s\":/app/output --volume \"%s\":/app/input %s python3 -m temp --mode train" % (output_path, data_path, IMAGE)]
    }

def task_batch():
    """Run batch mode inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"

    return {
        'actions': ["docker run --volume \"%s\":/app/output --volume \"%s\":/app/input %s python3 -m temp --mode batch" % (output_path, data_path, IMAGE)]
    }

def task_train_local():
    """Run training mode locally"""
    return {
        'basename': 'trainLocal',
        'actions': ["%s -m %s --mode train" % (sys.executable, PACKAGE_PATH)]
    }

def task_batch_local():
    """Run batch mode locally"""
    return {
        'basename': 'batchLocal',
        'actions': ["%s -m %s --mode batch" % (sys.executable, PACKAGE_PATH)]
    }

def task_web():
    """Run web mode inside the container"""
    return {
        'actions': ["docker run -p 8080:8080  %s python3 -m %s --mode web" % (IMAGE, PACKAGE_PATH)]
    }

def task_web_local():
    """Run web mode locally"""
    return {
        'basename': 'webLocal',
        'actions': ["%s -m %s --mode web" % (sys.executable, PACKAGE_PATH)]
    }
