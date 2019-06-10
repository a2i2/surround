import logging
from surround import SurroundData, Validator, Estimator, Assembler


class HelloWorld(Estimator):
    def estimate(self, surround_data, config):
        surround_data.text = "Hello world"

    def fit(self, surround_data, config):
        print("No training implemented")


class ValidateData(Validator):
    def validate(self, surround_data, config):
        if surround_data.text:
            raise ValueError("'text' is not None")


class BasicData(SurroundData):
    text = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = BasicData()
    assembler = Assembler("Hello world example", ValidateData(), HelloWorld())
    assembler.run(data)
    print("Text is '%s'" % data.text)
