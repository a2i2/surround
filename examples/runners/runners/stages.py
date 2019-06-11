from surround import Validator, Estimator, SurroundData


class RunnersData(SurroundData):
    input_data = None
    output_data = ""


class ValidateData(Validator):
    def validate(self, surround_data, config):
        if not surround_data.input_data:
            raise ValueError("'input_data' is None")


class HelloWorld(Estimator):
    def estimate(self, surround_data, config):
        surround_data.output_data += surround_data.input_data

    def fit(self, surround_data, config):
        print("TODO: Building models")
