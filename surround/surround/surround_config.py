import os
import sys
import functools
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from datetime import datetime
from hydra.core.config_store import ConfigStore
from hydra.experimental import compose, initialize_config_dir
from .project import PROJECTS
from .util import generate_docker_volume_path

def get_project_root(current_directory: str = os.getcwd()) -> Optional[str]:
    """
    Attempts to find the root path of the project by looking for the .surround
    folder that should be present in all generated Surround projects.
    
    :param current_directory: directory to start searching from
    :type current_directory: str
    """

    home = str(Path.home())

    while True:
        list_ = os.listdir(current_directory)
        parent_directory = os.path.dirname(current_directory)
        if current_directory in (home, parent_directory):
            break
        if ".surround" in list_:
            return current_directory
        current_directory = parent_directory

def find_package_path(project_root: str = get_project_root()) -> Optional[str]:
    """
    Attempts to find the projects package path by looking for the config.yaml file.
    This should only be used when the package name seems to be different from the root folder name.

    :param project_root: root of the project
    :type project_root: str
    :return: path to the package or None if unable to find it
    :rtype: str
    """

    results = [path for path, _, files in os.walk(project_root) if 'config.yaml' in files]
    results = [path for path in results if os.path.basename(path) not in PROJECTS['new']['dirs'] and ".hydra" not in path]

    return results[0] if len(results) == 1 else None

@dataclass
class SurroundConfig:
    # Configures whether the dump_output method of Stage is called after its operation.
    enable_stage_output_dump: bool = False

    # Configures whether exceptions thrown during pipeline execution are surfaced.
    surface_exceptions: bool = False

@dataclass 
class BaseConfig:
    # Absolute path to the root of the project.
    project_root: str = field(default_factory=get_project_root)

    # Absolute path to the package that will be executed to run the pipeline.
    package_path: str = field(default_factory=lambda: find_package_path(get_project_root()))

    # Absolute path to the root of the project, formatted for use in Docker commands (auto generated via project_root).
    volume_path: str = field(default_factory=lambda: generate_docker_volume_path(get_project_root()))

    # Absolute path to the inputs folder where data should be loaded from.
    input_path: str = field(default_factory=lambda: os.path.join(get_project_root(), "input"))

    # Absolute path to the models folder where models should be loaded from.
    model_path: str = field(default_factory=lambda: os.path.join(get_project_root(), "models"))

    # Absolute path to the output folder where outputs from the current run should be placed (timestamped folder). 
    output_path: str = field(default_factory=lambda: os.path.join(get_project_root(), "output", str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))))

    # Surround specific configuration.
    surround: SurroundConfig = SurroundConfig()

def config(config_class=None, name="config", group=None):
    """
    Class decorator that registers the config class with Hydra's ConfigStore.
    """

    @functools.wraps(config_class)
    def wrapper(config_class, name, group):
        cs = ConfigStore.instance()
        cs.store(name=name, node=config_class, group=group)
        return config_class

    if config_class:
        return wrapper(config_class, name, group)

    def recursive_wrapper(config_class):
        return config(config_class, name, group)

    return recursive_wrapper

def load_config(name="config", config_class=BaseConfig, config_dir=None):
    """
    Loads the configuration instance using Hydra's Compose API.
    """

    config_search_path = config_dir

    # Register Config class with Hydra.
    if config_class:
        cs = ConfigStore.instance()
        cs.store(name=name, node=config_class)

        # Get path to config script, search for overrides in the same folder.
        classpath = sys.modules[config_class.__module__].__file__
        config_search_path = os.path.dirname(classpath)
    elif not config_search_path: 
        # Try to get the project package if no search path provided.
        config_search_path = find_package_path()

    # Initialize hydra with the config search path.
    with initialize_config_dir(config_dir=config_search_path):
        # Create an instance of the config class, with any overrides found.
        config = compose(config_name=name)
        return config

def has_config(func=None, name="config", config_class=None):
    """
    Function decorator that injects the hyrdra config into the arguments of the function.
    """

    @functools.wraps(func)
    def function_wrapper(*args, **kwargs):
        # Load the config instance.
        config = load_config(name, config_class)

        # Inject this instance into the function argument.
        kwargs[name] = config
        return func(*args, **kwargs)

    if func:
        return function_wrapper

    def recursive_wrapper(func):
        return has_config(func, name, config_class)

    return recursive_wrapper
