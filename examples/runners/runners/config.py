from dataclasses import dataclass
from omegaconf import MISSING
from surround import BaseConfig, config


@config
@dataclass
class Config(BaseConfig):
    image: str = MISSING
    company: str = MISSING
    version: str = MISSING
