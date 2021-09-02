import logging
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from surround import Runner, RunMode
from .stages import AssemblerState

app = FastAPI()
logging.basicConfig(level=logging.INFO)


class WebRunner(Runner):

    def load_data(self, mode, config):
        return None

    def run(self, mode=RunMode.PREDICT):
        self.assembler.init_assembler()
        global assembler

        # Get the Config instance from the Assembler.
        assembler = self.assembler
        config = assembler.config
        uvicorn.run(
            app, port=8080, log_level="info"
        )


class EstimateBody(BaseModel):
    message: str


@app.post("/message")
def post_message(body: EstimateBody):
    # Prepare input_data for the assembler
    data = AssemblerState(body.message)

    # Execute assembler
    assembler.run(data)
    logging.info("Message: %s", data.output_data)
    return {"output": data.output_data}


@app.get("/info")
def get_info():
    return {"version": "0.0.1"}
