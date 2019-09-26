from surround import Assembler
from .stages import InputValidator, HelloWorld
from .batch_runner import BatchRunner
# pylint: disable=unused-import
from .web_runner import WebRunner

def main():
    assembler = Assembler("Default project").set_validator(InputValidator()).set_estimator(HelloWorld())

    # Example for running batch processing
    BatchRunner(assembler).run()

    # Web Runner example
    # WebRunner(assembler).run()

if __name__ == "__main__":
    main()
