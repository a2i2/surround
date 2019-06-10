import argparse
import re
import os
import sys
import inspect
import logging
import subprocess
import pkg_resources

from .remote import cli as remote_cli
from .linter import Linter

PROJECTS = {
    "new" : {
        "dirs" : [
            ".surround",
            "data",
            "output",
            "docs",
            "models",
            "notebooks",
            "scripts",
            "{project_name}",
            "spikes",
            "tests",
        ],
        "files": [
            ("requirements.txt", "surround=={version}"),
            (".surround/config.yaml", "project-info:\n  project-name: {project_name}")
        ],
        "templates" : [
            # File name, template name, capitalize project name
            ("README.md", "README.md.txt", False),
            ("{project_name}/stages.py", "stages.py.txt", True),
            ("{project_name}/runners.py", "runners.py.txt", True),
            ("{project_name}/__main__.py", "main.py.txt", True),
            ("{project_name}/__init__.py", "init.py.txt", True),
            ("dodo.py", "dodo.py.txt", False),
            ("Dockerfile", "Dockerfile.txt", False),
            ("{project_name}/config.yaml", "config.yaml.txt", False),
            (".gitignore", ".gitignore.txt", False)
        ]
    }
}

def process_directories(directories, project_dir, project_name):
    for directory in directories:
        actual_directory = directory.format(project_name=project_name)
        os.makedirs(os.path.join(project_dir, actual_directory))

def process_files(files, project_dir, project_name, project_description):
    for afile, content in files:
        actual_file = afile.format(project_name=project_name, project_description=project_description)
        actual_content = content.format(project_name=project_name, project_description=project_description, version=pkg_resources.get_distribution("surround").version)
        file_path = os.path.join(project_dir, actual_file)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(actual_content)

# pylint: disable=too-many-locals
def process_templates(templates, folder, project_dir, project_name, project_description, require_web):
    for afile, template, capitalize in templates:
        actual_file = afile.format(project_name=project_name, project_description=project_description)
        path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

        # Replace certain files when web service is required
        if require_web:
            if template == "runners.py.txt":
                template = "web_runner.py.txt"
            if template == "main.py.txt":
                template = "web_main.py.txt"

        with open(os.path.join(path, "templates", folder, template)) as f:
            contents = f.read()
            name = project_name.capitalize() if capitalize else project_name
            actual_contents = contents.format(project_name=name, project_description=project_description)
            file_path = os.path.join(project_dir, actual_file)
        with open(file_path, 'w') as f:
            f.write(actual_contents)

def process(project_dir, project, project_name, project_description, require_web, folder):
    if os.path.exists(project_dir):
        return False
    os.makedirs(project_dir)
    process_directories(project["dirs"], project_dir, project_name)
    process_files(project["files"], project_dir, project_name, project_description)
    process_templates(project["templates"], folder, project_dir, project_name, project_description, require_web)
    return True

def is_valid_dir(aparser, arg):
    if not os.path.isdir(arg):
        aparser.error("Invalid directory %s" % arg)
    elif not os.access(arg, os.W_OK | os.X_OK):
        aparser.error("Can't write to %s" % arg)
    else:
        return arg

def allowed_to_access_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        print("error: can't write to " + path)

    if os.access(path, os.R_OK | os.W_OK | os.F_OK | os.X_OK):
        return True
    return False

def is_valid_name(aparser, arg):
    if not arg.isalpha() or not arg.islower():
        aparser.error("Name %s must be lowercase letters" % arg)
    else:
        return arg

def load_modules_from_path(path, module_name):
    """Import all modules from the given directory

    :param path: Path to the directory
    :type path: string
    :param module_name: module to load
    :type module_name: string
    """
    # Check and fix the path
    if path[-1:] != '/':
        path += '/'

    # Get a list of files in the directory, if the directory exists
    if not os.path.exists(path):
        raise OSError("Directory does not exist: %s" % path)

    # Add path to the system path
    sys.path.append(path)

    # Another possibility
    # Load all the files, check: https://github.com/dstil/surround/pull/68/commits/2175f1ae11ad903d6513e4f288d80d182499bf38

    # For now, just load the wrapper.py
    modname = module_name

    # Import the module
    __import__(modname, globals(), locals(), ['*'])

def load_class_from_name(modulename, classname):
    """Import class from given module

    :param modulename: Name of the module
    :type modulename: string
    :param classname: Name of the class
    :type classname: string
    """

    # Import the module
    __import__(modulename, globals(), locals(), ['*'])

    # Get the class
    cls = getattr(sys.modules[modulename], classname)

    # Check cls
    if not inspect.isclass(cls):
        raise TypeError("%s is not a class" % classname)

    return cls

