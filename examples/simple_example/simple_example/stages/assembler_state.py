"""
This module defines the state object that is passed between each stage
in the pipeline.
"""

from surround import State


class AssemblerState(State):
    def __init__(self, input_data):
        super().__init__()
        self.input_data = input_data
        self.output_data = None
