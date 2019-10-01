from surround import Estimator, State, Validator


class AssemblerState(State):
    input_data = None
    output_data = None


class InputValidator(Validator):
    def validate(self, state, config):
        if not state.input_data:
            raise ValueError("'input_data' is None")

class Main(Estimator):
    def estimate(self, state, config):
        state.output_data = state.input_data

    def fit(self, state, config):
        print("TODO: Train your model here")
