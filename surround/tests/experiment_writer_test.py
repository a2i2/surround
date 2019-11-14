import os
import json
import shutil
import logging
import zipfile
import unittest
import subprocess
from ..experiment.experiment_writer import ExperimentWriter

class ExperimentWriterTest(unittest.TestCase):
    def setUp(self):
        # Create a project
        process = subprocess.Popen(["surround", "init", "-p", "temp_project", "-d", "test_description", "-w", "no"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        process.wait()
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()

        with open("temp_project/input/test.txt", "w+") as f:
            f.write("TEST_DATA")

        os.mkdir("temp_experiment_storage")

    def tearDown(self):
        shutil.rmtree("temp_project")
        shutil.rmtree("temp_experiment_storage")

    def test_write_project(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")

        self.assertTrue(os.path.exists("temp_experiment_storage/experimentation/temp_project/project.json"))
        with open("temp_experiment_storage/experimentation/temp_project/project.json", "r") as f:
            project_obj = json.loads(f.read())
            self.assertEqual("temp_project", project_obj["project_name"])
            self.assertEqual("test_description", project_obj["project_description"])
            self.assertIn("last_time_updated", project_obj)

    def test_remove_project(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")
        writer.remove_project("temp_project")

        self.assertFalse(os.path.exists("temp_experiment_storage/experimentation/temp_project"))

    def test_remove_experiment(self):
        writer = ExperimentWriter("temp_experiment_storage")

        writer.write_project("temp_project", "test_description")
        writer.start_experiment("temp_project", "temp_project", args={"mode": "batch"}, notes=["some", "notes"])
        writer.stop_experiment()

        folder_name = os.listdir("temp_experiment_storage/experimentation/temp_project/experiments")
        self.assertGreater(len(folder_name), 0)

        folder_name = folder_name[0]
        writer.remove_experiment("temp_project", folder_name)

        self.assertFalse(os.path.exists("temp_experiment_storage/experimentation/temp_project/experiments/%s" % folder_name))

    def test_start_experiment(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")
        writer.start_experiment("temp_project", "temp_project", args={"mode": "batch"}, notes=["some", "notes"])

        path = "temp_experiment_storage/experimentation/temp_project/experiments"
        self.assertTrue(os.path.exists(path))

        files = os.listdir(path)
        self.assertGreater(len(files), 0)
        self.assertRegex(files[0], r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{6}$")
        self.assertTrue(os.path.exists(os.path.join(path, files[0], "execution_info.json")))
        self.assertTrue(os.path.exists(os.path.join(path, files[0], "code.zip")))

        with zipfile.ZipFile(os.path.join(path, files[0], "code.zip"), "r") as f:
            code_files = f.namelist()

            expected_files = []
            for root, _, exp_files in os.walk("temp_project"):
                for ff in exp_files:
                    expected_files.append(os.path.relpath(os.path.join(root, ff), "temp_project"))

            expected_files = [exp_file.replace("\\", "/") for exp_file in expected_files]

            self.assertGreater(len(code_files), 0)
            for actual_file in code_files:
                self.assertIn(actual_file, expected_files)

        with open(os.path.join(path, files[0], "execution_info.json"), "r") as f:
            execution_info = json.load(f)
            self.assertIn("author", execution_info)
            self.assertIn("name", execution_info["author"])
            self.assertIn("email", execution_info["author"])
            self.assertIsNotNone(execution_info["author"]["name"])
            self.assertIsNotNone(execution_info["author"]["email"])
            self.assertDictEqual({"mode": "batch"}, execution_info["arguments"])
            self.assertListEqual(["some", "notes"], execution_info["notes"])
            self.assertIn("input/test.txt", [inf.replace("\\", "/") for inf in execution_info["input_files"]])

        writer.stop_experiment()

    def test_stop_experiment(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")

        writer.start_experiment("temp_project", "temp_project")
        writer.stop_experiment(metrics={"metric1": 0.99, "metric2": [0.2, 0.3]})

        path = "temp_experiment_storage/experimentation/temp_project/experiments"
        path = os.path.join(path, os.listdir(path)[0])

        self.assertTrue(os.path.exists(os.path.join(path, "log.txt")))
        self.assertTrue(os.path.exists(os.path.join(path, "results.json")))

        with open(os.path.join(path, "results.json"), "r") as f:
            results = json.load(f)
            self.assertIn("start_time", results)
            self.assertIn("end_time", results)
            self.assertIn("metrics", results)
            self.assertRegex(results["start_time"], r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{6}$")
            self.assertRegex(results["end_time"], r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{6}$")
            self.assertDictEqual({"metric1": 0.99, "metric2": [0.2, 0.3]}, results["metrics"])

    def test_error_on_double_start(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")

        writer.start_experiment("temp_project", "temp_project")

        with self.assertRaises(Exception):
            writer.start_experiment("temp_project", "temp_project")

        writer.stop_experiment()

    def test_error_on_end_without_start(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")

        with self.assertRaises(Exception):
            writer.stop_experiment()

    def test_no_project(self):
        writer = ExperimentWriter("temp_experiment_storage")

        with self.assertRaises(Exception):
            writer.start_experiment("temp_project", "temp_project")

    def test_model_capture(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")

        with open("temp_project/models/test_model.txt", "w+") as f:
            f.write("MODEL_CODE")

        writer.start_experiment("temp_project", "temp_project")
        writer.stop_experiment()

        path = "temp_experiment_storage/experimentation/temp_project/experiments"
        path = os.path.join(path, os.listdir(path)[0])

        with open(os.path.join(path, "execution_info.json"), "r") as f:
            execution_info = json.load(f)
            model_hash = execution_info["model_hash"]
            self.assertIsNotNone(model_hash)

        path = "temp_experiment_storage/experimentation/temp_project/cache"
        cache_files = os.listdir(path)

        self.assertGreater(len(cache_files), 0)
        model_file = cache_files[0]

        self.assertIn(model_hash, model_file)

        with zipfile.ZipFile(os.path.join(path, model_file), "r") as f:
            self.assertEqual("MODEL_CODE", f.read("models/test_model.txt").decode('utf-8'))

    def test_log_capture(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")

        writer.start_experiment("temp_project", "temp_project")

        expected_logs = ["test_log", "test_log_2"]

        logger = logging.getLogger("test_logger")

        for log in expected_logs:
            logger.info(log)

        writer.stop_experiment()

        path = "temp_experiment_storage/experimentation/temp_project/experiments"
        path = os.path.join(path, os.listdir(path)[0])

        self.assertTrue(os.path.exists(os.path.join(path, "log.txt")), msg=str(os.listdir(path)))
        self.assertTrue(os.path.exists(os.path.join(path, "logs")))

        # Check log.txt has all the expected logs, formatted correctly
        with open(os.path.join(path, "log.txt"), "r") as f:
            log = f.read()
            for exp_log in expected_logs:
                self.assertIn("INFO:test_logger:%s" % exp_log, log)

        # Check log/ has a file for each log and the contents are correct
        log_files = os.listdir(os.path.join(path, "logs"))
        self.assertEqual(len(expected_logs), len(log_files))
        log_files = sorted(log_files)

        for i, exp_log in enumerate(expected_logs):
            with open(os.path.join(path, "logs", log_files[i]), "r") as f:
                self.assertEqual("INFO:test_logger:%s" % exp_log, f.read())

    def test_output_capture(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")
        writer.start_experiment("temp_project", "temp_project")

        with open("temp_project/output/test_output.txt", "w+") as f:
            f.write("TEST_OUTPUT")

        writer.stop_experiment()

        path = "temp_experiment_storage/experimentation/temp_project/experiments"
        path = os.path.join(path, os.listdir(path)[0])

        self.assertTrue(os.path.exists(os.path.join(path, "output", "test_output.txt")))
        with open(os.path.join(path, "output", "test_output.txt"), "r") as f:
            self.assertEqual("TEST_OUTPUT", f.read())

    def test_html_results_capture(self):
        writer = ExperimentWriter("temp_experiment_storage")
        writer.write_project("temp_project", "test_description")
        writer.start_experiment("temp_project", "temp_project")

        with open("temp_project/output/results.html", "w+") as f:
            f.write("TEST_OUTPUT")

        writer.stop_experiment()

        path = "temp_experiment_storage/experimentation/temp_project/experiments"
        path = os.path.join(path, os.listdir(path)[0])

        self.assertTrue(os.path.exists(os.path.join(path, "results.html")))
        with open(os.path.join(path, "results.html"), "r") as f:
            self.assertEqual("TEST_OUTPUT", f.read())
