from enum import Enum


class RunMode(Enum):
    BATCH_PREDICT = 1
    PREDICT = 2
    TRAIN = 3