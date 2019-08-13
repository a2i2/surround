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
            # File name, template name, capitalize project name, is web component
            ("README.md", "README.md.txt", False, False),
            ("{project_name}/stages.py", "stages.py.txt", True, False),
            ("{project_name}/batch_runner.py", "batch_runner.py.txt", True, False),
            ("{project_name}/web_runner.py", "web_runner.py.txt", True, True),
            ("{project_name}/__main__.py", "batch_main.py.txt", True, False),
            ("{project_name}/__main__.py", "web_main.py.txt", True, True),
            ("{project_name}/__init__.py", "init.py.txt", True, False),
            ("dodo.py", "dodo.py.txt", False, False),
            ("dodo.py", "web_dodo.py.txt", False, True),
            ("Dockerfile", "Dockerfile.txt", False, False),
            ("{project_name}/config.yaml", "config.yaml.txt", False, False),
            (".gitignore", ".gitignore.txt", False, False)
        ]
    }
}
