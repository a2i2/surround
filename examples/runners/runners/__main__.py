from surround import Assembler
from .stages import ValidateData, HelloWorld
from .batch_runner import BatchRunner
# pylint: disable=unused-import
from .web_runner import WebRunner

def main() -> None:
    assembler = Assembler("Default project", ValidateData(), HelloWorld())

    # Example for running batch processing
    BatchRunner(assembler).run()

    # Web Runner example
    # WebRunner(assembler).run()

if __name__ == "__main__":
    main()
