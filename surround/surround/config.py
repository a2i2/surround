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

    if project_root:
        results = [path for path, _, files in os.walk(project_root) if 'config.yaml' in files]
        results = [path for path in results if os.path.basename(path) not in PROJECTS['new']['dirs'] and ".hydra" not in path]

        return results[0] if len(results) == 1 else None

def get_project_root_or_cwd():
    """
    Returns the project root when a project is found, otherwise returns the current working directory.

    :return: path to either the project root or current working directory
    :rtype: str
    """
    project_path = get_project_root()
    if project_path:
        return project_path

    return os.getcwd()

@dataclass
class SurroundConfig:
    """
    Surround specific configuration that dictates how it runs the pipeline.

    :cvar bool enable_stage_ouput_dump: Configures whether the dump_output method of Stage is called after its operation.
    :cvar bool surface_exceptions: Configurs whether exceptions are thrown during pipeline execution or consumed.
    """

    # Configures whether the dump_output method of Stage is called after its operation.
    enable_stage_output_dump: bool = False

    # Configures whether exceptions thrown during pipeline execution are surfaced.
    surface_exceptions: bool = False

@dataclass
class BaseConfig:
    """
    Base structured configuration class that should form the base of all custom
    configuration classes. Contains properties required by all Surround pipelines.

    :cvar Optional[str] project_root: Absolute path to the root of the Surround project.
    :cvar Optional[str] package_path: Absolute path to the package of the Surround project.
    :cvar Optional[str] volume_path: Absolute path to the root of the Surround project (formatted for use in Docker volume commands).
    :cvar Optional[str] input_path: Absolute path to the input folder where data should be loaded from.
    :cvar Optional[str] model_path: Absolute path to the models folder where models should be loaded from.
    :cvar Optional[str] output_path: Generated (datetime naming) absolute path to the output folder where output artifacts should be saved.
    :cvar SurroundConfig surround: Surround specific configuration that dictates how it runs the pipeline.
    """

    # Absolute path to the root of the project.
    project_root: Optional[str] = field(default_factory=get_project_root_or_cwd)

    # Absolute path to the package that will be executed to run the pipeline.
    package_path: Optional[str] = field(default_factory=lambda: find_package_path(get_project_root_or_cwd()))

    # Absolute path to the root of the project, formatted for use in Docker commands (auto generated via project_root).
    volume_path: Optional[str] = field(default_factory=lambda: generate_docker_volume_path(get_project_root_or_cwd()))

    # Absolute path to the inputs folder where data should be loaded from.
    input_path: Optional[str] = field(default_factory=lambda: os.path.join(get_project_root_or_cwd(), "input"))

    # Absolute path to the models folder where models should be loaded from.
    model_path: Optional[str] = field(default_factory=lambda: os.path.join(get_project_root_or_cwd(), "models"))

    # Absolute path to the output folder where outputs from the current run should be placed (timestamped folder). 
    output_path: Optional[str] = field(default_factory=lambda: os.path.join(get_project_root_or_cwd(), "output", str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))))

    # Surround specific configuration.
    surround: SurroundConfig = SurroundConfig()

def config(config_class=None, name="config", group=None):
    """
    Class decorator that registers a custom configuration class with 
    `Hydra's ConfigStore API <https://hydra.cc/docs/tutorials/structured_config/config_store>`_.

    If defining your own custom configuration class, your class must do the following:
        * Register with `Hydra's ConfigStore API <https://hydra.cc/docs/tutorials/structured_config/config_store>`_ (which this decorator does for you).
        * Register as a `@dataclass <https://docs.python.org/3/library/dataclasses.html>`_.

    Example::

        @config(name="db")
        @dataclass
        class DBConfig(BaseConfig):
            host: str = "localhost"

    .. note:: Make sure @dataclass comes after @config.

    This also supports `Hydra Config Groups <https://hydra.cc/docs/tutorials/structured_config/config_groups>`_, example::

        @config
        @dataclass
        class Config(BaseConfig):
            db: Any = MISSING

        @config(name="mysql", group="db")
        @dataclass
        class MySqlConfig:
            host: str = "mysql://localhost"
        
        @config(name="postgres", group="db")
        @dataclass
        class PostgresConfig:
            host: str = "postgres://localhost"
            postgres_specific_data: str = "some special data"

    Then when running the job you can do the following::

        $ python3 -m project_package db=mysql

    :param name: Name of the configuration, used to locate overrides.
    :type name: str
    :param group: Group name to support Hydra Config Groups.
    :type group: str
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

def load_config(name="config", config_class=BaseConfig, config_dir=None, overrides=None):
    """
    Loads the configuration instance using `Hydra's Compose API <https://hydra.cc/docs/experimental/compose_api>`_.

    Example::

        @config(name="db")
        @dataclass
        class DBConfig(BaseConfig):
            host: str = "localhost"

        config = load_config(name='db', config_class=DBConfig)
        assembler = Assembler(name='Pipeline', config)
        ...

    You could then override the value of ``host`` by creating a YAML
    file in the same working directory called ``db.yaml`` with the following::

        host: mysql://192.168.1.2

    :param name: Name of the configuration, used to locate overrides.
    :type name: str
    :param config_class: The class describing the schema of the configuration.
    :type config_class: :class:`BaseConfig`
    :param config_dir: Directory to search override config files for.
    :type config_dir: str
    :param overrides: Manual overrides of the configuration properties.
    :type overrides: dict
    """

    config_search_path = config_dir

    # User has not provided any config override search path...
    if not config_search_path:
        # Look for a Surround project in current working directory.
        config_search_path = find_package_path()

        # No project has been detected, use the specified config class directory instead.
        if not config_search_path and config_class and config_class != BaseConfig:
            classpath = sys.modules[config_class.__module__].__file__
            config_search_path = os.path.dirname(classpath)

    # Still no search path found, so search the current working directory.
    if not config_search_path:
        config_search_path = os.getcwd()

    # Register Config class with Hydra.
    if config_class:
        cs = ConfigStore.instance()
        cs.store(name=name, node=config_class)

    # Initialize hydra with the config search path.
    with initialize_config_dir(config_dir=config_search_path):
        # Create an instance of the config class, with any overrides found.
        config_instance = compose(config_name=name, overrides=overrides)
        return config_instance
