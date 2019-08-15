from surround import Validator, Estimator, State


class RunnersData(State):
    input_data = None
    output_data = ""


class InputValidator(Validator):
    def validate(self, state, config):
        if not state.input_data:
            raise ValueError("'input_data' is None")


class HelloWorld(Estimator):
    def estimate(self, state, config):
        state.output_data += state.input_data

    def fit(self, state, config):
        print("TODO: Building models")
