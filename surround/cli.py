import argparse
import os
import sys

PROJECTS = {
    "new" : {
        "dirs" : [
            "data",
            "data/output",
            "data/input",
            "docs",
            "models",
            "notebooks",
            "scripts",
            "{project_name}",
            "spikes",
            "tests",
        ],
        "files": [
            ("requirements.txt", "surround==0.1"),
            ("{project_name}/config.yaml", "output:\n  text: Hello World")
        ],
        "templates" : [
            ("README.md", "README.md.txt", False),
            ("{project_name}/stages.py", "stages.py.txt", True),
            ("{project_name}/__main__.py", "main.py.txt", True)
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
        path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        with open(os.path.join(path, "templates", folder, template)) as f:
            contents = f.read()
            name = project_name.capitalize() if capitalize else project_name
            actual_contents = contents.format(project_name=name, project_description=project_description)
            file_path = os.path.join(project_dir, actual_file)
        with open(file_path, 'w') as f:
            f.write(actual_contents)

def process(path, project, project_name, project_description, folder):
    project_dir = os.path.join(path, project_name)
    os.makedirs(project_dir)
    process_directories(project["dirs"], project_dir, project_name)
    process_files(project["files"], project_dir, project_name, project_description)
    process_templates(project["templates"], folder, project_dir, project_name, project_description)

def is_valid_dir(aparser, arg):
    if not os.path.isdir(arg) or not os.access(arg, os.W_OK | os.X_OK):
        aparser.error("Invalid directory or can't write to %s" % arg)
    else:
        return arg


def main():

    parser = argparse.ArgumentParser(prog='surround', description="The Surround Command Line Interface")
    sub_parser = parser.add_subparsers(description="Surround must be called with one of the following commands")
    init_parser = sub_parser.add_parser('init', help="Initialiser for new Surround projects")
    init_parser.add_argument('path', type=lambda x: is_valid_dir(parser, x), help="Path for creating a Surround project")
    init_parser.add_argument('-t', '--tutorial', help="Create the Surround tutorial project", action='store_true')

    # Check for valid sub commands as 'add_subparsers' in Python < 3.7
    # is missing the 'required' keyword
    tools = ["init"]
    if len(sys.argv) < 2 or not sys.argv[1] in tools:
        print("Invalid subcommand, must be one of %s" % tools)
        parser.print_help()
    else:
        value = parser.parse_args()
        if value.tutorial:
            process(value.path, PROJECTS["new"], "tutorial", None, "tutorial")
        else:
            while True:
                project_name = input("Name of project: ")
                if not project_name.isalpha() or not project_name.islower():
                    print("Project name requires lowercase letters only")
                else:
                    break
            project_description = input("What is the purpose of this project?: ")
            process(value.path, PROJECTS["new"], project_name, project_description, "new")

if __name__ == "__main__":
    main()
