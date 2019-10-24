import ast
import os

from pathlib import Path
from collections.abc import Mapping
from pkg_resources import resource_stream

import yaml

from .util import generate_docker_volume_path
from .project import PROJECTS

ENV_VAR_PREFIX = "SURROUND_"

class Config(Mapping):
    """
    An iterable dictionary class that loads and stores all the configuration settings from
    both default and project YAML files and environment variables. Primarily used in stages
    to retrieve configuration data set for development/production.

    Responsibilities:

    - Parse the config.yaml file and store the data as key-value pairs.
    - Allow environment variables override data loaded from file/dict (must be prefixed with ``SURROUND_``).
    - Provide READ-ONLY access to the stored config values via ``[]`` operator and iteration.

    Example usage::

        config = Config()
        config.read_from_dict({ "debug": True })
        config.read_config_files(["config.yaml"])

        if config["debug"]:
            # Do debug stuff

        for key, value in config:
            # Iterate over all data

    You could then override the above configuration using the systems environment variables,
    just prefix the var with `SURROUND_` like so::

        SURROUND_DEBUG=False

    It also supports overriding nested configuration data, for example with the following config::

        predict:
            debug: True

    We can override the above with the following environment variable::

        SURRROUND_PREDICT_DEBUG=False
    """

    def __init__(self, project_root=None, package_path=None, auto_load=False):
        """
        Constructor of the Config class, loads the default YAML file into storage.
        If the :attr:`project_root` is provided then the project's `config.yaml`
        file is also loaded into configuration.

        The default config file (`defaults.yaml`) can be found in the same directory as the `config.py` script.
        The project config file (`config.yaml`) can be found in the root of the project folder.

        :param project_root: path to the root directory of the surround project (default: None)
        :type project_root: str
        :param package_path: path to the root directory of the package that contains the surround project (default: None)
        :type package_path: str
        :param auto_load: Attempt to load the config.yaml file from the Surround project in the current directory (default: False)
        :type auto_load: bool
        """

        self._storage = self.__load_defaults()

        # Try to get the project root if none specified
        if auto_load and not project_root:
            project_root = self.__get_project_root_from_current_dir()

        # Set framework paths
        if project_root:
            # Resolve absolute path
            project_root = str(Path(project_root).resolve())
            volume_path = generate_docker_volume_path(project_root)

            # Attempt to find package path by looking for config.yaml
            if not package_path:
                package_path = self.__find_package_path(project_root)

            self._storage["project_root"] = project_root
            self._storage["package_path"] = package_path
            self._storage["volume_path"] = volume_path
            self._storage["output_path"] = os.path.join(project_root, "output")
            self._storage["input_path"] = os.path.join(project_root, "input")
            self._storage["models_path"] = os.path.join(project_root, "models")

            # Load project config
            if package_path:
                config_path = os.path.join(package_path, 'config.yaml')
            else:
                config_path = os.path.join(project_root, os.path.basename(project_root), 'config.yaml')

            if os.path.exists(config_path):
                self.read_config_files([config_path])

    def read_config_files(self, yaml_files):
        """
        Parses the YAML files provided and stores their key-value pairs in config.

        :param yaml_files: multiple paths to the YAML files to load
        :type yaml_files: list
        :return: true on success, throws :exc:`IOError` on failure
        :rtype: bool
        """

        configs = []
        try:
            for path in yaml_files:
                with open(path) as afile:
                    configs.append(yaml.safe_load(afile.read()))
        except IOError as err:
            err.strerror = 'Unable to load configuration file (%s)' % err.strerror
            raise

        self.__merge_configs(configs)
        self.__insert_environment_variables()
        return True

    def read_from_dict(self, config_dict):
        """
        Retrieve all key-value pairs from the dict provided and store in config.

        :param config_dict: configuration settings to be added to storage
        :type config_dict: dict
        :return: true on success, throws exception on failure (:exc:`TypeError`)
        :rtype: bool
        """

        if not isinstance(config_dict, dict):
            return TypeError("config_dict should be a dict")

        self.__merge_configs([config_dict])
        self.__insert_environment_variables()
        return True

    def get_path(self, path):
        """
        Returns value that can be found at the key path provided (useful for nested values).

        For example::

            config.get_path('surround.stages') == config['surround']['stages']
            --> True

        :param path: path to the value in storage
        :type path: str
        :return: the value found at the path or none if not found
        :rtype: any
        """

        if not isinstance(path, str):
            raise TypeError("path should be a string")
        if not "." in path:
            return self._storage[path] if path in self._storage else None
        return self.__iterate_over_dict(self._storage, path.split("."))

    def get_dict(self):
        """
        Returns the configuration data in a dictionary

        :returns: dictionary of the configuration data
        :rtype: dict
        """

        return self._storage

    def __find_package_path(self, project_root):
        """
        Attempts to find the projects package path by looking for the config.yaml file.
        This should only be used when the package name seems to be different from the root folder name.

        :param project_root: root of the project
        :type project_root: str
        :return: path to the package or None if unable to find it
        :rtype: str
        """

        results = [path for path, _, files in os.walk(project_root) if 'config.yaml' in files]
        results = [path for path in results if os.path.basename(path) not in PROJECTS['new']['dirs']]

        return results[0] if len(results) == 1 else None

    def __load_defaults(self):
        """
        Returns the config key-value pairs loaded from defaults.yaml.

        :return: the key-value pairs loaded from the file
        :rtype: dict
        """

        try:
            with resource_stream(__name__, "defaults.yaml") as f:
                config = yaml.safe_load(f)
        except IOError as err:
            err.strerror = 'Unable to load default config file'
            raise
        return config

    def __get_project_root_from_current_dir(self):
        return self.__get_project_root(os.getcwd())

    def __get_project_root(self, current_directory):
        home = str(Path.home())

        while True:
            list_ = os.listdir(current_directory)
            parent_directory = os.path.dirname(current_directory)
            if current_directory in (home, parent_directory):
                break
            elif ".surround" in list_:
                return current_directory
            current_directory = parent_directory

    def __merge_configs(self, configs):
        """
        Merges a list of dictionaries into the dictionary of this class. Note that lists are
        overriden completely not extended.

        :param configs: a collection of dictionaries to merge into storage
        :type configs: a list of dict
        """

        if not isinstance(configs, list):
            raise TypeError("configs should be a list")

        def extend_dict(target, src):
            """
            Merges the key-value pairs in src into the given target dictionary.

            :param target: the target dictionary being extended
            :type target: dict
            :param src: the dictionary where key-value pairs are being extracted
            :type src: dict
            """

            if isinstance(src, dict):
                for k, v in src.items():
                    if k in target:
                        if isinstance(target[k], dict):
                            extend_dict(target[k], v)
                        else:
                            target[k] = v
                    else:
                        target[k] = v

        for config in configs:
            extend_dict(self._storage, config)

    def __insert_environment_variables(self):
        """
        Inserts environment variables prefixed with ENV_VAR_PREFIX into storage. Overriding any
        clashing key-value pairs in storage already.

        Example:
        SURROUND_TEST_KEY='test_value'
        This will be loaded into storage as a string value and can be found at path 'test.key' (or `config['test']['key']`)
        """

        for var in os.environ:
            if not var.startswith(ENV_VAR_PREFIX) or len(var) == len(ENV_VAR_PREFIX):
                continue
            surround_variables = [n.lower() for n in var[len(ENV_VAR_PREFIX):].split("_") if n]
            self.__override_or_add_var(self._storage, surround_variables, os.getenv(var))

    def __override_or_add_var(self, config, key_list, value):
        """
        Recursively inserts or overrides the value in the storage specified at the specified path.

        :param config: the storage container we're adding the value to
        :type config: dict
        :param key_list: collection of keys that specifies the key path (e.g. ["test", "key"] == 'test.key')
        :type key_list: list of str
        :param value: the value being set to the specified path
        :type value: any
        :return: the storage container we've been adding to
        :rtype: dict
        """

        if len(key_list) > 1:
            key = key_list[0]
            if not key in config:
                config[key] = dict()
            self.__override_or_add_var(config[key], key_list[1:], value)
        else:
            new_key = key_list[0]
            if new_key in config:
                the_type = type(config[new_key])
            else:
                try:
                    the_type = type(ast.literal_eval(value))
                    if the_type == bool:
                        value = ast.literal_eval(value)
                except Exception:
                    if value.lower() == "true":
                        value = True
                        the_type = bool
                    elif value.lower() == "false":
                        value = False
                        the_type = bool
                    else:
                        the_type = str

            config[new_key] = the_type(value)
        return config

    def __iterate_over_dict(self, dictionary, key_list):
        """
        Return the value of the last key in the key list provided by traversing the dict tree.

        Example::
            self.__iterate_over_dict({ "a": { "b": "c" } }, ["a", "b"])
            --> "c"

        :param dictionary: the dictionary we are finding the value in
        :type dictionary: dict
        :param key_list: collection of key names (correspond to the path to the value in the dictionary)
        :type key_list: list of str
        :return: the value found or none if not found
        :rtype: any
        """

        key = key_list[0] if not key_list == [] else ""
        if key in dictionary:
            if len(key_list) > 1:
                return self.__iterate_over_dict(dictionary[key], key_list[1:])
            return dictionary[key]
        return None

    def __getitem__(self, key):
        """
        Provides access to stored data via the [] operator.

        :param key: the key provided in the [] operator
        :type key: str
        :return: the value found at the specified key
        :rtype: any
        """

        return self._storage[key]

    def __iter__(self):
        """
        Allows for iteration through the config dictionary.

        Example::

            config = Config()
            config.read_config_files(['config.yaml'])

            # Iterate over the key-value pairs in the config data
            for key, value in config:
                print("Key: " + key + " Value: " + value)

        :return: the iterator for the internal dictionary
        :rtype: dict_keyiterator
        """

        return iter(self._storage)

    def __len__(self):
        """
        Returns the length of the config dictionary.

        :return: the number of key-value pairs in the dictionary
        :rtype: int
        """

        return len(self._storage)
