from collections.abc import Mapping

import os
import json
import yaml

from .util import (
    get_formats_from_directory,
    get_formats_from_files,
    get_types_from_formats,
)


class Metadata(Mapping):
    """
    Represents metadata of a Data Container.

    Responsibilities:

    - Create metadata, explorting to YAML string and/or file
    - Generate default metadata as per schema
    - Automatically generate values to fields based on files given
    - Get/set properties
    """

    # 'key_name': (TYPE, REQUIRED, SUB_SCHEMA)
    SCHEMA = {
        "v0.1": {
            "version": (str, True, None),
            "summary": (
                dict,
                True,
                {
                    "title": (str, True, None),
                    "creator": (str, True, None),
                    "subject": (list, True, None),
                    "description": (str, True, None),
                    "publisher": (str, True, None),
                    "contributor": (str, True, None),
                    "date": (str, True, None),
                    "types": (list, True, None),
                    "formats": (list, True, None),
                    "identifier": (str, True, None),
                    "source": (str, False, None),
                    "language": (str, True, None),
                    "rights": (str, True, None),
                    "under-ethics": (bool, True, None),
                },
            ),
            "manifests": (
                list,
                False,
                {
                    "path": (str, True, None),
                    "description": (str, True, None),
                    "types": (list, True, None),
                    "formats": (list, True, None),
                    "language": (str, True, None),
                },
            ),
        }
    }

    def __init__(self, version="v0.1"):
        """
        :param version: the version of the schema to use (default: v0.1)
        :type version: str
        """

        self.version = version
        self.__storage = self.generate_default(version)

    def generate_default(self, version):
        """
        Generate a dictionary with all required fields created as per the schema.

        :param version: which version of the schema to use
        :type version: str
        :returns: the dictionary with default values
        :rtype: dict
        """

        def gen_dict(schema):
            result = {}

            for key, value in schema.items():
                typ = value[0]
                required = value[1]
                sub_schema = value[2]

                if required and typ is dict:
                    result[key] = gen_dict(sub_schema)
                elif key == "version":
                    result[key] = version
                elif required:
                    result[key] = typ()

            return result

        return gen_dict(self.SCHEMA[version])

    def generate_from_files(self, files, root, root_level_dirs):
        """
        Automatically generate metadata from a list of files such as:

        - Formats (mime types)
        - Types (types from vocab)
        - Group manifests (each root level directory is considered a group)

        :param files: list of files to generate from
        :type files: list
        :param root: path to the root of the folder container the files
        :type root: str
        :param root_level_dirs: list of directories in the root
        :type root_level_dirs: list
        """

        formats = get_formats_from_files(files)
        types = get_types_from_formats(formats)

        if root_level_dirs:
            types.append("Collection")

        self.__storage["summary"]["formats"] = formats
        self.__storage["summary"]["types"] = types

        if root_level_dirs:
            self.__storage["manifests"] = []

            for root_dir in root_level_dirs:
                formats = get_formats_from_directory(os.path.join(root, root_dir))
                types = get_types_from_formats(formats)

                if "Collection" not in types:
                    types.append("Collection")

                self.__storage["manifests"].append(
                    {
                        "path": root_dir,
                        "description": None,
                        "formats": formats,
                        "types": types,
                        "language": None,
                    }
                )

    def generate_from_directory(self, directory):
        """
        Automatically generate metadata from a directory, such as:

        - Formats (mime types)
        - Types (types from vocab)
        - Group manifests (each root level directory is considered a group)

        :param directory: path to the directory to generate from
        :type directory: str
        """

        root_level_dirs = []
        all_files = []

        for root, dirs, files in os.walk(directory):
            for name in files:
                all_files.append(os.path.join(root, name))

            if os.path.abspath(root) == os.path.abspath(directory):
                root_level_dirs.extend(dirs)

        self.generate_from_files(all_files, directory, root_level_dirs)

    def generate_from_file(self, filepath):
        """
        Automatically generate metadata from a single file

        :param filepath: path to the file
        :type filepath: str
        """

        formats = get_formats_from_files([filepath])
        types = get_types_from_formats(formats)

        self.__storage["summary"]["formats"] = formats
        self.__storage["summary"]["types"] = types

    def generate_manifest_for_group(self, group_name, files, formats=None):
        """
        Generate a manifest for a group of files where the manifest contains:

        - path
        - description
        - language
        - formats (mime types)
        - types (from vocab)

        Store the manifest in the metadata storage plus return it.

        :param group_name: name of the group
        :type group_name: str
        :param files: list of files in the group
        :type files: list
        :param formats: list of formats in the group
        :type formats: list
        :returns: the manifest created
        :rtype: dict
        """

        if not formats:
            formats = []

        formats.extend(get_formats_from_files(files))
        types = get_types_from_formats(formats)

        # Add collection to types if more than one file or format
        if "Collection" not in types and (
            len(files) > 1 or (formats and len(formats) > 1)
        ):
            types.append("Collection")

        if "manifests" not in self.__storage:
            self.__storage["manifests"] = []

        manifest = {
            "path": group_name,
            "description": None,
            "language": None,
            "formats": formats,
            "types": types,
        }

        self.__storage["manifests"].append(manifest)

        return manifest

    def load_from_path(self, path):
        """
        Load metadata from file (YAML)

        :param path: path to the YAML file
        :type path: str
        """

        with open(path, "r") as yaml_file:
            self.__storage = yaml.safe_load(yaml_file.read())

    def load_from_data(self, data):
        """
        Load metadata from a YAML string

        :param data: YAML string
        :type data: str
        """

        self.__storage = yaml.safe_load(data)

    def save_to_path(self, path):
        """
        Save metadata to YAML file

        :param path: path to save file to
        :type path: str
        """

        with open(path, "w+") as yaml_file:
            yaml.dump(self.__storage, yaml_file)

    def save_to_data(self):
        """
        Returns metadata as string formatted in YAML

        :returns: the data in YAML string
        :rtype: str
        """

        return yaml.dump(self.__storage)

    def save_to_json(self, indent=4):
        """
        Returns metadata as string formatted in JSON

        :param indent: number of spaces in indentations
        :type indent: int
        :returns: the data in JSON format
        :rtype: str
        """

        return json.dumps(self.__storage, indent=indent)

    def save_to_json_file(self, path, indent=4):
        """
        Saves metadata to JSON file

        :param path: path to file to export to
        :type path: str
        :param indent: number of spaces in indentations
        :type indent: int
        """

        with open(path, "w+") as f:
            json.dump(self.__storage, f, indent=indent)

    def get_property(self, path):
        """
        Get the value of a property given a path in dot notation e.g. summary.title

        ``metadata.get_property('summary.title')`` would retrieve ``Test name`` from the following::

            summary:
                title: Test name

        :param path: path to the property using dot notation
        :type path: str
        :returns: the value of the property, none otherwise
        :rtype: any
        """

        keys = path.split(".")

        def traverse_dict(keys, container):
            key = keys[0]

            if key in container:
                if len(keys) > 1 and isinstance(container[key], dict):
                    return traverse_dict(keys[1:], container[key])

                return container[key]

            return None

        return traverse_dict(keys, self.__storage)

    def set_property(self, path, value):
        """
        Set the value of a property given a path in dot notation e.g. summary.title

        ``metadata.set_property('summary.title')`` would set the title of the data container.

        :param path: path to the property in dot notation
        :type path: str
        :param value: value to set to the property
        :type value: any
        """

        keys = path.split(".")

        def update_dict(keys, collection, value):
            key = keys[0]

            if len(keys) > 1 and isinstance(collection[key], dict):
                collection[key] = update_dict(keys[1:], collection[key], value)
            else:
                collection[key] = value

            return collection

        self.__storage = update_dict(keys, self.__storage, value)

    def __getitem__(self, key):
        return self.__storage[key]

    def __iter__(self):
        return iter(self.__storage)

    def __len__(self):
        return len(self.__storage)
