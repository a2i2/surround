import os
import json
import shutil
import zipfile
import logging
import datetime
from pathlib import Path

import tornado.template
from .util import hash_zip, get_driver_type_from_url
from .log_stream_handler import LogStreamHandler
from ..config import Config
from ..configuration import cli as config_cli

DATETIME_FORMAT_STR = "%Y-%m-%dT%H-%M-%S-%f"

def get_config():
    config = Config(auto_load=False)
    local_config = Config(auto_load=True)

    global_config_path = os.path.join(Path.home(), ".surround", "config.yaml")
    local_config_path = os.path.join(local_config["project_root"], ".surround", "config.yaml")

    global_exists = os.path.exists(global_config_path)
    local_exists = os.path.exists(local_config_path)

    # Load the configuration file from the global surround path
    if global_exists:
        config.read_config_files([global_config_path])

    # Load the configuration file from the project surround path
    if local_exists:
        config.read_config_files([local_config_path])

    # If neither exist or we don't have the required property, setup the configuration
    if not global_exists and (not local_exists or not config.get_path("experiment.url")):
        logger = logging.getLogger(__name__)
        logger.info("Setting up global configuration...")
        logger.info("No username or email have been set in your configuration!")
        logger.info("To set your name and email use the following commands:")
        logger.info("$ surround config user.name John Doe")
        logger.info("$ surround config user.email john.doe@email.com\n")

        config_cli.update_required_fields(config, global_config_path, answers={
            'user.name': 'Unknown',
            'user.email': 'Unknown'
        }, verbose=False)

    return config

