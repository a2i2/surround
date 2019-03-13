import tornado.ioloop
import tornado.web

class HealthCheck(tornado.web.RequestHandler):
    def get(self):
        self.write("OK!")

class Predict(tornado.web.RequestHandler):
    def initialize(self, wrapper):
        self.wrapper = wrapper

    def post(self):
        self.wrapper.run()
        self.write("Task executed successfully")

def make_app(wrapper_object):
    predict_init_args = dict(wrapper=wrapper_object)

    return tornado.web.Application([
        (r"/", HealthCheck),
        (r"/predict", Predict, predict_init_args),
    ])
