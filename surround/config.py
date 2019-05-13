import ast
import os
from pathlib import Path
from collections.abc import Mapping
from pkg_resources import resource_stream

import yaml

ENV_VAR_PREFIX = "SURROUND_"

class Config(Mapping):
    """
    An iterable dictionary class that loads and stores all the configuration settings from
    both default and project YAML files and environment variables.

    Responsibilities:
    - Parse the config.yaml file and store the data as key-value pairs.
    - Allow environment vars override data loaded from file/dict (must be prefixed with ENV_VAR_PREFX).
    - Provide READ-ONLY access to the stored config values via [key] and iteration.

    Public methods (see methods for more information):
    - read_config_files(yaml_files)
    - read_from_dict(config_dict)
    - get_path(path)
    """

    def __init__(self, project_root=None):
        """
        Constructor of the Config class, loads the default and project YAML files into storage,
        and sets the framework paths into storage (if project root provided).

        :param project_root: path to the root directory of the surround project (default: None)
        :type project_root: string
        """

        self._storage = self.__load_defaults()

        # Set framework paths
        if project_root:
            # Resolve absolute path
            project_root = str(Path(project_root).resolve())

            # If the system has a drive letter, change the project_root to /c/rest/of/path
            split_path = os.path.splitdrive(project_root)
            if split_path[0] != '':
                drive_letter = split_path[0][0].lower()
                path = split_path[1].replace('\\', '/')
                project_root = '/' + drive_letter + path

            self._storage["project_root"] = project_root
            self._storage["package_path"] = package_path
            self._storage["output_path"] = os.path.join(project_root, "output")
            self._storage["data_path"] = os.path.join(project_root, "data")
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
        :type yaml_files: list of strings
        :return: True on success, throws on failure
        :rtype: Boolean or IOError exception
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
        :type config_dict: dictionary
        :return: true on success, throws exception on failure
        :rtype: bool or TypeError
        """

        if not isinstance(config_dict, dict):
            return TypeError("config_dict should be a dict")

        self.__merge_configs([config_dict])
        self.__insert_environment_variables()
        return True

    def get_path(self, path):
        """
        Returns value that can be found at the key path provided (useful for nested values).

        Example:
        config.get_path('surround.stages') is equivalent to config['surround']['stages']

        :param path: path to the value in storage
        :type path: string
        :return: the value found at the path or none if not found
        :rtype: any
        """

        if not isinstance(path, str):
            raise TypeError("path should be a string")
        if not "." in path:
            return self._storage[path]
        return self.__iterate_over_dict(self._storage, path.split("."))

    def __load_defaults(self):
        """
        Returns the config key-value pairs loaded from defaults.yaml.

        :return: the key-value pairs loaded from the file
        :rtype: dictionary
        """

        try:
            with resource_stream(__name__, "defaults.yaml") as f:
                config = yaml.safe_load(f)
        except IOError as err:
            err.strerror = 'Unable to load default config file'
            raise
        return config

    def __merge_configs(self, configs):
        """
        Merges a list of dictionaries into the dictionary of this class. Note that lists are
        overriden completely not extended.

        :param configs: a collection of dictionaries to merge into storage
        :type configs: a list of dictionaries
        """

        if not isinstance(configs, list):
            raise TypeError("configs should be a list")

        def extend_dict(target, src):
            """
            Merges the key-value pairs in src into the given target dictionary.

            :param target: the target dictionary being extended
            :type target: dictionary
            :param src: the dictionary where key-value pairs are being extracted
            :type src: dictionary
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
        This will be loaded into storage as a string value and can be found at path 'test.key' (or config['test']['key'])
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
        :type config: dictionary
        :param key_list: collection of keys that specifies the key path (e.g. ["test", "key"] == 'test.key')
        :type key_list: list of strings
        :param value: the value being set to the specified path
        :type value: any
        :return: the storage container we've been adding to
        :rtype: dictionary
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
                the_type = type(ast.literal_eval(value))
            config[new_key] = the_type(value)
        return config

    def __iterate_over_dict(self, dictionary, key_list):
        """
        Return the value of the last key in the key list provided by traversing the dict tree.

        Example:
        self.__iterate_over_dict({ "a": { "b": "c" } }, ["a", "b"]) would return "c".

        :param dictionary: the dictionary we are finding the value in
        :type dictionary: dictionary
        :param key_list: collection of key names (correspond to the path to the value in the dictionary)
        :type key_list: list of strings
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
        :type key: string
        :return: the value found at the specified key
        :rtype: any
        """

        return self._storage[key]

    def __iter__(self):
        """
        Allows for iteration through the config dictionary.

        :return: the iterator for the internal dictionary
        :rtype: iterator
        """

        return iter(self._storage)

    def __len__(self):
        """
        Returns the length of the config dictionary.

        :return: the number of key-value pairs in the dictionary
        :rtype: integer
        """

        return len(self._storage)
