# pylint: disable=E0611, W0603, R0903
import logging
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from surround import Runner, RunMode
from .stages import AssemblyState

APP = FastAPI()

# Global variable to store the assembler instance (so FastAPI endpoint handlers can access it).
ASSEMBLER = None

logging.basicConfig(level=logging.INFO)


class WebRunner(Runner):

    def load_data(self, mode, config):
        return None

    def run(self, mode=RunMode.PREDICT):
        self.assembler.init_assembler()
        global ASSEMBLER

        # Get the Config instance from the Assembler.
        ASSEMBLER = self.assembler
        uvicorn.run(
            APP, port=8080, log_level="info"
        )


class MessageInput(BaseModel):
    message: str


class MessageOutput(BaseModel):
    output: str


@APP.post("/message", response_model=MessageOutput)
def post_message(request_input: MessageInput):
    # Prepare input_data for the assembler
    data = AssemblyState()
    data.output_data = ""
    data.input_data = request_input.message

    # Execute assembler
    ASSEMBLER.run(data)
    logging.info("Message: %s", data.output_data)
    return MessageOutput(output=data.output_data)


class VersionOutput(BaseModel):
    version: str


@APP.get("/info", response_model=VersionOutput)
def get_info():
    return VersionOutput(version="0.0.1")
