from collections.abc import Mapping

import os
import yaml

from .util import get_formats_from_directory, get_formats_from_files, get_types_from_formats, hash_file

class Metadata(Mapping):
    """
    Represents metadata of a Data Container.
    """

    REQUIRED_FIELDS = {
        'v0.1': {
            'version': True,
            'summary': {
                'title': True,
                'creator': True,
                'subject': True,
                'description': True,
                'publisher': True,
                'contributor': True,
                'date': True,
                'types': True,
                'formats': True,
                'identifier': True,
                'source': False,
                'language': True,
                'rights': True,
                'under-ethics': True,
            },
            'manifests': {
                'path': True,
                'description': True,
                'types': True,
                'formats': True,
                'language': True,
            }
        }
    }

    def __init__(self, version='v0.1'):
        self.version = version
        self.__storage = {
            'version': version,
        }

    def generate_from_files(self, files, root_level_dirs):
        formats = get_formats_from_files(files)
        types = get_types_from_formats(formats)

        if root_level_dirs:
            types.append("Collection")

        self.__storage['summary'] = {
            'title': None,
            'creator': None,
            'subject': None,
            'description': None,
            'publisher': None,
            'contributor': None,
            'date': None,
            'types': types,
            'formats': formats,
            'identifier': None,
            'source': None,
            'language': None,
            'rights': None,
            'under-ethics': None,
        }

        if root_level_dirs:
            self.__storage['manifests'] = []
            for root_dir in root_level_dirs:
                formats = get_formats_from_directory(root_dir)
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

        self.generate_from_files(all_files, root_level_dirs)

    def generate_from_file(self, filepath):
        formats = get_formats_from_files([filepath])
        types = get_types_from_formats(formats)
        self.__storage['summary'] = {
            'title': None,
            'creator': None,
            'subject': None,
            'description': None,
            'publisher': None,
            'contributor': None,
            'date': None,
            'types': types,
            'formats': formats,
            'identifier': hash_file(filepath),
            'source': None,
            'language': None,
            'rights': None,
            'under-ethics': None
        }

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