def parse_lint_args(args):
    linter = Linter()
    if args.list:
        print(linter.dump_checks())
    else:
        errors, warnings = linter.check_project(PROJECTS, args.path)
        for e in errors + warnings:
            print(e)
        if not errors and not warnings:
            print("All checks passed")

def parse_run_args(args):
    logging.getLogger().setLevel(logging.INFO)

    if remote_cli.is_surround_project():
        actual_current_dir = os.getcwd()
        os.chdir(remote_cli.get_project_root_from_current_dir())
        run_locally(args)
        os.chdir(actual_current_dir)
    else:
        print("error: not a surround project")

def run_locally(args):
    if args.task:
        task = args.task
    else:
        task = 'list'

    print("Project tasks:")
    run_process = subprocess.Popen([sys.executable, '-m', 'doit', task])
    run_process.wait()

# pylint: disable=too-many-branches
def parse_init_args(args):
    if allowed_to_access_dir(args.path):
        if args.project_name:
            project_name = args.project_name
        else:
            while True:
                project_name = input("Name of project: ")
                if not re.match("^[A-Za-z_-]*$", project_name) or not project_name.islower():
                    print("error: project name requires lowercase letters and hyphens only")
                else:
                    break

        if args.description:
            project_description = args.description
        else:
            project_description = input("What is the purpose of this project?: ")

        if args.require_web:
            require_web = args.require_web
        else:
            while True:
                require_web_string = input("Does it require a web runner? (yes / no) ")
                if require_web_string.lower() == "yes":
                    require_web = True
                    break
                if require_web_string.lower() == "no":
                    require_web = False
                    break

        new_dir = os.path.join(args.path, project_name)
        if process(new_dir, PROJECTS["new"], project_name, project_description, require_web, "new"):
            print("info: project created at %s" % os.path.join(os.path.abspath(args.path), project_name))
        else:
            print("error: directory %s already exists" % new_dir)
    else:
        print("error: permission denied")

def parse_tool_args(parsed_args, remote_parser, tool):
    if tool == "lint":
        parse_lint_args(parsed_args)
    elif tool == "run":
        parse_run_args(parsed_args)
    elif tool == "remote":
        remote_cli.parse_remote_args(remote_parser, parsed_args)
    elif tool == "add":
        remote_cli.parse_add_args(parsed_args)
    elif tool == "pull":
        remote_cli.parse_pull_args(parsed_args)
    elif tool == "push":
        remote_cli.parse_push_args(parsed_args)
    elif tool == "list":
        remote_cli.parse_list_args(parsed_args)
    else:
        parse_init_args(parsed_args)

def main():

    parser = argparse.ArgumentParser(prog='surround', description="The Surround Command Line Interface")
    sub_parser = parser.add_subparsers(description="Surround must be called with one of the following commands")

    init_parser = sub_parser.add_parser('init', help="Initialise a new Surround project")
    init_parser.add_argument('path', help="Path for creating a Surround project", nargs='?', default="./")
    init_parser.add_argument('-p', '--project-name', help="Name of the project", type=lambda x: is_valid_name(parser, x))
    init_parser.add_argument('-d', '--description', help="A description for the project")
    init_parser.add_argument('-w', '--require-web', help="Is web service required for the project")

    run_parser = sub_parser.add_parser('run', help="Run a Surround project task, witout an argument all tasks will be shown")
    run_parser.add_argument('task', help="Task defined in a Surround project dodo.py file.", nargs='?')

    linter_parser = sub_parser.add_parser('lint', help="Run the Surround linter")
    linter_group = linter_parser.add_mutually_exclusive_group(required=False)
    linter_group.add_argument('-l', '--list', help="List all Surround checkers", action='store_true')
    linter_group.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path for running the Surround linter", nargs='?', default="./")

    remote_parser = remote_cli.add_remote_parser(sub_parser)
    remote_cli.create_add_parser(sub_parser)
    remote_cli.add_pull_parser(sub_parser)
    remote_cli.add_push_parser(sub_parser)
    remote_cli.add_list_parser(sub_parser)

    # Check for valid sub commands as 'add_subparsers' in Python < 3.7
    # is missing the 'required' keyword
    tools = ["init", "lint", "run", "remote", "add", "pull", "push", "list"]
    try:
        if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
            parser.print_help()
        elif len(sys.argv) < 2 or not sys.argv[1] in tools:
            print("Invalid subcommand, must be one of %s" % tools)
            parser.print_help()
        else:
            tool = sys.argv[1]
            parsed_args = parser.parse_args()
            parse_tool_args(parsed_args, remote_parser, tool)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")

if __name__ == "__main__":
    main()
