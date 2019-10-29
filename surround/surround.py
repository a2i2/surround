import logging

from .runners import RunMode
from .experiment import ExperimentWriter

LOGGER = logging.getLogger(__name__)

class Surround:
    def __init__(self, runners, assemblies, project_name, project_description, project_root):
        self.runners = runners
        self.assemblies = assemblies
        self.project_name = project_name
        self.project_root = project_root

        # Create a project in the experiment storage
        self.writer = ExperimentWriter()
        self.writer.write_project(project_name, project_description)

    def run(self, runner_key, assembler_key, mode, is_experiment=True, args=None):
        if is_experiment:
            notes = [args.note] if args and args.note else []
            self.writer.start_experiment(self.project_name, self.project_root, vars(args), notes)

        runner = self.__get_runner(runner_key)

        if not runner:
            LOGGER.error("Failed to find runner '%s'", runner_key)
            return

        assembler = self.__get_assembler(assembler_key)

        if not assembler:
            LOGGER.error("Failed to find assembler '%s'", assembler_key)
            return

        if mode == "batch":
            mode = RunMode.BATCH_PREDICT
        else:
            mode = RunMode.TRAIN

        runner.set_assembler(assembler)
        runner.run(mode)

        if is_experiment:
            self.writer.stop_experiment(metrics=runner.assembler.state.metrics)

        return runner.assembler.state, runner, runner.assembler

    def show_info(self):
        print("Available assemblies:")
        self.list_assemblies()

        print("\nAvailable runners:")
        self.list_runners()

    def list_assemblies(self):
        for i, assembler in enumerate(self.assemblies):
            print("%i. %s" % (i, assembler.assembler_name))

    def list_runners(self):
        for i, runner in enumerate(self.runners):
            print("%i. %s" % (i, runner.name))

    def __get_assembler(self, key):
        assembler = None

        # Try and get the assembler via index
        try:
            index = int(key)

            if 0 <= index < len(self.assemblies):
                assembler = self.assemblies[index]
        except Exception:
            pass

        # Try and get the assember via key (name)
        if not assembler:
            assembler = next((x for x in self.assemblies if x.assembler_name.lower() == key.lower()), None)

        return assembler

    def __get_runner(self, key):
        runner = None

        # Try and get the assembler via index
        try:
            index = int(key)

            if 0 <= index < len(self.runners):
                runner = self.runners[index]
        except Exception:
            pass

        # Try and get the assember via key (name)
        if not runner:
            runner = next((x for x in self.runners if x.name.lower() == key.lower()), None)

        return runner
