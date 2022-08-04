from surround import Assembler, load_config
from .stages import InputValidator, HelloWorld
from .batch_runner import BatchRunner
from .config import Config


def main():
    assembler = Assembler(
        "Default project", config=load_config(config_class=Config)
    ).set_stages([InputValidator(), HelloWorld()])

    # Example for running batch processing
    BatchRunner(assembler).run()

    # Web Runner example
    # WebRunner(assembler).run()


if __name__ == "__main__":
    main()
