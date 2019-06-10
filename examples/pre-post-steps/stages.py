from surround import Filter, Estimator, SurroundData, Validator


class AddHello(Filter):
    def operate(self, surround_data, config):
        surround_data.text = "hello"


class AddWorld(Estimator):
    def estimate(self, surround_data, config):
        surround_data.text += " world"

    def fit(self, surround_data, config):
        print("No training implemented")


class AddSurround(Filter):
    def operate(self, surround_data, config):
        surround_data.text += ", Surround"


class BasicData(SurroundData):
    text = None


class ValidateData(Validator):
    def validate(self, surround_data, config):
        if surround_data.text:
            raise ValueError("'text' is not None")
