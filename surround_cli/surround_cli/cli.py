import argparse
import re
import os
import sys
import inspect
import logging
import subprocess
import pkg_resources

from surround.project import PROJECTS
from .remote import cli as remote_cli
from .split import cli as split_cli
from .visualise import cli as visualise_cli
from .data.cli import cli as data_cli
from .linter import Linter

def process_directories(directories, project_dir, project_name):
    """
    Creates new directories in the project folder according to the list provided.

    :param directories: collection of directory names
    :type directories: list of strings
    :param project_dir: path to the project directory
    :type project_dir: string
    :param project_name: name of the project
    :type project_name: string
    """

    for directory in directories:
        actual_directory = directory.format(project_name=project_name)
        os.makedirs(os.path.join(project_dir, actual_directory))

def process_files(files, project_dir, project_name, project_description, require_web):
    """
    Create new files in the project directory, inserting the project name and description into their content.

    :param files: collection of file templates (filenames and content to insert into the file)
    :type files: list of tuples (filename: string, content: string)
    :param project_dir: path to the project directory
    :type project_dir: string
    :param project_name: name of the project
    :type project_name: string
    :param project_description: description of the project
    :type project_description: string
    """

    for afile, content in files:
        actual_file = afile.format(project_name=project_name, project_description=project_description)
        actual_content = content.format(project_name=project_name, project_description=project_description, version=pkg_resources.get_distribution("surround").version)
        file_path = os.path.join(project_dir, actual_file)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(actual_content)

# pylint: disable=too-many-locals
def process_templates(templates, folder, project_dir, project_name, project_description,
                      author_name, author_email, require_web):
    """
    Creates files from templates into the project directory with the project name and description inserted.

    :param templates: collection of templates
    :type templates: list of tuples (filename: string, templateFilename: string, capitalizeName: boolean)
    :param folder: name of the folder containing the templates
    :type folder: string
    :param project_dir: path of the project directory
    :type project_dir: string
    :param project_name: name of the project
    :type project_name: string
    :param project_description: description of the project
    :type project_description: string
    :param author_name: name of the author
    :type author_name: string
    :param author_email: email of the author
    :type author_email: string
    :param require_web: whether the project requires web components
    :type require_web: bool
    """

    for afile, template, capitalize, web_component in templates:
        actual_file = afile.format(project_name=project_name, project_description=project_description)
        path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

        if not require_web and web_component:
            continue

        with open(os.path.join(path, "templates", folder, template)) as f:
            contents = f.read()
            name = project_name.capitalize() if capitalize else project_name
            actual_contents = contents.format(project_name=name, project_description=project_description,
                                              author_name=author_name, author_email=author_email,
                                              version=pkg_resources.get_distribution("surround").version)
            if require_web and afile == "pyproject.toml":
                actual_contents = actual_contents.replace("\n[build-system]", "tornado =\"6.1.0\"\n\n[build-system]")

            file_path = os.path.join(project_dir, actual_file)
        with open(file_path, 'w') as f:
            f.write(actual_contents)

def process(project_dir, project, project_name, project_description, author_name, author_email, require_web, folder):
    """
    Creates a new Surround project using the directory and template provided.

    :param project_dir: path to the project directory
    :type project_dir: string
    :param project: project structure template
    :type project: dictionary
    :param project_name: name of the new project
    :type project_name: string
    :param project_description: description of the new project
    :type project_description: string
    :param author_name: name of the author
    :type author_name: string
    :param author_email: email of the author
    :type author_email: string
    :param require_web: whether the project requires web components
    :type require_web: bool
    :param folder: name of the folder in the templates folder to use
    :type folder: string
    :return: Whether the process completed successfully
    :rtype: bool
    """

    if os.path.exists(project_dir):
        return False
    os.makedirs(project_dir)
    process_directories(project["dirs"], project_dir, project_name)
    process_files(project["files"], project_dir, project_name, project_description, require_web)
    process_templates(project["templates"], folder, project_dir, project_name, project_description, author_name, author_email, require_web)
    return True

def is_valid_dir(aparser, arg):
    """
    Checks whether the directory provided is valid for use with Surround.

    :param aparser: the parser being used
    :type aparser: <class 'argparse.ArgumentParser'>
    :param arg: the argument containing the directory path
    :type arg: string
    :return: the path if valid, or nothing
    :rtype: string
    """

    if not os.path.isdir(arg):
        aparser.error("Invalid directory %s" % arg)
    elif not os.access(arg, os.W_OK | os.X_OK):
        aparser.error("Can't write to %s" % arg)
    else:
        return arg

