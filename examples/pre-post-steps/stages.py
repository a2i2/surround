from surround import Stage, Estimator, State


class AddHello(Stage):
    def operate(self, state, config):
        state.text = "hello"


class AddWorld(Estimator):
    def estimate(self, state, config):
        state.text += " world"

    def fit(self, state, config):
        print("No training implemented")


class AddSurround(Stage):
    def operate(self, state, config):
        state.text += ", Surround"


class AssemblerState(State):
    text = None


class InputValidator(Stage):
    def operate(self, state, config):
        if state.text:
            raise ValueError("'text' is not None")
