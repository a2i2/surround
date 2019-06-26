import logging
from surround import SurroundData, Validator, Estimator, Assembler, Visualiser, Config


class BasicData(SurroundData):
    training_message: str = None
    text: str = None


class HelloWorld(Estimator):
    def estimate(self, surround_data: BasicData, config: Config) -> None:
        if surround_data.training_message:
            surround_data.text = surround_data.training_message
        else:
            surround_data.text = "Hello world"


    def fit(self, surround_data: BasicData, config: Config) -> None:
        surround_data.training_message = "Training message"


class ValidateData(Validator):
    def validate(self, surround_data: BasicData, config: Config) -> None:
        if surround_data.text:
            raise ValueError("'text' is not None")


class Formatter(Visualiser):
    def visualise(self, surround_data: BasicData, config: Config) -> None:
        print("Visualiser result: %s" % surround_data.training_message)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = BasicData()
    assembler = Assembler("Training example", ValidateData(), HelloWorld())
    assembler.init_assembler(True)
    assembler.set_visualiser(Formatter())

    # Run assembler before training
    assembler.run(data)
    print("Text before training is '%s'" % data.text)
    data.text = None    # Clear text to prevent validation raising error

    # Run training mode
    assembler.run(data, True)

    # Run assembler after training
    assembler.run(data)
    print("Text after training is '%s'" % data.text)
