import json
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from surround import Runner
from stages import AssemblerState

logging.basicConfig(level=logging.INFO)

class WebRunner(Runner):
    def run(self, is_training=False):
        # Setup web service
        self.assembler.init_assembler()
        self.application = Application(self.assembler)
        self.application.listen(8080)
        logging.info("Server started at http://localhost:8080")
        tornado.ioloop.IOLoop.instance().start()


class Application(tornado.web.Application):
    def __init__(self, assembler):
        handlers = [
            (r"/estimate", EstimateHandler, {'assembler': assembler}),
            (r"/info", InfoHandler, {'assembler': assembler}),
        ]
        tornado.web.Application.__init__(self, handlers)


class EstimateHandler(tornado.web.RequestHandler):
    def initialize(self, assembler):
        self.assembler = assembler
        self.data = AssemblerState()

    def post(self):
        req_data = json.loads(self.request.body)

        # Clean output_data on every request
        self.data.output_data = ""

        # Prepare input_date for the assembler
        self.data.input_data = req_data["message"]

        # Execute assembler
        self.assembler.run(self.data)
        logging.info("Message: %s", self.data.output_data)


class InfoHandler(tornado.web.RequestHandler):
    def initialize(self, assembler):
        self.assembler = assembler

    def get(self):
      self.write({'version': '0.0.1'})
