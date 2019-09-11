import logging
from surround import State, Validator, Estimator, Assembler


class HelloWorld(Estimator):
    def estimate(self, state, config):
        state.text = "Hello world"

    def fit(self, state, config):
        print("No training implemented")


class InputValidator(Validator):
    def validate(self, state, config):
        if state.text:
            raise ValueError("'text' is not None")


class AssemblerState(State):
    text = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = AssemblerState()
    assembler = Assembler("Hello world example").set_validator(InputValidator()).set_estimator(HelloWorld())
    assembler.run(data)
    print("Text is '%s'" % data.text)
