import os
import json
import shutil
import zipfile
import logging
import datetime

from .util import hash_zip, get_surround_config
from .drivers import get_driver_type_from_url
from .log_stream_handler import LogStreamHandler

DATETIME_FORMAT_STR = "%Y-%m-%dT%H-%M-%S-%f"

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
                    code.zip
                    results.json
                    results.html
                    log.txt
    """

    def __init__(self, storage_url=None, storage_driver=None):
        self.current_experiment = None
        self.prev_experiment = None
        self.storage_url = storage_url

        config = get_surround_config()

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

    def remove_experiment(self, project_name, experiment):
        if self.storage.exists('experimentation/%s/experiments/%s' % (project_name, experiment)):
            self.storage.delete('experimentation/%s/experiments/%s' % (project_name, experiment))

    def push_experiment_file(self, project_name, experiment, path, bytes_data):
        if self.storage.exists('experimentation/%s/experiments/%s' % (project_name, experiment)):
            path = 'experimentation/%s/experiments/%s/%s' % (project_name, experiment, path)
            self.storage.push(path, bytes_data=bytes_data, override_ok=True)

    def start_experiment(self, project_name, project_root, args=None, notes=None):
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
            'time_started': datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
            'model_hash': self.__get_previous_model_hash(project_name),
        }

        # Capture log output and stream to experiment storage
        self.current_experiment['log_file_handler'] = LogStreamHandler(self.storage, self.current_experiment)

        # Update the "last updated time" for the project metadata file
        self.__update_project_meta(project_name)

        # Generate path to the new experiment folder
        path = "experimentation/%s/experiments/%s/" % (project_name, self.current_experiment['time_started'])

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

        global_config = get_surround_config()

        execution_info = {
            'author': {
                'name': global_config.get_path("user.name"),
                'email': global_config.get_path("user.email")
            },
            'arguments': args,
            'model_hash': self.current_experiment['model_hash'],
            'start_time': self.current_experiment['time_started'],
            'notes': notes if notes else [],
            'input_files': self.__get_input_file_structure(project_root)
        }

        # Generate execution info object (in JSON) and push to experiment storage
        self.storage.push(path + "execution_info.json", bytes_data=json.dumps(execution_info, indent=4).encode('utf-8'))

        # Setup logging to go to both the console and file
        root_log = logging.getLogger()
        root_log.setLevel(logging.INFO)
        root_log.addHandler(self.current_experiment['log_file_handler'])

    def stop_experiment(self, metrics=None):
        if not self.current_experiment:
            raise Exception("No experiment has been started!")

        # Stop capturing the logging output
        root_logger = logging.getLogger()
        root_logger.removeHandler(self.current_experiment['log_file_handler'])

        project_root = self.current_experiment['project_root']
        path = "experimentation/%s/experiments/%s/" % (self.current_experiment['project_name'], self.current_experiment['time_started'])

        # Push the logs captured to the experiment folder
        if os.path.exists(os.path.join(project_root, 'log.txt')):
            self.storage.push(path + "log.txt", os.path.join(project_root, 'log.txt'))
        else:
            self.storage.push(path + "log.txt", bytes_data=" ".encode('utf-8'))

        # Update the project metadata file
        self.__update_project_meta(self.current_experiment['project_name'])

        # Push the output of the experiment to the experiment folder and remove locally
        for root, _, files in os.walk(os.path.join(project_root, "output")):
            for f in files:
                self.storage.push(path + "output/" + f, os.path.join(root, f))

        results = {
            'start_time': self.current_experiment['time_started'],
            'end_time': datetime.datetime.now().strftime(DATETIME_FORMAT_STR),
            'metrics': metrics if metrics else {}
        }

        # Generate results object (in JSON) and push to experiment storage
        self.storage.push(path + "results.json", bytes_data=json.dumps(results, indent=4).encode('utf-8'))

        # Upload results.html from output folder (if it exists)
        results_html_path = os.path.join(project_root, "output", "results.html")
        if os.path.exists(results_html_path):
            self.storage.push(path + "results.html", local_path=results_html_path)

        self.prev_experiment = self.current_experiment
        self.current_experiment = None

    def __package_project_code(self, project_root, export_path):
        project_root = os.path.abspath(project_root)
        staging = []
        ignore_dirs = ['models', 'output', 'logs', '__pycache__', 'input']
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

    def __get_input_file_structure(self, project_root):
        project_root = os.path.abspath(project_root)
        results = []
        for root, _, files in os.walk(os.path.join(project_root, "input")):
            for f in files:
                results.append(os.path.relpath(os.path.join(root, f), project_root))

        return results

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
        cache_files = self.storage.get_files(base_url="experimentation/%s/cache" % project_name)

        if cache_files:
            # FORMAT: model-YYYY-MM-DDTHH-MM-SS-MMMMMM-MODEL_HASH_HERE.zip
            dates = [(path[33:-4], path[6:32]) for path in cache_files]
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
