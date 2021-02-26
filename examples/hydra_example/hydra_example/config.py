from dataclasses import dataclass
from surround import BaseConfig, config

@config(name="config")
@dataclass
class Config(BaseConfig):
    # Docker image configuration
    company: str = "a2i2"
    image: str = "hudra_example"
    version: str = "latest"

    # Pipeline configuration
    runner: str = "0"
    assembler: str = "baseline"

    # Pipeline run configuration
    mode: str = "predict"
    status: bool = False
