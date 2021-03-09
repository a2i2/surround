"""
This module defines the tasks that can be executed using `surround run [task name]`
"""

import os
import sys
import subprocess

from pathlib import Path
from doit.tools import LongRunning
from surround import Config

CONFIG = Config(os.path.dirname(__file__))
DOIT_CONFIG = {"verbosity": 2, "backend": "sqlite3", "default_tasks": ["status"]}
PACKAGE_PATH = os.path.basename(CONFIG["project_root"])
IMAGE = "%s/%s:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])
IMAGE_JUPYTER = "%s/%s-jupyter:%s" % (
    CONFIG["company"],
    CONFIG["image"],
    CONFIG["version"],
)
DOCKER_JUPYTER = "Dockerfile.Notebook"

PARAMS = [{"name": "args", "long": "args", "type": str, "default": ""}]


def run(image, args, docker_args=None):
    if docker_args is None:
        docker_args = []
    cmd = (
        ["docker", "run"]
        + docker_args
        + ["--volume", "%s/:/app" % CONFIG["volume_path"]]
    )
    return [LongRunning(" ".join(cmd + [image] + args))]


def task_status():
    """Show information about the project such as available runners and assemblers"""
    return {"actions": ["%s -m %s --status" % (sys.executable, PACKAGE_PATH)]}


def task_build():
    """Build the Docker image for the current project"""
    return {
        "actions": ["docker build --tag=%s -f ./docker/Dockerfile ." % IMAGE],
        "params": PARAMS,
    }


def task_remove():
    """Remove the Docker image for the current project"""
    return {"actions": ["docker rmi %s -f" % IMAGE], "params": PARAMS}


def task_interactive():
    """Run the Docker container in interactive mode"""

    def interactive():
        cmd = run(IMAGE, ["bash"], ["-it", "--rm"])[0].split(" ")
        process = subprocess.Popen(cmd, encoding="utf-8")
        process.wait()

    return {"actions": [interactive]}


def task_build_jupyter():
    """Build the Docker image for a Jupyter Lab notebook"""
    return {
        "basename": "buildJupyter",
        "actions": ["docker build --tag=%s . -f %s" % (IMAGE_JUPYTER, DOCKER_JUPYTER)],
        "task_dep": ["build"],
    }


def task_jupyter():
    """Run a Jupyter Lab notebook"""
    return {
        "actions": run(IMAGE_JUPYTER, [], docker_args=["-itp", "8888:8888"]),
    }


def task_interactive_jupyter():
    """Run the Docker Jupyter container in interactive mode"""

    def interactive():
        cmd = run(IMAGE_JUPYTER, ["bash"], ["-it", "--rm", "-w", "/app"])[0].split(" ")
        process = subprocess.Popen(cmd, encoding="utf-8")
        process.wait()

    return {"actions": [interactive], "basename": "interactiveJupyter"}


def task_train():
    """Run training mode inside the container"""

    return {
        "actions": run(IMAGE, ["python3", "-m", "web_app", "--mode", "train"]),
        "params": PARAMS,
    }


def task_batch():
    """Run batch mode inside the container"""
    return {
        "actions": run(IMAGE, ["python3", "-m", "web_app", "--mode", "batch"]),
        "params": PARAMS,
    }


def task_main():
    """Run project inside container"""
    cmd = ["python3 -m %s" % PACKAGE_PATH, "--runner WebRunner", "%(args)s"]

    return {"actions": run(IMAGE, cmd, ["-p", "8080:8080"]), "params": PARAMS}


def task_experiment():
    """Run experiment in a Docker container"""
    cmd = ["mlflow", "run", "-P", "mode=%(mode)s", "."]
    return {
        "actions": [" ".join(cmd)],
        "params": [{"name": "mode", "long": "mode", "type": str, "default": "train"}],
    }


def task_format():
    """Run Python code formatter for the project"""
    return {"actions": ["black ."]}


def task_lint():
    """Run Python linter for the project"""
    return {"actions": ["mypy web_app", "pylint web_app"]}


def task_test():
    """Runs the unit and integration tests"""
    return {"actions": ["python -m unittest discover -s tests"]}
