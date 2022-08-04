import os
import zipfile
from .metadata import Metadata
from .util import hash_zip


class MetadataNotFoundError(Exception):
    """
    Thrown when no metadata was found in the data container loaded
    """


class DataContainer:
    """
    Represents a data container which holds both data and metadata.

    Responsibilities:

    - Import files into a container and export
    - Load existing containers
    - Extract files
    """

    def __init__(self, path=None, metadata_version="v0.1"):
        """
        :param path: path for container to load (default: None)
        :type path: str
        :param metadata_version: the version of metadata being used (default: v0.1)
        :type metadata_version: str
        """

        self.path = path
        self.metadata = Metadata(metadata_version)
        self.__imported_files = []
        self.__loaded_files = []

        if path:
            self.load(path)

    def load(self, path):
        """
        Load an existing data container, preparing it for extracting files.

        :param path: path to the container
        :type path: str
        """

        self.path = path

        # Open the zip file and get all the contents
        with zipfile.ZipFile(path, "r", compression=zipfile.ZIP_DEFLATED) as container:
            self.__loaded_files = container.namelist()

        # If we have metadata, get the information, otherwise throw an exception
        if self.file_exists("manifest.yaml"):
            self.metadata.load_from_data(self.extract_file_bytes("manifest.yaml"))
        else:
            self.__loaded_files = []
            raise MetadataNotFoundError

    def export(self, export_to):
        """
        Import all staged files into the container, hash the contents, set the hash to the
        metadata and import the metadata file.

        :param export_to: path to export the file to
        :type export_to: str
        """

        self.path = export_to
        self.__loaded_files.clear()

        # Import all the files waiting
        with zipfile.ZipFile(
            self.path, "w", compression=zipfile.ZIP_DEFLATED
        ) as container:
            for path, internal_path, data in self.__imported_files:
                if path:
                    container.write(
                        path, internal_path, compress_type=zipfile.ZIP_DEFLATED
                    )
                elif data:
                    container.writestr(
                        internal_path, data, compress_type=zipfile.ZIP_DEFLATED
                    )

                self.__loaded_files.append(internal_path)

        self.__imported_files.clear()

        # Hash the zip file without the metadata
        container_hash = hash_zip(self.path)

        with zipfile.ZipFile(self.path, "a") as container:
            # Set the identifier field to the calculated hash
            self.metadata.set_property("summary.identifier", container_hash)

            # Write the metadata yaml file to the container
            metadata = self.metadata.save_to_data()
            container.writestr("manifest.yaml", metadata)

    def import_files(self, files, generate_metadata=True):
        """
        Stage the list of files for importing when export is requested.

        :param files: list of files to import
        :type files: list
        :param generate_metadata: whether metadata should be generated for this file
        :type generate_metadata: bool
        """

        for path, internal_path in files:
            self.import_file(path, internal_path, generate_metadata)

    def import_directory(self, path, generate_metadata=True, reimport=True):
        """
        Stage the directory provided for importing when export is requested.

        :param path: the directory of files to import
        :type path: str
        :param generate_metadata: whether metadata should be generated for this folder
        :type generate_metadata: bool
        :param reimport: whether or not files that are already staged should be staged again
        :type reimport: bool
        """

        if generate_metadata:
            # Generate the automatic fields in the metadata using the directory
            self.metadata.generate_from_directory(path)

        if not os.path.exists(path):
            raise FileNotFoundError

        # Add them all to a queue for the next export call
        for root, _, files in os.walk(path):
            for name in files:
                filepath = os.path.join(root, name)
                internal_path = os.path.relpath(filepath, start=path)

                # If requested, don't reimport already imported files
                if not reimport and any(
                    [f[0] == filepath for f in self.__imported_files]
                ):
                    continue

                self.import_file(filepath, internal_path, False)

    def import_file(self, import_path, internal_path, generate_metadata=True):
        """
        Stage file for importing when the next export operation is called.

        :param import_path: path to the file on the users drive
        :type import_path: str
        :param internal_path: path to the file inside the container
        :type internal_path: str
        :param generate_metadata: whether metadata should be generated for this file
        :type generate_metadata: bool
        """

        if generate_metadata:
            # Generate the automatic fields in the metadata using the file
            self.metadata.generate_from_file(import_path)

        # Add them to a queue for the next export call
        self.__imported_files.append(
            (import_path, internal_path.replace("\\", "/"), None)
        )

    def import_data(self, data, internal_path, generate_metadata=True):
        if generate_metadata:
            # Generate the automatic fields in the metadata using the extension
            self.metadata.generate_from_file(internal_path)

        # Add the data to a queue for the next export call
        self.__imported_files.append((None, internal_path.replace("\\", "/"), data))

    def extract_file_bytes(self, path):
        """
        Extract the bytes of a file in the current data container

        :param path: path inside the container
        :type path: str
        :returns: the bytes extracted or None if it doesn't exist
        :rtype: bytes
        """

        if self.file_exists(path):
            with zipfile.ZipFile(self.path, "r") as container:
                with container.open(path) as myfile:
                    return myfile.read()

        return None

    def extract_file(self, internal_path, extract_path="."):
        """
        Extract a file in the current data container to a path on disk

        :param internal_path: path inside the container
        :type internal_path: str
        :param extract_path: path to extract file to
        :returns: true on success, false otherwise
        :rtype: bool
        """

        if self.file_exists(internal_path):
            with zipfile.ZipFile(self.path, "r") as container:
                container.extract(internal_path, path=extract_path)
                return True

        return False

    def extract_files(self, internal_paths, extract_path="."):
        """
        Extract files in the current data container to a path on disk

        :param internal_paths: list of files to extract
        :type internal_paths: list
        :param extract_path: path to extract files to
        :type extract_path: str
        :returns: true on success, false otherwise
        :rtype: bool
        """

        result = True
        for internal_path in internal_paths:
            result = result and self.extract_file(internal_path, extract_path)

        return result

    def extract_all(self, extract_to):
        """
        Extract all files in the current data container to a path on disk

        :param extract_to: path to extract files to
        :type extract_to: str
        :returns: true on success, false otherwise
        :rtype: bool
        """

        if self.path:
            with zipfile.ZipFile(self.path, "r") as container:
                container.extractall(extract_to)
                return True
        else:
            print("Unable to extract when no container loaded!")
            return False

    def file_exists(self, path):
        """
        Checks whether file exists in current data container

        :returns: true if the file exists
        :rtype: bool
        """

        return path in self.__loaded_files

    def get_files(self):
        """
        Returns all the files in the current data container

        :returns: list of the files
        :rtype: list
        """

        return self.__loaded_files
