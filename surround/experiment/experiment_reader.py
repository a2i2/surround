import re
import json
from .util import get_surround_config, get_driver_type_from_url

class ExperimentReader:
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
        if not self.has_project(project_name):
            return None

        results = []
        path = "experimentation/%s/experiments/" % project_name
        if self.storage.exists(path):
            experiment_files = self.storage.get_files(base_url=path)
            execution_files = [f for f in experiment_files if re.match(r"^[T0-9\-]+[/\\]{1,2}execution_info.json$", f)]

            execution_infos = []
            for exec_file in execution_files:
                info_obj = self.storage.pull(path + exec_file).decode('utf-8')
                info_obj = json.loads(info_obj)
                execution_infos.append(info_obj)

            for execution_info in execution_infos:
                if self.storage.exists(path + execution_info["start_time"] + "/results.json"):
                    result_obj = self.storage.pull(path + execution_info["start_time"] + "/results.json")
                    result_obj = json.loads(result_obj.decode('utf-8'))
                else:
                    result_obj = None

                if self.storage.exists(path + execution_info["start_time"] + "/log.txt"):
                    log = self.storage.pull(path + execution_info["start_time"] + "/log.txt").decode('utf-8')
                else:
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
        if not self.storage.exists(path):
            return None

        return self.storage.pull(path)

    def pull_cache_file(self, project_name, path):
        path = "experimentation/%s/cache/%s" % (project_name, path)
        if not self.storage.exists(path):
            return None

        return self.storage.pull(path)
