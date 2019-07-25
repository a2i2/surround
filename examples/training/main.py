import logging
from surround import State, Validator, Estimator, Assembler, Visualiser


class HelloWorld(Estimator):
    def estimate(self, state, config):
        if state.training_message:
            state.text = state.training_message
        else:
            state.text = "Hello world"


    def fit(self, state, config):
        state.training_message = "Training message"


class ValidateData(Validator):
    def validate(self, state, config):
        if state.text:
            raise ValueError("'text' is not None")


class BasicData(State):
    training_message = None
    text = None


class Formatter(Visualiser):
    def visualise(self, state, config):
        print("Visualiser result: %s" % state.training_message)


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