def allowed_to_access_dir(path):
    """
    Checks whether we have permission to access the specified directory.
    This includes read, write, and execution.

    :param path: the path to the directory
    :type path: string
    :return: whether access is allowed
    :rtype: boolean
    """

    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        print("error: can't write to " + path)

    if os.access(path, os.R_OK | os.W_OK | os.F_OK | os.X_OK):
        return True
    return False

def is_valid_name(aparser, arg):
    """
    Checks whether a name passed in arguments is valid for use in Surround.

    :param aparser: the parser being used
    :type aparser: <class 'argparse.ArgumentParser'>
    :param arg: the argument containing the name
    :type arg: string
    :return: the name if valid, nothing otherwise
    :rype: string
    """

    if not re.match("^[A-Za-z_]*$", arg) or not arg.islower():
        aparser.error("Name %s must be lowercase letters and underscores only" % arg)
    else:
        return arg

def load_modules_from_path(path, module_name):
    """
    Import all modules from the given directory.

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
    """
    Import class from given module.

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

def parse_lint_args(parser, args, extra_args):
    """
    Executes the "lint" sub-command which will run the Surround Linter
    on the current project.

    If the "list" argument is supplied then it will instead list the
    checks performed by the linter.

    :param args: the arguments parsed from the user
    :type args: <class 'argparse.Namespace'>
    """

    linter = Linter()
    if args.list:
        linter.dump_checks()
    elif remote_cli.get_project_root(os.path.abspath(args.path)):
        linter.check_project(args.path, extra_args, verbose=True)
    else:
        print("error: .surround does not exist")

def parse_run_args(parser, args, extra_args):
    """
    Executes the "run" sub-command which will run the surround pipeline
    as a local app or a web app (depending on the arguments provided).

    :param args: arguments parsed from the user
    :type args: <class 'argparse.Namespace'>
    """

    logging.getLogger().setLevel(logging.INFO)

    if remote_cli.is_surround_project():
        actual_current_dir = os.getcwd()
        os.chdir(remote_cli.get_project_root_from_current_dir())
        run_locally(args, extra_args)
        os.chdir(actual_current_dir)
    else:
        print("error: not a surround project")

def run_locally(args, extra_args):
    """
    Runs the surround pipeline locally executing the task provided
    (or will list tasks if none provided).

    Tasks are defined in the projects dodo.py file.

    Example tasks:
    - build - builds a docker image for the pipeline
    - dev - runs the surround pipeline in a docker container
    - prod - builds and runs the surround pipeline in a docker container (for production)
    - batch - runs the surround pipeline using the batch runner
    - web - runs the surround pipeline using the web runner (if they have it)
    - remove - deletes the docker image for this pipeline

    :param args: the arguments parsed from the user
    :type args: <class 'argparse.Namespace'>
    """

    run_args = [sys.executable, '-m', 'doit']

    if args.task:
        run_args.append(args.task)

        if extra_args:
            run_args.append("--args")
            run_args.append(" ".join([arg if " " not in arg else "\"%s\"" % arg for arg in extra_args]))
    else:
        # No arguments provided, so list the tasks available
        print("Project tasks:")
        run_args.append('list')

    run_process = subprocess.Popen(run_args)
    run_process.wait()

def parse_to_bool(bool_value):
    valid = {'true': True, 't': True, '1': True, 'false': False, 'f': False, '0': False}

    lower_value = bool_value.lower()
    if lower_value in valid:
        return valid[lower_value]
    raise ValueError('Failed parsing "%s" for boolean' % bool_value)

# pylint: disable=too-many-branches
def parse_init_args(parser, args, extra_args):
    """
    Executes the "init" sub-command which creates a new project folder with
    the name and description provided in the current directory.

    :param args: the arguments provided by the user
    :param args: <class 'argparse.Namespace'>
    """

    if allowed_to_access_dir(args.path):
        if args.project_name:
            project_name = args.project_name
        else:
            while True:
                project_name = input("Name of project: ")
                if not re.match("^[A-Za-z_]*$", project_name) or not project_name.islower():
                    print("error: project name requires lowercase letters and underscores only")
                else:
                    break

        if args.description:
            project_description = args.description
        else:
            project_description = input("What is the purpose of this project?: ")

        if args.author_name:
            author_name = args.author_name
        else:
            author_name = input("What is the author name?: ")

        if args.author_email:
            author_email = args.author_email
        else:
            author_email = input("What is the author email?: ")

        if args.require_web:
            try:
                require_web = parse_to_bool(args.require_web)
            except ValueError as e:
                print(str(e))
                sys.exit(1)
        else:
            while True:
                require_web_string = input("Does it require a web runner? (y/n) ")
                if require_web_string.lower() == "y":
                    require_web = True
                    break
                if require_web_string.lower() == "n":
                    require_web = False
                    break

        new_dir = os.path.join(args.path, project_name)
        if process(new_dir, PROJECTS["new"], project_name, project_description, author_name, author_email, require_web, "new"):
            print("info: project created at %s" % os.path.join(os.path.abspath(args.path), project_name))
        else:
            print("error: directory %s already exists" % new_dir)
    else:
        print("error: permission denied")

