import logging
from surround import State, Validator, Estimator, Assembler


class HelloWorld(Estimator):
    def estimate(self, state, config):
        state.text = "Hello world"

    def fit(self, state, config):
        print("No training implemented")


class ValidateData(Validator):
    def validate(self, state, config):
        if state.text:
            raise ValueError("'text' is not None")


class BasicData(State):
    text = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = BasicData()
    assembler = Assembler("Hello world example", ValidateData(), HelloWorld())
    assembler.run(data)
    print("Text is '%s'" % data.text)
