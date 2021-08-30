from dataclasses import dataclass
from surround import config, BaseConfig

@dataclass
class Loader:
    input: str = "data/input.csv"
    output: str = "data/output.csv"

@dataclass
class ProcessCSV:
    include_company: bool = True

@config(name="config")
@dataclass
class Config(BaseConfig):
    loader: Loader = Loader()
    process_csv: ProcessCSV = ProcessCSV()
