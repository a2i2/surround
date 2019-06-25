import pkg_resources

from .surround import SurroundData
from .stage import Validator, Filter, Estimator
from .visualiser import Visualiser
from .config import Config
from .assembler import Assembler
from .runners import Runner

__version__ = pkg_resources.get_distribution("surround").version
