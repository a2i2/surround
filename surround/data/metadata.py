from collections.abc import Mapping

import os
import json
import yaml

from .util import get_formats_from_directory, get_formats_from_files, get_types_from_formats

class Metadata(Mapping):
    """
    Represents metadata of a Data Container.
    """

    # (TYPE, REQUIRED, SUB_SCHEMA)
    SCHEMA = {
        'v0.1': {
            'version': (str, True, None),
            'summary': (dict, True, {
                'title': (str, True, None),
                'creator': (str, True, None),
                'subject': (list, True, None),
                'description': (str, True, None),
                'publisher': (str, True, None),
                'contributor': (str, True, None),
                'date': (str, True, None),
                'types': (list, True, None),
                'formats': (list, True, None),
                'identifier': (str, True, None),
                'source': (str, False, None),
                'language': (str, True, None),
                'rights': (str, True, None),
                'under-ethics': (bool, True, None),
            }),
            'manifests': (list, False, {
                'path': (str, True, None),
                'description': (str, True, None),
                'types': (list, True, None),
                'formats': (list, True, None),
                'language': (str, True, None),
            })
        }
    }

    def __init__(self, version='v0.1'):
        self.version = version
        self.__storage = self.generate_default(version)

    def generate_default(self, version):
        def gen_dict(schema):
            result = {}

            for key, value in schema.items():
                typ = value[0]
                required = value[1]
                sub_schema = value[2]

                if required and typ is dict:
                    result[key] = gen_dict(sub_schema)
                elif key == 'version':
                    result[key] = version
                elif required:
                    result[key] = typ()

            return result

        return gen_dict(self.SCHEMA[version])

    def generate_from_files(self, files, root, root_level_dirs):
        formats = get_formats_from_files(files)
        types = get_types_from_formats(formats)

        if root_level_dirs:
            types.append("Collection")

        self.__storage['summary']['formats'] = formats
        self.__storage['summary']['types'] = types

        if root_level_dirs:
            self.__storage['manifests'] = []

            for root_dir in root_level_dirs:
                formats = get_formats_from_directory(os.path.join(root, root_dir))
                types = get_types_from_formats(formats)

                if 'Collection' not in types:
                    types.append('Collection')

                self.__storage['manifests'].append({
                    'path': root_dir,
                    'description': None,
                    'formats': formats,
                    'types': types,
                    'language': None,
                })

    def generate_from_directory(self, directory):
        root_level_dirs = []
        all_files = []

        for root, dirs, files in os.walk(directory):
            for name in files:
                all_files.append(os.path.join(root, name))

            if os.path.abspath(root) == os.path.abspath(directory):
                root_level_dirs.extend(dirs)

        self.generate_from_files(all_files, directory, root_level_dirs)

    def generate_from_file(self, filepath):
        formats = get_formats_from_files([filepath])
        types = get_types_from_formats(formats)

        self.__storage['summary']['formats'] = formats
        self.__storage['summary']['types'] = types

    def load_from_path(self, path):
        with open(path, "r") as yaml_file:
            self.__storage = yaml.safe_load(yaml_file.read())

    def load_from_data(self, data):
        self.__storage = yaml.safe_load(data)

    def save_to_path(self, path):
        with open(path, "w+") as yaml_file:
            yaml.dump(self.__storage, yaml_file)

    def save_to_data(self):
        return yaml.dump(self.__storage)

    def save_to_json(self, indent=4):
        return json.dumps(self.__storage, indent=indent)

    def save_to_json_file(self, path, indent=4):
        with open(path, "w+") as f:
            json.dump(self.__storage, f, indent=indent)

    def validate(self):
        raise NotImplementedError

    def get_property(self, path):
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
