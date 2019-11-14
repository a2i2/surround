import os
import re
import unittest
import shutil
import subprocess
import logging
import zipfile

from io import BytesIO

from ..experiment.file_storage_driver import FileStorageDriver
from ..experiment.experiment_reader import ExperimentReader
from ..experiment.experiment_writer import ExperimentWriter

class ExperimentReaderTest(unittest.TestCase):
    def setUp(self):
        writer = ExperimentWriter(storage_url="temporary/experiments", storage_driver=FileStorageDriver)
        writer.write_project("test_project", "test_description")
        writer.write_project("test_project_two", "test_description_2")

        process = subprocess.Popen(['surround', 'init', '-p', 'test_project', '-d', 'test_description', '-w', 'no'], cwd="temporary", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        process.stdout.close()
        process.stderr.close()

        process = subprocess.Popen(['surround', 'init', '-p', 'test_project_two', '-d', 'test_description', '-w', 'no'], cwd="temporary", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        process.stdout.close()
        process.stderr.close()

        with open("temporary/test_project/models/test.model", "w+") as f:
            f.write("WEIGHTS")

        with open("temporary/test_project_two/models/test.model", "w+") as f:
            f.write("WEIGHTS")

        writer.start_experiment("test_project", "temporary/test_project", args={'mode': 'batch'}, notes=['test', 'note'])
        logging.info("test_log")
        writer.stop_experiment(metrics={'test_metric': 0.1})

        writer.start_experiment("test_project", "temporary/test_project", args={'mode': 'batch'}, notes=['test', 'note'])
        logging.info("test_log")
        writer.stop_experiment(metrics={'test_metric': 0.2})

        writer.start_experiment("test_project_two", "temporary/test_project_two", args={'mode': 'batch'}, notes=['test', 'note'])
        logging.info("test_log")
        writer.stop_experiment(metrics={'test_metric': 0.2})

        writer.start_experiment("test_project_two", "temporary/test_project_two", args={'mode': 'batch'}, notes=['test', 'note'])
        writer.stop_experiment(metrics={'test_metric': 0.3})

        self.folder_names = os.listdir("temporary/experiments/experimentation/test_project/experiments")
        self.folder_names_2 = os.listdir("temporary/experiments/experimentation/test_project_two/experiments")

        self.folder_names = sorted(self.folder_names)
        self.folder_names_2 = sorted(self.folder_names_2)

    def tearDown(self):
        shutil.rmtree("temporary")

    def test_get_projects(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)
        projects = reader.get_projects()

        self.assertIsInstance(projects, list)

        expected_names = ["test_project", "test_project_two"]
        expected_descs = ["test_description", "test_description_2"]

        for proj in projects:
            self.assertIn("project_name", proj)
            self.assertIn("project_description", proj)
            self.assertIn("last_time_updated", proj)
            self.assertIn(proj['project_name'], expected_names)
            self.assertIn(proj['project_description'], expected_descs)
            self.assertRegex(proj['last_time_updated'], r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}$")

    def test_get_project(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        project = reader.get_project("test_project")
        self.assertEqual("test_project", project["project_name"])
        self.assertEqual("test_description", project["project_description"])
        self.assertRegex(project['last_time_updated'], r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}$")

        project = reader.get_project("doesnt exist")
        self.assertIsNone(project)

    def test_has_project(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        self.assertTrue(reader.has_project("test_project"))
        self.assertTrue(reader.has_project("test_project_two"))
        self.assertFalse(reader.has_project("non-exist"))

    def test_get_experiment(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        exp = reader.get_experiment("test_project", self.folder_names[0])

        self.assertIn("execution_info", exp)
        self.assertIn("logs", exp)
        self.assertIn("results", exp)

        self.assertEqual(exp["execution_info"]["start_time"], self.folder_names[0])
        self.assertEqual(exp["logs"][0], "INFO:root:test_log")
        self.assertEqual(exp["results"]["start_time"], self.folder_names[0])

    def test_get_experiments(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        exps = reader.get_experiments("test_project")

        for exp in exps:
            self.assertIn(exp['execution_info']['start_time'], self.folder_names + self.folder_names_2)
            self.assertEqual(exp["logs"][0], "INFO:root:test_log")
            self.assertIn(exp['results']['start_time'], self.folder_names + self.folder_names_2)

    def test_has_experiment(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        for name in self.folder_names:
            self.assertTrue(reader.has_experiment("test_project", name))

        for name in self.folder_names_2:
            self.assertTrue(reader.has_experiment("test_project_two", name))

        self.assertFalse(reader.has_experiment("non-exist", "non-exists"))
        self.assertFalse(reader.has_experiment("test_project", "non-exists"))
        self.assertFalse(reader.has_experiment("test_project_two", "non-exists"))

    def test_get_experiment_files(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        expected_files = [
            "code.zip",
            "results.json",
            "execution_info.json",
            "log.txt"
        ]

        for name in self.folder_names:
            files = reader.get_experiment_files("test_project", name)
            for f in expected_files:
                self.assertIn(f, files)

        for name in self.folder_names_2:
            files = reader.get_experiment_files("test_project_two", name)
            for f in expected_files:
                self.assertIn(f, files)

    def test_get_cache_files(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        files = reader.get_project_cache("test_project")

        for f in files:
            self.assertRegex(f, r"^model-[T0-9\-]{26}-[a-z0-9]+\.zip$")

    def test_pull_experiment_files(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        log = reader.pull_experiment_file("test_project", self.folder_names[0], "log.txt")
        self.assertIsNotNone(log)

        log = log.decode('utf-8')
        self.assertEqual("INFO:root:test_log", log.rstrip())

        log = reader.pull_experiment_file("test_project_two", self.folder_names_2[0], "log.txt")
        self.assertIsNotNone(log)

        log = log.decode('utf-8')
        self.assertEqual("INFO:root:test_log", log.rstrip())

    def test_pull_cache_files(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        cache_files = reader.get_project_cache("test_project")
        self.assertGreater(len(cache_files), 0)

        model = reader.pull_cache_file("test_project", cache_files[0])
        self.assertIsNotNone(model)

        with open("temporary/model.zip", "wb+") as f:
            f.write(model)

        with zipfile.ZipFile("temporary/model.zip", "r") as f:
            model_file = f.read("models/test.model")
            model_file = model_file.decode('utf-8')
            self.assertEqual("WEIGHTS", model_file)

    def test_pull_model(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        cache_files = reader.get_project_cache("test_project")
        self.assertGreater(len(cache_files), 0)
        self.assertRegex(cache_files[0], r"^model.+-(.+)\.zip$")

        expected_file = reader.pull_cache_file("test_project", cache_files[0])

        model_hash = re.match(r"^model.+-(.+)\.zip$", cache_files[0]).group(1)
        pulled_file = reader.pull_model("test_project", model_hash)

        self.assertIsNotNone(pulled_file)
        self.assertEqual(expected_file, pulled_file)

    def test_replicate_file(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        output = reader.replicate("test_project", self.folder_names[0], file_path="temporary/replication")
        self.assertEqual(output, "temporary/replication")

        expected_files = [
            '.surround',
            'models/test.model',
            'test_project/',
            'test_project/stages/baseline.py',
            'dodo.py',
        ]

        self.assertTrue(os.path.exists("temporary/replication"))

        for expected in expected_files:
            self.assertTrue(os.path.exists(os.path.join("temporary/replication", expected)))

        with open("temporary/replication/models/test.model", "r") as f:
            self.assertEqual("WEIGHTS", f.read())

    def test_replicate_zip(self):
        reader = ExperimentReader(storage_url="temporary/experiments", storage_driver=FileStorageDriver)

        output_zip = reader.replicate("test_project", self.folder_names[0])
        output_zip = BytesIO(output_zip)

        self.assertIsNotNone(output_zip)

        expected_files = [
            '.surround/config.yaml',
            'models/test.model',
            'test_project/__main__.py',
            'test_project/stages/baseline.py',
            'dodo.py',
        ]

        with zipfile.ZipFile(output_zip, "r") as f:
            for expected in expected_files:
                self.assertIn(expected, f.namelist())