def print_version():
    """
    Prints the current Surround package version to the console.
    """

    print("Surround v" + pkg_resources.get_distribution("surround").version)

def execute_cli():
    """
    Uses the argparse module to parse sys.argv for sub-commands and any arguments (if required).
    Executes the appropriate command according to the arguments.

    Sub-commands:
    - init - creates a new surround project
    - run - runs a task defined in the projects dodo.py file
    - lint - runs the surround linter on the current project (see linter.py)
    - store remote - intializes a new remote
    - store add - adds a specified file to the remote
    - store pull - pulls files from the remote
    - store push - pushes files to the remote
    - store list - lists files in a remote
    - split - splits a directory/file into test/train/validate sets
    """

    parser = argparse.ArgumentParser(prog='surround', description="The Surround Command Line Interface")
    parser.add_argument('-v', '--version', action='store_true', help="Show the current version of Surround")

    sub_parser = parser.add_subparsers(description="Surround must be called with one of the following commands")

    init_parser = sub_parser.add_parser('init', help="Initialise a new Surround project")
    init_parser.add_argument('path', help="Path for creating a Surround project", nargs='?', default="./")
    init_parser.add_argument('-p', '--project-name', help="Name of the project", type=lambda x: is_valid_name(parser, x))
    init_parser.add_argument('-d', '--description', help="A description for the project")
    init_parser.add_argument('-n', '--author-name', help="A name of the author")
    init_parser.add_argument('-e', '--author-email', help="An email of the author")
    init_parser.add_argument('-w', '--require-web', help="Is web service required for the project")

    run_parser = sub_parser.add_parser('run', help="Run a Surround project task, witout an argument all tasks will be shown")
    run_parser.add_argument('task', help="Task defined in dodo.py file of your project", nargs='?')

    linter_parser = sub_parser.add_parser('lint', help="Run the Surround linter")
    linter_group = linter_parser.add_mutually_exclusive_group(required=False)
    linter_group.add_argument('-l', '--list', help="List all Surround checkers", action='store_true')
    linter_group.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path for running the Surround linter", nargs='?', default="./")

    remote_parser = remote_cli.add_store_parser(sub_parser)

    split_parser = sub_parser.add_parser('split', parents=[split_cli.get_split_parser()], add_help=False, help="Split data into train/test/validate sets")
    visualise_parser = sub_parser.add_parser('viz', parents=[visualise_cli.get_visualise_parser()], add_help=False, help="Visualise results of a pipeline")
    data_parser = sub_parser.add_parser('data', parents=[data_cli.get_data_parser()], help="Surround Data Container Tool", add_help=False)

    # Check for valid sub commands as 'add_subparsers' in Python < 3.7
    # is missing the 'required' keyword
    # Tuple format: (tool_parser, func(parser, args, extra_args))
    # Where extra_args are arguments parsed but not known to argparse
    tools = {
        "init": (init_parser, parse_init_args),
        "lint": (linter_parser, parse_lint_args),
        "run": (run_parser, parse_run_args),
        "store": (remote_parser, remote_cli.parse_store_args),
        "split": (split_parser, split_cli.execute_split_tool),
        "viz": (visualise_parser, visualise_cli.execute_visualise_tool),
        "data": (data_parser, data_cli.execute_data_tool)
    }

    try:
        if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
            parser.print_help()
        elif sys.argv[1] in ['-v', '--version']:
            print_version()
        elif len(sys.argv) < 2 or not sys.argv[1] in tools:
            print("Invalid subcommand, must be one of %s" % tools)
            parser.print_help()
        else:
            tool = sys.argv[1]
            parsed_args, extra_args = parser.parse_known_args()
            tool_parser, tool_func = tools[tool]

            tool_func(tool_parser, parsed_args, extra_args)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")

    return parser

def main():
    """
    Entry-point for the Surround Command Line Interface (CLI).
    Runs the parser and executes the appropriate operation according to the arguments given.
    """

    execute_cli()

if __name__ == "__main__":
    main()