class ExperimentWriter:
    """
    Experiment Storage Structure:
    experimentation/
        project_name/
            project.json
            experiments/
                YYYY-MM-DDThh-mm-ss-mmmm/
                    logs/
                        ...
                    output/
                        ...
                    metrics/
                        ...
                    status.txt
                    code.zip
                    results.json
                    results.html
                    log.txt
    """

    def __init__(self, storage_url=None, storage_driver=None):
        self.current_experiment = None
        self.prev_experiment = None
        self.storage_url = storage_url

        config = get_config()

        if not self.storage_url:
            self.storage_url = config.get_path("experiment.url")

        if not self.storage_url or not isinstance(self.storage_url, str):
            raise ValueError("No valid storage URL has been provided!")

        if not storage_driver:
            storage_driver = get_driver_type_from_url(self.storage_url)

        if not storage_driver or not isinstance(storage_driver, type):
            raise ValueError("No valid storage driver has been provided!")

        self.storage = storage_driver(self.storage_url)

    def write_project(self, project_name, project_description):
        metadata = {
            'project_name': project_name,
            'project_description': project_description,
            'last_time_updated': datetime.datetime.now().isoformat()
        }

        metadata = json.dumps(metadata, indent=4)
        metadata = metadata.encode(encoding='utf-8')
        self.storage.push('experimentation/%s/project.json' % project_name, bytes_data=metadata, override_ok=True)

    def remove_project(self, project_name):
        if self.storage.exists('experimentation/' + project_name):
            self.storage.delete('experimentation/' + project_name)

    def start_experiment(self, project_name, project_root, args=None):
        if self.current_experiment:
            raise Exception("There is already an experiment in progress!")

        if not self.storage.exists("experimentation/%s/project.json" % project_name):
            raise Exception("This project doesn't exist in the experiment storage!")

        # Clean up the logs (from any previous experiments)
        if os.path.exists(os.path.join(project_root, "log.txt")):
            os.remove(os.path.join(project_root, "log.txt"))

        # Clean up the output (from any previous experiments)
        if os.path.exists(os.path.join(project_root, "output")) and os.listdir(os.path.join(project_root, "output")):
            shutil.rmtree(os.path.join(project_root, "output"))
            os.mkdir(os.path.join(project_root, "output"))

        self.current_experiment = {
            'project_name': project_name,
            'project_root': project_root,
            'args': args,
            'time_started': datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
            'model_hash': self.__get_previous_model_hash(project_name),
            'metrics': {}
        }

        # Capture log output and stream to experiment storage
        self.current_experiment['log_file_handler'] = LogStreamHandler(self.storage, self.current_experiment)

        path = "experimentation/%s/experiments/%s/" % (project_name, self.current_experiment['time_started'])

        # Write status file to experiment folder & update the projects metadata file
        self.storage.push(path + "status.txt", bytes_data="RUNNING".encode('utf-8'))
        self.__update_project_meta(project_name)

        os.makedirs('temp')
        try:
            # Upload the code used for this experiment
            self.__package_project_code(project_root, "temp/temp.zip")
            self.storage.push(path + "code.zip", "temp/temp.zip")

            model_hash = self.__package_model(project_root, "temp/models.zip")
            if model_hash:
                # If the model in the previous experiment is different to this then upload the new model
                if self.current_experiment['model_hash'] != model_hash:
                    self.current_experiment['model_hash'] = model_hash
                    self.storage.push("experimentation/%s/cache/model-%s-%s.zip" % (project_name, self.current_experiment['time_started'], model_hash), "temp/models.zip")
            else:
                self.current_experiment['model_hash'] = None
        finally:
            shutil.rmtree('temp')

        # Setup logging to go to both the console and file
        root_log = logging.getLogger()
        root_log.setLevel(logging.DEBUG)
        root_log.addHandler(self.current_experiment['log_file_handler'])

    def write_metric(self, key, value):
        if not self.current_experiment:
            raise Exception("No experiment is in progress!")

        metrics_path = "experimentation/%s/experiments/%s/metrics/%s/" % (
            self.current_experiment['project_name'],
            self.current_experiment['time_started'],
            key
        )

        timestamp = datetime.datetime.now().strftime(DATETIME_FORMAT_STR)

        if key in self.current_experiment['metrics']:
            # If not a list, make a list since multiple values are being written
            if not isinstance(self.current_experiment['metrics'][key], list):
                self.current_experiment['metrics'][key] = [self.current_experiment['metrics'][key]]

            # Append new value to list and push to new file in experiment storage
            self.storage.push(
                metrics_path + "%s_%i.txt" % (timestamp, len(self.current_experiment['metrics'][key])),
                bytes_data=str(value).encode('utf-8'))
            self.current_experiment['metrics'][key].append(value)
        else:
            # First time writing this metric, consider single value and write to file in storage
            self.current_experiment['metrics'][key] = value
            self.storage.push(metrics_path + "%s_0.txt" % timestamp, bytes_data=str(value).encode('utf-8'))

    def stop_experiment(self, metrics=None, notes=None):
        if not self.current_experiment:
            raise Exception("No experiment has been started!")

        # Stop capturing the logging output
        root_logger = logging.getLogger()
        root_logger.removeHandler(self.current_experiment['log_file_handler'])

        project_root = self.current_experiment['project_root']
        path = "experimentation/%s/experiments/%s/" % (self.current_experiment['project_name'], self.current_experiment['time_started'])

        # Push the logs captured to the experiment folder and delete locally
        self.storage.push(path + "log.txt", os.path.join(project_root, 'log.txt'))

        # Update the status of the experiment to COMPLETE
        self.storage.push(path + "status.txt", bytes_data="COMPLETE".encode('utf-8'), override_ok=True)

        # Update the project metadata file
        self.__update_project_meta(self.current_experiment['project_name'])

        # Push the output of the experiment to the experiment folder and remove locally
        for root, _, files in os.walk(os.path.join(project_root, "output")):
            for f in files:
                self.storage.push(path + "output/" + f, os.path.join(root, f))

        if metrics:
            metrics.update(self.current_experiment['metrics'])
        else:
            metrics = self.current_experiment['metrics']

        global_config = get_config()

        results = {
            'author': {
                'name': global_config.get_path("user.name"),
                'email': global_config.get_path("user.email")
            },
            'arguments': self.current_experiment['args'],
            'start_time': self.current_experiment['time_started'],
            'end_time': datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
            'metrics': metrics if metrics else {},
            'notes': notes if notes else [],
            'model_hash': self.current_experiment['model_hash']
        }

        # Generate results object (in JSON) and push to experiment storage
        self.storage.push(path + "results.json", bytes_data=json.dumps(results, indent=4).encode('utf-8'))

        # Generate HTML page visualising the results (if templates available)
        if os.path.exists(os.path.join(project_root, "templates/")):
            try:
                results_html = tornado.template.Loader(os.path.join(project_root, "templates/"))
                results_html = results_html.load("results.html")
                results_html = results_html.generate(results=results)

                self.storage.push(path + "results.html", bytes_data=results_html)
            except Exception:
                logging.exception("Failed to generate the result HTML file for the experiment:")

        self.prev_experiment = self.current_experiment
        self.current_experiment = None

    def __package_project_code(self, project_root, export_path):
        project_root = os.path.abspath(project_root)
        staging = []
        ignore_dirs = ['models', 'output', 'logs', '__pycache__']
        ignore_files = ['log.txt', '.doit.db.bak', '.doit.db.dat', '.doit.db.dir']

        for root, _, files in os.walk(project_root):
            if os.path.basename(root) in ignore_dirs:
                continue

            for f in files:
                if f in ignore_files:
                    continue

                staging.append(os.path.join(root, f))

        # Package code into zip folder called code.zip and upload
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as f:
            for source_file in staging:
                f.write(source_file, os.path.relpath(source_file, project_root))

    def __package_model(self, project_root, export_path):
        project_root = os.path.abspath(project_root)
        models_path = os.path.join(project_root, "models")

        if not os.path.exists(models_path):
            raise Exception("Cannot package models folder for experiment since it doesn't exist!")

        if not os.listdir(models_path):
            return None

        with zipfile.ZipFile(export_path, "w", zipfile.ZIP_DEFLATED) as package:
            for root, _, files in os.walk(models_path):
                for f in files:
                    file_path = os.path.join(root, f)
                    package.write(file_path, os.path.relpath(file_path, project_root))

        return hash_zip(export_path)

    def __get_previous_model_hash(self, project_name):
        remote_files = self.storage.get_files()
        cache_files = [path for path in remote_files if os.path.basename(os.path.dirname(path)) == "cache" and os.path.splitext(path)[1] == ".zip" and project_name in path]

        if cache_files:
            # FORMAT: .../cache/models-YYYY-MM-DDTHH-MM-HH-MODEL_HASH_HERE.zip
            dates = [(os.path.basename(path)[26:-4], os.path.basename(path)[6:25]) for path in cache_files]
            dates = [(hash_str, datetime.datetime.strptime(time_str, DATETIME_FORMAT_STR)) for hash_str, time_str in dates]

            last_model_hash, _ = max(dates, key=lambda x: x[1])

            return last_model_hash

        return None

    def __update_project_meta(self, project_name):
        if self.storage.exists("experimentation/%s/project.json" % project_name):
            # Update the "last updated time" property to now
            project_meta = self.storage.pull("experimentation/%s/project.json" % project_name)
            project_meta = json.loads(project_meta.decode('utf-8'))
            project_meta['last_time_updated'] = datetime.datetime.now().isoformat()
            self.storage.push(
                "experimentation/%s/project.json" % project_name,
                bytes_data=json.dumps(project_meta, indent=4).encode('utf-8'),
                override_ok=True)
