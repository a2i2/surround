import ast
import os
from collections.abc import Mapping
from pkg_resources import resource_stream

import yaml

ENV_VAR_PREFIX = "SURROUND_"

class Config(Mapping):

    def __init__(self):
        self._storage = self.__load_defaults()

    def read_config_files(self, yaml_files):
        configs = []
        try:
            for path in reversed(yaml_files):
                with open(path) as afile:
                    configs.append(yaml.safe_load(afile.read()))
        except IOError as err:
            err.strerror = 'Unable to load configuration file (%s)' % err.strerror
            raise

        self.__merge_configs(configs)
        self.__insert_environment_variables()
        return True

    def read_from_dict(self, config_dict):
        if not isinstance(config_dict, dict):
            return TypeError("config_dict should be a dict")

        self.__merge_configs([config_dict])
        self.__insert_environment_variables()
        return True

    def get_path(self, path):
        if not isinstance(path, str):
            raise TypeError("path should be a string")
        if not "." in path:
            return self._storage[path]
        return self.__iterate_over_dict(self._storage, path.split("."))

    def __load_defaults(self):
        try:
            with resource_stream(__name__, "defaults.yaml") as f:
                config = yaml.safe_load(f)
        except IOError as err:
            err.strerror = 'Unable to load default config file'
            raise
        return config

    def __merge_configs(self, configs):
        """ Merges a list of dictionaries into the dictionary of this class. Note that lists are
        overriden completely not extended.
        """
        if not isinstance(configs, list):
            raise TypeError("configs should be a list")

        def extend_dict(target, src):
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
        for var in os.environ:
            if not var.startswith(ENV_VAR_PREFIX) or len(var) == len(ENV_VAR_PREFIX):
                continue
            surround_variables = [n.lower() for n in var[len(ENV_VAR_PREFIX):].split("_") if n]
            self.__override_or_add_var(self._storage, surround_variables, os.getenv(var))

    def __override_or_add_var(self, config, key_list, value):
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
        key = key_list[0] if not key_list == [] else ""
        if key in dictionary:
            if len(key_list) > 1:
                return self.__iterate_over_dict(dictionary[key], key_list[1:])
            return dictionary[key]
        return None

    def __getitem__(self, key):
        return self._storage[key]

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)
