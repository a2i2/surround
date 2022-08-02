"""
This module is responsible for serving the pipeline via HTTP endpoints.
"""

# pylint: disable=E0611, R0903
import logging
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from surround import Runner, RunMode
from .stages import AssemblerState


class APIHelper:
    assembler = None


APP = FastAPI()
HELPER = APIHelper()
logging.basicConfig(level=logging.INFO)


class WebRunner(Runner):

    def load_data(self, mode, config):
        return None

    def run(self, mode=RunMode.PREDICT):
        # Setup web service
        self.assembler.init_assembler()
        HELPER.assembler = self.assembler
        uvicorn.run(
            APP, host="0.0.0.0", port=8080, log_level="info"
        )


class EstimateInput(BaseModel):
    message: str


class EstimateOutput(BaseModel):
    output: str


@APP.post("/estimate", response_model=EstimateOutput)
def post_estimate(request_input: EstimateInput):
    # Prepare input data for the assembler
    data = AssemblerState(request_input.message)

    # Execute assembler
    HELPER.assembler.run(data)
    logging.info("Message: %s", data.output_data)
    return EstimateOutput(output=data.output_data)


class VersionOutput(BaseModel):
    version: str


@APP.get("/info", response_model=VersionOutput)
def get_info():
    return VersionOutput(version="0.0.1")
