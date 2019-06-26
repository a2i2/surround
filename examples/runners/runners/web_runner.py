import json
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from surround import Runner, Assembler
from .stages import RunnersData

logging.basicConfig(level=logging.INFO)

class WebRunner(Runner):
    def run(self, is_training: bool = False) -> None:
        self.assembler.init_assembler()
        self.application: Application = Application(self.assembler)
        self.application.listen(8080)
        logging.info("Server started at http://localhost:8080")
        tornado.ioloop.IOLoop.instance().start()


class Application(tornado.web.Application):
    def __init__(self, assembler: Assembler) -> None:
        handlers = [
            (r"/message", MessageHandler, {'assembler': assembler})
        ]
        tornado.web.Application.__init__(self, handlers)


class MessageHandler(tornado.web.RequestHandler):
    def initialize(self, assembler: Assembler) -> None:
        self.assembler: Assembler = assembler
        self.data: RunnersData = RunnersData()

    def post(self) -> None:
        req_data = json.loads(self.request.body)

        # Clean output_data on every request
        self.data.output_data = ""

        # Prepare input_date for the assembler
        self.data.input_data = req_data["message"]

        # Execute assembler
        self.assembler.run(self.data)
        logging.info("Message: %s", self.data.output_data)
