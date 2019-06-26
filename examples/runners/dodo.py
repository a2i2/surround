import os
from surround import Config

CONFIG: Config = Config(os.path.dirname(__file__))
DOIT_CONFIG: dict = {'verbosity':2}
IMAGE: str = "%s/%s:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])

def task_build() -> dict:
    """Build the Docker image for the current project"""
    return {
        'actions': ['docker build --tag=%s .' % IMAGE]
    }

def task_remove() -> dict:
    """Remove the Docker image for the current project"""
    return {
        'actions': ['docker rmi %s -f' % IMAGE]
    }

def task_dev() -> dict:
    """Run the main task for the project"""
    return {
        'actions': ["docker run --volume %s/:/app %s" % (CONFIG["project_root"], IMAGE)]
    }

def task_prod() -> dict:
    """Run the main task inside a Docker container for use in production """
    return {
        'actions': ["docker run %s" % IMAGE],
        'task_dep': ["build"]
    }
