from abc import abstractmethod
import argparse
import os
from .config import Config
from .pipeline import Pipeline

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


class FileSystemAdapter():

    def __init__(self, pipeline, **kwargs):
        assert isinstance(pipeline, Pipeline), \
            "pipeline must be a class or subclass of Pipeline"
        self.pipeline = pipeline

        assert all(isinstance(value, str) for value in kwargs.values()), \
            "Keys should be a string description of that input parameter"

        assert 'description' in kwargs, "Missing description from kwargs"

        self.parser = argparse.ArgumentParser(description=kwargs.get('description'))

        if 'output_dir' in kwargs:
            self.parser.add_argument('-o', '--output-dir', required=True, help=kwargs.get('output_dir'),
                                     type=lambda x: is_valid_dir(self.parser, x))

        if 'input_dir' in kwargs:
            self.parser.add_argument('-i', '--input-dir', required=True, help=kwargs.get('input_dir'),
                                     type=lambda x: is_valid_dir(self.parser, x))

        if 'file0' in kwargs:
            self.parser.add_argument('-f0', '--file0', required=True, help=kwargs.get('file0'),
                                     type=lambda x: is_valid_file(self.parser, x))

        if 'file1' in kwargs:
            self.parser.add_argument('-f1', '--file1', required=True, help=kwargs.get('file1'),
                                     type=lambda x: is_valid_file(self.parser, x))

        if 'file2' in kwargs:
            self.parser.add_argument('-f2', '--file2', required=True, help=kwargs.get('file2'),
                                     type=lambda x: is_valid_file(self.parser, x))

        if 'config_file' in kwargs:
            self.parser.add_argument('-c', '--config-file', required=True, help=kwargs.get('config_file'),
                                     type=lambda x: is_valid_file(self.parser, x))


    @abstractmethod
    def transform(self, input_data):
        pass

    def start(self):
        args = self.parser.parse_args()
        if hasattr(args, 'config_file'):
            config = Config()
            config.read_config_files([args.config_file])
            self.pipeline.set_config(config)
        self.transform(args)
