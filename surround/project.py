PROJECTS = {
    "new" : {
        "dirs" : [
            ".surround",
            "input",
            "output",
            "docs",
            "models",
            "notebooks",
            "scripts",
            "{project_name}",
            "{project_name}/stages",
            "spikes",
            "templates",
            "tests",
        ],
        "files": [
            ("requirements.txt", "surround=={version}"),
            (".surround/config.yaml", "project-info:\n  project-name: {project_name}")
        ],
        "templates" : [
            # File name, template name, capitalize project name, is web component
            ("README.md", "README.md.txt", False, False),
            ("{project_name}/stages/__init__.py", "stages_init.py.txt", False, False),
            ("{project_name}/stages/assembler_state.py", "assembler_state.py.txt", False, False),
            ("{project_name}/stages/baseline.py", "baseline.py.txt", False, False),
            ("{project_name}/stages/input_validator.py", "input_validator.py.txt", False, False),
            ("{project_name}/stages/report_generator.py", "report_generator.py.txt", False, False),
            ("{project_name}/file_system_runner.py", "file_system_runner.py.txt", False, False),
            ("{project_name}/web_runner.py", "web_runner.py.txt", False, True),
            ("{project_name}/__main__.py", "batch_main.py.txt", False, False),
            ("{project_name}/__main__.py", "web_main.py.txt", False, True),
            ("{project_name}/__init__.py", "init.py.txt", False, False),
            ("notebooks/example.ipynb", "example.ipynb.txt", False, False),
            ("notebooks/example.ipynb", "example.ipynb.txt", False, True),
            ("templates/results.html", "results.html.txt", False, False),
            ("templates/results.html", "results.html.txt", False, True),
            ("dodo.py", "dodo.py.txt", False, False),
            ("dodo.py", "web_dodo.py.txt", False, True),
            ("Dockerfile", "Dockerfile.txt", False, False),
            ("{project_name}/config.yaml", "config.yaml.txt", False, False),
            (".gitignore", ".gitignore.txt", False, False)
        ]
    }
}
