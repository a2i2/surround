# pylint: disable=E0611, R0903
import logging
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from surround import Runner, RunMode
from .stages import AssemblyState


class APIHelper:
    assembler = None


APP = FastAPI()
HELPER = APIHelper()
logging.basicConfig(level=logging.INFO)


class WebRunner(Runner):

    def load_data(self, mode, config):
        return None

    def run(self, mode=RunMode.PREDICT):
        self.assembler.init_assembler()
        HELPER.assembler = self.assembler
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
    HELPER.assembler.run(data)
    logging.info("Message: %s", data.output_data)
    return MessageOutput(output=data.output_data)


class VersionOutput(BaseModel):
    version: str


@APP.get("/info", response_model=VersionOutput)
def get_info():
    return VersionOutput(version="0.0.1")
