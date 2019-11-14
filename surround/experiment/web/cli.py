import argparse
import webbrowser
import logging
import tornado
from .experiment_app import ExperimentApp

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_parser():
    parser = argparse.ArgumentParser(prog="experimentation", description="Manage the experimentation platform of Surround")
    parser.add_argument("-p", "--port", type=int, help="Port number to bind the server to (default: 45710)", default=45710)

    return parser

def execute_tool(parser, args, extra_args):
    LOGGER.info("Starting the experimentation platform server...")

    ExperimentApp().listen(args.port)

    LOGGER.info("Server started at: http://localhost:%i", args.port)
    webbrowser.open("http://localhost:%i" % args.port)

    tornado.ioloop.IOLoop.instance().start()
