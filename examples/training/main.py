import logging

from surround import State, Estimator, Assembler, Stage, RunMode


class HelloWorld(Estimator):
    def estimate(self, state, config):
        if state.training_message:
            state.text = state.training_message
        else:
            state.text = "Hello world"

    def fit(self, state, config):
        state.training_message = "Training message"


class AssemblerState(State):
    training_message = None
    text = None


class Formatter(Stage):
    def visualise(self, state, config):
        print("Visualiser result: %s" % state.training_message)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = AssemblerState()
    assembler = Assembler("Training example")
    assembler.set_stages([HelloWorld(), Formatter()])
    assembler.init_assembler()

    # Run assembler before training
    assembler.run(data, RunMode.TRAIN)
    print("Text before training is '%s'" % data.text)
    data.text = None  # Clear text to prevent validation raising error

    # Run training mode
    assembler.run(data)

    # Run assembler after training
    assembler.run(data)
    print("Text after training is '%s'" % data.text)
