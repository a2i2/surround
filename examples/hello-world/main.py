import logging
from surround import SurroundData, Validator, Estimator, Assembler, Config


class BasicData(SurroundData):
    text: str = None


class HelloWorld(Estimator):
    def estimate(self, surround_data: BasicData, config: Config) -> None:
        surround_data.text = "Hello world"

    def fit(self, surround_data: BasicData, config: Config) -> None:
        print("No training implemented")


class ValidateData(Validator):
    def validate(self, surround_data: BasicData, config: Config) -> None:
        if surround_data.text:
            raise ValueError("'text' is not None")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = BasicData()
    assembler = Assembler("Hello world example", ValidateData(), HelloWorld())
    assembler.run(data)
    print("Text is '%s'" % data.text)
