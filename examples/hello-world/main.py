import logging
from surround import SurroundData, Estimator, Assembler


class HelloWorld(Estimator):
    def estimate(self, surround_data, config):
        surround_data.text = "Hello world"

    def fit(self, surround_data, config):
        print("No training implemented")


class BasicData(SurroundData):
    text = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = BasicData()
    assembler = Assembler("Hello world example", data, HelloWorld())
    assembler.run()
    print("Text is '%s'" % data.text)
