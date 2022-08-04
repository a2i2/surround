PROJECTS = {
    "new": {
        "dirs": [
            ".surround",
            "input",
            "output",
            "notebooks",
            "{project_name}",
            "{project_name}/stages",
            "tests",
        ],
        "files": [
            (".surround/config.yaml", "project-info:\n  project-name: {project_name}")
        ],
        "templates": [
            # File name, template name, capitalize project name, is web component
            ("README.md", "README.md.txt", False, False),
            ("{project_name}/stages/__init__.py", "stages_init.py.txt", False, False),
            (
                "{project_name}/stages/assembler_state.py",
                "assembler_state.py.txt",
                False,
                False,
            ),
            ("{project_name}/stages/baseline.py", "baseline.py.txt", False, False),
            (
                "{project_name}/stages/input_validator.py",
                "input_validator.py.txt",
                False,
                False,
            ),
            (
                "{project_name}/file_system_runner.py",
                "file_system_runner.py.txt",
                False,
                False,
            ),
            ("{project_name}/config.py", "config.py.txt", False, False),
            ("{project_name}/web_runner.py", "web_runner.py.txt", False, True),
            ("{project_name}/__main__.py", "batch_main.py.txt", False, False),
            ("{project_name}/__main__.py", "web_main.py.txt", False, True),
            ("{project_name}/__init__.py", "init.py.txt", False, False),
            ("notebooks/data_analysis.ipynb", "data_analysis.ipynb.txt", False, False),
            ("dodo.py", "dodo.py.txt", False, False),
            ("dodo.py", "web_dodo.py.txt", False, True),
            ("Dockerfile", "Dockerfile.txt", False, False),
            ("Dockerfile.Notebook", "Dockerfile.Notebook.txt", False, False),
            ("{project_name}/config.yaml", "config.yaml.txt", False, False),
            (".gitignore", ".gitignore.txt", False, False),
            ("VERSION", "VERSION.txt", False, False),
            ("pyproject.toml", "pyproject.txt", False, False),
        ],
    }
}
