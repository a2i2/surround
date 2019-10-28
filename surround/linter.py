import os
from pathlib import Path
from pylint.lint import Run

class Linter():
    """
    Represents the Surround linter which performs multiple checks on the surround project
    and displays warnings/errors found during the linting process.

    This class is used by the Surround CLI to perform the linting of a project via the
    `lint` sub-command.
    """

    def dump_checks(self):
        """
        Dumps a list of the checks in this linter to the terminal.

        :return: formatted list of the checkers in the linter
        :rtype: str
        """

        print("Checkers in Surround's linter")
        print("=============================")

        try:
            Run(['--list-msgs-enabled'])
        except SystemExit:
            pass

    def check_project(self, project_root=os.curdir, extra_args=None, verbose=False):
        """
        Runs the linter against the project specified, returning zero on success

        :param project_root: path to the root of the project (default: current directory)
        :type project_root: str
        :return: errors and warnings found (if any)
        :rtype: (list of error strings, list of warning strings)
        """

        args = [str(p) for p in Path(project_root).glob("**/*.py")]
        if extra_args:
            args.extend(extra_args)

        disable_msgs = [
            'missing-class-docstring',
            'missing-function-docstring',
            'abstract-method',
            'attribute-defined-outside-init'
        ]

        for msg in disable_msgs:
            args.append('--disable=%s' % msg)

        result = Run(args, do_exit=False)
        return result.linter.msg_status == 0
