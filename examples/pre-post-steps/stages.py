from surround import Filter, Estimator, SurroundData, Validator, Config


class BasicData(SurroundData):
    text: str = None


class AddHello(Filter):
    def operate(self, surround_data: BasicData, config: Config) -> None:
        surround_data.text = "hello"


class AddWorld(Estimator):
    def estimate(self, surround_data: BasicData, config: Config) -> None:
        surround_data.text += " world"

    def fit(self, surround_data: BasicData, config: Config) -> None:
        print("No training implemented")


class AddSurround(Filter):
    def operate(self, surround_data: BasicData, config: Config) -> None:
        surround_data.text += ", Surround"


class ValidateData(Validator):
    def validate(self, surround_data, config) -> None:
        if surround_data.text:
            raise ValueError("'text' is not None")
