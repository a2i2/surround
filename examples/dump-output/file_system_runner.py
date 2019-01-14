import argparse
import os
from surround import Config, Surround

def is_valid_dir(parser, arg):
    if not os.path.isdir(arg):
        parser.error("Invalid directory %s" % arg)
    else:
        return arg

def is_valid_file(parser, arg):
    if not os.path.isfile(arg):
        parser.error("Invalid file %s" % arg)
    else:
        return arg

class FileSystemRunner():
    def __init__(self, surround, **kwargs):
        assert isinstance(surround, Surround), \
            "surround must be a class or subclass of Surround"
        self.surround = surround

        assert all(isinstance(value, str) for value in kwargs.values()), \
            "Keys should be a string description of that input parameter"

        assert 'description' in kwargs, "Missing description from kwargs"

        self.parser = argparse.ArgumentParser(description=kwargs.get('description'))

        if 'config_file' in kwargs:
            self.parser.add_argument('-c', '--config-file',
                                     required=True, help=kwargs.get('config_file'),
                                     type=lambda x: is_valid_file(self.parser, x))

    def start(self):
        args = self.parser.parse_args()
        if hasattr(args, 'config_file'):
            config = Config()
            config.read_config_files([args.config_file])
            self.surround.set_config(config)
