import pkg_resources

from .run_modes import RunMode
from .surround import Surround
from .state import State
from .config import Config, has_config
from .stage import Stage, Estimator
from .assembler import Assembler
from .runners import Runner

__version__ = pkg_resources.get_distribution("surround").version
