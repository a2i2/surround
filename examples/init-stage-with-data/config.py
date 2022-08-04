from dataclasses import dataclass
from omegaconf import MISSING
from surround import BaseConfig, config


@config(name="config")
@dataclass
class Config(BaseConfig):
    path_to_hello_world: str = MISSING
