import argparse
import webbrowser
import logging
import tornado
from .experiment_app import ExperimentApp
from ..util import get_surround_config

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_parser():
    config = get_surround_config()

    parser = argparse.ArgumentParser(prog="experimentation", description="Manage the experimentation platform of Surround")
    parser.add_argument("-u", "--url", type=str, help="The storage location", default=config.get_path("experiment.url"))
    parser.add_argument("-p", "--port", type=int, help="Port number to bind the server to (default: 45710)", default=45710)

    return parser

def execute_tool(parser, args, extra_args):
    LOGGER.info("Starting the experimentation platform server...")

    ExperimentApp(args.url).listen(args.port)

    LOGGER.info("Server started at: http://localhost:%i", args.port)
    webbrowser.open("http://localhost:%i" % args.port)

    tornado.ioloop.IOLoop.instance().start()
