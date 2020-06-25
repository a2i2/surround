from surround import Assembler
from .stages import InputValidator, HelloWorld
from .batch_runner import BatchRunner


def main():
    assembler = Assembler("Default project").set_stages([InputValidator(), HelloWorld()])

    # Example for running batch processing
    BatchRunner(assembler).run()

    # Web Runner example
    # WebRunner(assembler).run()


if __name__ == "__main__":
    main()
