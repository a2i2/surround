import logging

import tornado.ioloop

from surround import Stage, SurroundData, Surround, Config, test

class HelloSurround(Stage):

    def __init__(self):
        self.data = None

    def init_stage(self, config):
        file_ = open(config.get_path("surround.path_to_HelloSurround"), "r")
        self.data = file_.read()

    def operate(self, surround_data, config):
        print(self.data)

class HelloWorld(Stage):

    def __init__(self):
        self.data = None

    def init_stage(self, config):
        file_ = open(config.get_path("surround.path_to_HelloWorld"), "r")
        self.data = file_.read()

    def operate(self, surround_data, config):
        print(self.data)

class BasicData(SurroundData):
    text = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    surround = Surround([HelloSurround(), HelloWorld()])
    surround_config = Config()
    surround_config.read_config_files(["temp/init-stage-with-data/config.yaml"])
    surround.set_config(surround_config)
    surround.init_stages()
    # surround.process(BasicData())

    test.Predict.surround = surround
    test.Predict.data = BasicData()

    app = test.make_app()
    app.listen(8889)
    tornado.ioloop.IOLoop.current().start()

