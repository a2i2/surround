"""
Main entry-point for the Surround project.
Runners and ASSEMBLIES are defined in here.
"""

import os
import hydra
from surround import Surround, Assembler
from .config import Config
from .stages import Baseline, InputValidator
from .file_system_runner import FileSystemRunner
from .web_runner import WebRunner

RUNNERS = [
    WebRunner(),
    FileSystemRunner()
]

ASSEMBLIES = [
    Assembler("baseline")
        .set_stages([InputValidator(), Baseline()])
]

@hydra.main(config_name="config")
def main(config: Config):
    surround = Surround(
        RUNNERS,
        ASSEMBLIES,
        config,
        "web_runner_sample",
        "Web runner sample",
        os.path.dirname(os.path.dirname(__file__))
    )

    if config.status:
        surround.show_info()
    else:
        surround.run(config.runner, config.assembler, config.mode)

if __name__ == "__main__":
    main(None)
