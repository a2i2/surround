import logging
from surround import Assembler
from .stages import RunnersData, HelloWorld
from .runners import SingleRunner, BatchRunner
from .web_runner import WebRunner

logging.basicConfig(level=logging.INFO)

def main():
    data = RunnersData()
    assembler = Assembler("Default project", data, HelloWorld())

    # Example for running single process
    SingleRunner(assembler).run()
    logging.info("Single Runner: %s", data.output_data)

    # Example for running batch processing
    data.output_data = ""
    BatchRunner(assembler).run()
    logging.info("Batch Runner: %s", data.output_data)

    # Web Runner example
    # data.output_data = ""
    # WebRunner(assembler).run()

if __name__ == "__main__":
    main()
