import datetime
import os
import tornado.ioloop
import tornado.web
import pkg_resources
from surround import AllowedTypes

# Get time for uptime calculation.
START_TIME = datetime.datetime.now()

class HealthCheck(tornado.web.RequestHandler):
    def get(self):
        print("info: started get request at /")
        self.write(dict(
            app="Surround Server",
            version=pkg_resources.get_distribution("surround").version,
            uptime=str(datetime.datetime.now() - START_TIME)
        ))
        print("info: finished get request at /")

class Upload(tornado.web.RequestHandler):
    def get_template_path(self):
        return os.getcwd()

    def get(self):
        print("info: started get request at /upload")
        self.render("upload.html")
        print("info: finished get request at /upload")

class Predict(tornado.web.RequestHandler):
    def initialize(self, wrapper):
        self.wrapper = wrapper

    def post(self):
        print("info: started post request at /predict")
        if self.wrapper.type_of_uploaded_object == AllowedTypes.IMAGE:
            fileinfo = self.request.files['data'][0]
            self.wrapper.process(fileinfo['body'])
        else:
            self.wrapper.process(None)
        self.write("Task executed successfully")
        print("info: finished post request at /predict")

def make_app(wrapper_object):
    predict_init_args = dict(wrapper=wrapper_object)

    return tornado.web.Application([
        (r"/", HealthCheck),
        (r"/upload", Upload),
        (r"/predict", Predict, predict_init_args),
    ])
