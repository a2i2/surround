import pkg_resources

from .surround import Surround
from .state import State
from .stage import Validator, Filter, Estimator
from .visualiser import Visualiser
from .config import Config, has_config
from .assembler import Assembler
from .runners import Runner, RunMode

__version__ = pkg_resources.get_distribution("surround").version
