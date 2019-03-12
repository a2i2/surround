import os
import subprocess

from surround.linter import Linter

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/12'

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
            ("requirements.txt", "surround==0.0.2"),
            ("{project_name}/config.yaml", "output:\n  text: Hello World"),
            (".surround/config.yaml", "project-info:\n  project-name: {project_name}")
        ],
        "templates" : [
            # File name, template name, capitalize project name
            ("README.md", "README.md.txt", False),
            ("{project_name}/stages.py", "stages.py.txt", True),
            ("{project_name}/__main__.py", "main.py.txt", True),
            ("dodo.py", "dodo.py.txt", False)
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
        actual_content = content.format(project_name=project_name, project_description=project_description)
        file_path = os.path.join(project_dir, actual_file)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(actual_content)

def process_templates(templates, folder, project_dir, project_name, project_description):
    for afile, template, capitalize in templates:
        actual_file = afile.format(project_name=project_name, project_description=project_description)
        path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
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

def add_tutorial_parser(parser, sub_parser):
    tutorial_parser = sub_parser.add_parser('tutorial', help="Create the tutorial project")
    tutorial_parser.add_argument('tutorial', help="Create the Surround tutorial project", action='store_true')
    tutorial_parser.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path for creating the tutorial project", nargs='?', default="./")

def add_init_parser(parser, sub_parser):
    init_parser = sub_parser.add_parser('init', help="Initialise a new Surround project")
    init_parser.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path for creating a Surround project", nargs='?', default="./")
    init_parser.add_argument('-p', '--project-name', help="Name of the project", type=lambda x: is_valid_name(parser, x))
    init_parser.add_argument('-d', '--description', help="A description for the project")

def add_run_parser(parser, sub_parser):
    run_parser = sub_parser.add_parser('run', help="Run a Surround project task, witout an argument all tasks will be shown")
    run_parser.add_argument('task', help="Task defined in a Surround project dodo.py file.", nargs='?')
    run_parser.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path to a Surround project", nargs='?', default="./")

def add_linter_parser(parser, sub_parser):
    linter_parser = sub_parser.add_parser('lint', help="Run the Surround linter")
    linter_group = linter_parser.add_mutually_exclusive_group(required=False)
    linter_group.add_argument('-l', '--list', help="List all Surround checkers", action='store_true')
    linter_group.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path for running the Surround linter", nargs='?', default="./")

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
    deploy = {
        "new": {
            "dirs": [
                "models",
                "{project_name}",
            ],
            "files" : [
                ("{project_name}/config.yaml", "output:\n  text: Hello World"),
                ("dodo.py", "")
            ]
        }
    }

    path = args.path
    errors, warnings = Linter().check_project(deploy, path)
    if errors:
        print("Invalid Surround project")
    for e in errors + warnings:
        print(e)
    if not errors:
        print("Project tasks:")
        if args.task:
            task = args.task
        else:
            task = 'list'
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
