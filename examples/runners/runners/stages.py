from surround import Validator, Estimator, SurroundData, Config


class RunnersData(SurroundData):
    input_data: str = None
    output_data: str = ""


class ValidateData(Validator):
    def validate(self, surround_data: RunnersData, config: Config) -> None:
        if not surround_data.input_data:
            raise ValueError("'input_data' is None")


class HelloWorld(Estimator):
    def estimate(self, surround_data: RunnersData, config: Config) -> None:
        surround_data.output_data += surround_data.input_data

    def fit(self, surround_data: RunnersData, config: Config) -> None:
        print("TODO: Building models")
