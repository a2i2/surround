import os
import zipfile
from .metadata import Metadata
from .util import hash_file

class DataContainer:
    """
    Represents a data container which holds both data and metadata.
    """

    def __init__(self, path=None):
        self.path = path
        self.metadata = Metadata()
        self.__imported_files = []
        self.__loaded_files = []

        if path:
            self.load(path)

    def load(self, path):
        self.path = path

        # Open the zip file and get all the contents
        with zipfile.ZipFile(path, 'r', compression=zipfile.ZIP_DEFLATED) as container:
            self.__loaded_files = container.namelist()

        # If we have metadata, get the information
        if self.file_exists('manifest.yaml'):
            self.metadata.load_from_data(self.extract_file_bytes('manifest.yaml'))

    def export(self, export_to):
        self.path = export_to

        # Import all the files waiting
        with zipfile.ZipFile(self.path, 'w', compression=zipfile.ZIP_DEFLATED) as container:
            for path, internal_path, data in self.__imported_files:
                if path:
                    container.write(path, internal_path, compress_type=zipfile.ZIP_DEFLATED)
                elif data:
                    container.writestr(internal_path, data, compress_type=zipfile.ZIP_DEFLATED)

        self.__imported_files.clear()

        # Hash the zip file without the metadata
        container_hash = hash_file(self.path)

        with zipfile.ZipFile(self.path, 'a') as container:
            # Set the identifier field to the calculated hash
            self.metadata.set_property("summary.identifier", container_hash)

            # Write the metadata yaml file to the container
            metadata = self.metadata.save_to_data()
            container.writestr('manifest.yaml', metadata)

    def import_directory(self, path):
        # Add them all to a queue for the next export call
        for root, _, files in os.walk(path):
            for name in files:
                filepath = os.path.join(root, name)
                internal_path = os.path.relpath(filepath, start=path)

                self.import_file(filepath, internal_path)

    def import_file(self, import_path, internal_path):
        # Add them to a queue for the next export call
        self.__imported_files.append((import_path, internal_path, None))

    def import_data(self, data, internal_path):
        # Add the data to a queue for the next export call
        self.__imported_files.append((None, internal_path, data))

    def extract_file_bytes(self, path):
        if self.file_exists(path):
            with zipfile.ZipFile(self.path, "r") as container:
                with container.open(path) as myfile:
                    return myfile.read()

        return None

    def extract_file(self, internal_path, extract_path):
        if self.file_exists(internal_path):
            with zipfile.ZipFile(self.path, "r") as container:
                container.extract(internal_path, path=extract_path)
                return True

        return False

    def extract_all(self, extract_to):
        if self.path:
            with zipfile.ZipFile(self.path, 'r') as container:
                container.extractall(extract_to)
                return True
        else:
            print("Unable to extract when no container loaded!")
            return False

    def file_exists(self, path):
        return path in self.__loaded_files

    def get_files(self):
        return self.__loaded_files
