import os
from surround import Config

CONFIG = Config(os.path.dirname(__file__))
DOIT_CONFIG = {'verbosity':2}
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
        'actions': ["docker run --volume %s/:/app %s" % (CONFIG["project_root"], IMAGE)]
    }

def task_prod():
    """Run the main task inside a Docker container for use in production """
    return {
        'actions': ["docker run %s" % IMAGE],
        'task_dep': ["build"]
    }
