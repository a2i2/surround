import re
import os
import json
import zipfile
from io import BytesIO
from .util import get_surround_config
from .drivers import get_driver_type_from_url

class ExperimentReader:
    """
    Experiment Storage Structure:
    experimentation/
        project_name/
            project.json
            experiments/
                YYYY-MM-DDThh-mm-ss-mmmm/
                    output/
                        ...
                    code.zip
                    results.json
                    results.html
                    log.txt
    """

    def __init__(self, storage_url=None, storage_driver=None):
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

    def get_projects(self):
        project_folders = self.storage.get_files(base_url="experimentation")
        project_folders = [f for f in project_folders if re.match(r"^[a-z_]+[/\\]{1,2}project.json$", f)]

        results = []
        for project_folder in project_folders:
            project_meta = self.storage.pull("experimentation/" + project_folder)
            project_meta = json.loads(project_meta.decode("utf-8"))
            results.append(project_meta)

        return results

    def has_project(self, project_name):
        return self.storage.exists("experimentation/%s/project.json" % project_name)

    def get_project(self, project_name):
        if not self.has_project(project_name):
            return None

        project_meta = self.storage.pull("experimentation/%s/project.json" % project_name)
        project_meta = json.loads(project_meta.decode('utf-8'))

        return project_meta

    def get_experiments(self, project_name):
        results = []
        path = "experimentation/%s/experiments/" % project_name
        experiment_files = self.storage.get_files(base_url=path)

        if experiment_files:
            execution_files = [f for f in experiment_files if re.match(r"^[T0-9\-]+[/\\]{1,2}execution_info.json$", f)]

            execution_infos = []
            for exec_file in execution_files:
                info_obj = self.storage.pull(path + exec_file).decode('utf-8')
                info_obj = json.loads(info_obj)
                execution_infos.append(info_obj)

            for execution_info in execution_infos:
                try:
                    result_obj = self.storage.pull(path + execution_info["start_time"] + "/results.json")
                    result_obj = json.loads(result_obj.decode('utf-8'))
                except FileNotFoundError:
                    result_obj = None

                try:
                    log = self.storage.pull(path + execution_info["start_time"] + "/log.txt").decode('utf-8')
                except FileNotFoundError:
                    log = []

                results.append({
                    'execution_info': execution_info,
                    'logs': [l.rstrip() for l in log.split("\n")] if log else [],
                    'results': result_obj
                })

        return results

    def has_experiment(self, project_name, experiment_date):
        return self.storage.exists("experimentation/%s/experiments/%s" % (project_name, experiment_date))

    def get_experiment(self, project_name, experiment_date):
        if not self.has_experiment(project_name, experiment_date):
            return None

        path = "experimentation/%s/experiments/%s/" % (project_name, experiment_date)
        execution_info = self.storage.pull(path + "execution_info.json").decode('utf-8')
        execution_info = json.loads(execution_info)

        if self.storage.exists(path + "log.txt"):
            logs = self.storage.pull(path + "log.txt").decode('utf-8')
            logs = [l.rstrip() for l in logs.rstrip().split("\n")]
        else:
            logs = []

        if self.storage.exists(path + "results.json"):
            results = self.storage.pull(path + "results.json").decode('utf-8')
            results = json.loads(results)
        else:
            results = None

        return {
            'execution_info': execution_info,
            'logs': logs,
            'results': results
        }

    def get_experiment_files(self, project_name, experiment_date, base_url=None):
        if not self.has_experiment(project_name, experiment_date):
            return None

        url = "experimentation/%s/experiments/%s" % (project_name, experiment_date)

        if base_url:
            url = "%s/%s" % (url, base_url)

        return self.storage.get_files(base_url=url)

    def get_project_cache(self, project_name):
        if not self.storage.exists("experimentation/%s/cache" % project_name):
            return None

        return self.storage.get_files(base_url="experimentation/%s/cache" % project_name)

    def pull_experiment_file(self, project_name, experiment_date, path):
        path = "experimentation/%s/experiments/%s/%s" % (project_name, experiment_date, path)

        try:
            return self.storage.pull(path)
        except FileNotFoundError:
            return None

    def pull_cache_file(self, project_name, path):
        path = "experimentation/%s/cache/%s" % (project_name, path)
        if not self.storage.exists(path):
            return None

        return self.storage.pull(path)

    def pull_model(self, project_name, model_hash):
        if not self.has_project(project_name):
            return None

        files = self.storage.get_files(base_url="experimentation/%s/cache" % project_name)
        for f in files:
            if re.match(r"^model.+" + model_hash + r"\.zip$", f):
                return self.pull_cache_file(project_name, f)

        return None

    def replicate(self, project_name, experiment_date, file_path=None, zip_path=None, include_output=False):
        path = "experimentation/%s/experiments/%s" % (project_name, experiment_date)

        if not self.storage.exists(path):
            return None

        if file_path and zip_path:
            raise ValueError("cannot specify both a zip and file export path")

        if file_path:
            return self.__replicate_file(project_name, experiment_date, path, file_path, include_output)

        return self.__replicate_zip(project_name, experiment_date, zip_path, include_output)

    def __replicate_file(self, project_name, experiment_date, experiment_path, export_path, include_output):
        # Export the code package
        self.storage.pull(experiment_path + "/code.zip", local_path=os.path.join(export_path, "code.zip"))
        with zipfile.ZipFile(os.path.join(export_path, "code.zip"), "r") as f:
            for code_file in f.namelist():
                # Create any sub-directories
                os.makedirs(os.path.join(export_path, os.path.dirname(code_file)), exist_ok=True)

                with open(os.path.join(export_path, code_file), "wb+") as cf:
                    cf.write(f.read(code_file))

        os.remove(os.path.join(export_path, "code.zip"))

        # Export the model used (if any)
        execution_info = self.pull_experiment_file(project_name, experiment_date, "execution_info.json")
        execution_info = json.loads(execution_info.decode("utf-8"))

        if execution_info["model_hash"]:
            model_zip = self.pull_model(project_name, execution_info['model_hash'])
            model_zip = BytesIO(model_zip)

            with zipfile.ZipFile(model_zip, "r") as f:
                for name in f.namelist():
                    # Create any sub-directories
                    os.makedirs(os.path.dirname(os.path.join(export_path, name)), exist_ok=True)

                    with open(os.path.join(export_path, name), "wb+") as ef:
                        ef.write(f.read(name))

        # Export the output (if requested)
        if include_output and self.storage.exists(experiment_path + "/output"):
            for f in self.storage.get_files(base_url=experiment_path + "/output"):
                self.storage.pull(experiment_path + "/output/" + f, local_path=os.path.join(export_path, "output", f))

        return export_path

    def __replicate_zip(self, project_name, experiment_date, export_path, include_output):
        output_zip = BytesIO()

        with zipfile.ZipFile(output_zip, "w") as output:
            # Import code package into the output zip
            code_zip = self.pull_experiment_file(project_name, experiment_date, "code.zip")
            code_zip = BytesIO(code_zip)

            with zipfile.ZipFile(code_zip, "r") as f:
                for name in f.namelist():
                    output.writestr(name, f.read(name))

            # Import the model used (if any)
            execution_info = self.pull_experiment_file(project_name, experiment_date, "execution_info.json")
            execution_info = json.loads(execution_info.decode("utf-8"))

            if execution_info["model_hash"]:
                model_zip = self.pull_model(project_name, execution_info['model_hash'])
                model_zip = BytesIO(model_zip)

                with zipfile.ZipFile(model_zip, "r") as f:
                    for name in f.namelist():
                        output.writestr(name, f.read(name))

            # Import the output (if requested)
            if include_output:
                for f in self.get_experiment_files(project_name, experiment_date, "output"):
                    data = self.pull_experiment_file(project_name, experiment_date, "output/" + f)
                    output.writestr("output/" + f, data)

        # Export the zip to a file (if an export path specified)
        if export_path:
            with open(export_path, "wb+") as f:
                output_zip.seek(0)
                f.write(output_zip.read())

            return export_path

        # Otherwise return the zip as a byte array
        output_zip.seek(0)
        return output_zip.read()
