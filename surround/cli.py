import argparse
import os
import sys
import inspect
import logging
import subprocess
from pathlib import Path
import pkg_resources
import yaml

try:
    import tornado.ioloop
    from .runner.web import api
except ImportError:
    pass

from .surround import AllowedTypes
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
            ("requirements.txt", "surround=={version}\ntornado==6.0.1"),
            (".surround/config.yaml", "project-info:\n  project-name: {project_name}")
        ],
        "templates" : [
            # File name, template name, capitalize project name
            ("README.md", "README.md.txt", False),
            ("{project_name}/stages.py", "stages.py.txt", True),
            ("{project_name}/__main__.py", "main.py.txt", True),
            ("{project_name}/__init__.py", "init.py.txt", True),
            ("{project_name}/wrapper.py", "wrapper.py.txt", True),
            ("dodo.py", "dodo.py.txt", False),
            ("Dockerfile", "Dockerfile.txt", False),
            ("{project_name}/config.yaml", "config.yaml.txt", False)

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

def process_templates(templates, folder, project_dir, project_name, project_description):
    for afile, template, capitalize in templates:
        actual_file = afile.format(project_name=project_name, project_description=project_description)
        path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        with open(os.path.join(path, "templates", folder, template)) as f:
            contents = f.read()
            name = project_name.capitalize() if capitalize else project_name
            actual_contents = contents.format(project_name=name, project_description=project_description)
            file_path = os.path.join(project_dir, actual_file)
        with open(file_path, 'w') as f:
            f.write(actual_contents)

def process(project_dir, project, project_name, project_description, folder):
    if os.path.exists(project_dir):
        return False
    os.makedirs(project_dir)
    process_directories(project["dirs"], project_dir, project_name)
    process_files(project["files"], project_dir, project_name, project_description)
    process_templates(project["templates"], folder, project_dir, project_name, project_description)
    return True

def is_valid_dir(aparser, arg):
    if not os.path.isdir(arg):
        aparser.error("Invalid directory %s" % arg)
    elif not os.access(arg, os.W_OK | os.X_OK):
        aparser.error("Can't write to %s" % arg)
    else:
        return arg

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

    deploy = {
        "new": {
            "dirs": [
                "models",
                "{project_name}",
            ],
            "files" : [
                ("{project_name}/config.yaml", "output:\n  text: Hello World"),
                ("dodo.py", "")
            ],
            "templates" : []
        }
    }

    path = args.path
    web = args.web
    errors, warnings = Linter().check_project(deploy, path)
    if errors:
        print("Invalid Surround project")
    for e in errors + warnings:
        print(e)
    if not errors:
        if args.task:
            task = args.task
        else:
            task = 'list'

        if web:
            obj = None
            loaded_class = None
            path_to_modules = os.path.join(os.getcwd(), os.path.basename(os.getcwd()))
            path_to_config = os.path.join(path_to_modules, "config.yaml")

            if Path(path_to_config).exists():
                with open(path_to_config, "r") as f:
                    config = yaml.safe_load(f)
                    module_name = config["wrapper-info"]["module"]
                    class_name = config["wrapper-info"]["class"]
            else:
                print("error: config does not exist")
                return

            if Path(os.path.join(path_to_modules, module_name + ".py")).exists():
                load_modules_from_path(path_to_modules, module_name)
                if hasattr(sys.modules[module_name], class_name):
                    loaded_class = load_class_from_name(module_name, class_name)
                    obj = loaded_class()
                else:
                    print("error: " + module_name + " does not have " + class_name)
                    return
            else:
                print("error: " + module_name + " does not exist")
                return

            if obj is None:
                print("error: cannot load " + class_name + " from " + module_name)
                return

            app = api.make_app(obj)
            app.listen(8888)
            print(os.path.basename(os.getcwd()) + " is running on http://localhost:8888")
            print("Available endpoints:")
            print("* GET  /                 # Health check")
            if obj.type_of_uploaded_object == AllowedTypes.FILE:
                print("* GET  /upload           # Upload data")
            print("* POST /predict          # Send data to the Surround pipeline")
            tornado.ioloop.IOLoop.current().start()
        else:
            print("Project tasks:")
            run_process = subprocess.Popen(['python3', '-m', 'doit', task], cwd=path)
            run_process.wait()

def parse_tutorial_args(args):
    new_dir = os.path.join(args.path, "tutorial")
    if process(new_dir, PROJECTS["new"], "tutorial", None, "tutorial"):
        print("The tutorial project has been created.\n")
        print("Start by reading the README.md file at:")
        print(os.path.abspath(os.path.join(args.path, "tutorial", "README.md")))
    else:
        print("Directory %s already exists" % new_dir)


def parse_init_args(args):
    if args.project_name:
        project_name = args.project_name
    else:
        while True:
            project_name = input("Name of project: ")
            if not project_name.isalpha() or not project_name.islower():
                print("Project name requires lowercase letters only")
            else:
                break

    if args.description:
        project_description = args.description
    else:
        project_description = input("What is the purpose of this project?: ")

    new_dir = os.path.join(args.path, project_name)
    if process(new_dir, PROJECTS["new"], project_name, project_description, "new"):
        print("Project created at %s" % os.path.join(os.path.abspath(args.path), project_name))
    else:
        print("Directory %s already exists" % new_dir)

def parse_tool_args(parsed_args, remote_parser, tool):
    if tool == "tutorial":
        parse_tutorial_args(parsed_args)
    elif tool == "lint":
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


    tutorial_parser = sub_parser.add_parser('tutorial', help="Create the tutorial project")
    tutorial_parser.add_argument('tutorial', help="Create the Surround tutorial project", action='store_true')
    tutorial_parser.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path for creating the tutorial project", nargs='?', default="./")

    init_parser = sub_parser.add_parser('init', help="Initialise a new Surround project")
    init_parser.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path for creating a Surround project", nargs='?', default="./")
    init_parser.add_argument('-p', '--project-name', help="Name of the project", type=lambda x: is_valid_name(parser, x))
    init_parser.add_argument('-d', '--description', help="A description for the project")

    run_parser = sub_parser.add_parser('run', help="Run a Surround project task, witout an argument all tasks will be shown")
    run_parser.add_argument('task', help="Task defined in a Surround project dodo.py file.", nargs='?')
    run_parser.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path to a Surround project", nargs='?', default="./")
    run_parser.add_argument('-w', '--web', help="Name of the class inherited from Wrapper", action='store_true')

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
    tools = ["init", "tutorial", "lint", "run", "remote", "add", "pull", "push", "list"]
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
