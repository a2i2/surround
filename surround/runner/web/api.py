import datetime
import os
import tornado.ioloop
import tornado.web
import pkg_resources
from surround import AllowedTypes

# Get time for uptime calculation.
START_TIME = datetime.datetime.now()

class HealthCheck(tornado.web.RequestHandler):
    """
    Class which handles the health check HTTP GET web endpoint ("/").
    """

    def get(self):
        """
        Called when endpoint is requested via GET method.
        Responds with a JSON document containing the app name, version and server uptime.
        """

        self.write(dict(
            app="Surround Server",
            version=pkg_resources.get_distribution("surround").version,
            uptime=str(datetime.datetime.now() - START_TIME)
        ))

class Upload(tornado.web.RequestHandler):
    """
    Class which handles the upload HTTP GET web endpoint ("/upload").
    """

    def get_template_path(self):
        """
        Returns the path to the folder containing the upload.html file.

        :return: path to the folder
        :rtype: str
        """

        path_to_upload_dir = os.path.split(__file__)[0]
        return path_to_upload_dir

    def get(self):
        """
        Called when endpoint is requested via GET method.
        Renders the upload.html file in the user's browser.

        The form in `upload.html` POST's to the :class:`Predict` endpoint.
        """

        self.render("upload.html")

class Predict(tornado.web.RequestHandler):
    """
    Class which handles the predict HTTP POST web endpoint ("/predict").
    """

    def initialize(self, wrapper):
        """
        Called when the endpoint is initialized, keeps a
        reference to the pipeline wrapper.

        :param wrapper: the wrapper for the surround pipeline
        :type wrapper: :class:`surround.Wrapper`
        """

        self.wrapper = wrapper

    def post(self):
        """
        Called when data has been posted to the web endpoint.
        Processes the uploaded data using the pipeline and responds with the output.
        """

        output = None
        if self.wrapper.type_of_uploaded_object == AllowedTypes.FILE:
            fileinfo = self.request.files['data'][0]
            output = self.wrapper.process(fileinfo['body'])
        else:
            output = self.wrapper.process(self.request.body)
        self.write({"output": output})

def make_app(wrapper_object):
    """
    Creates a web-server with the following endpoints:

    - `/` - HTTP GET - responds with the Surround version and current uptime (see :class:`HealthCheck`)
    - `/upload` - HTTP GET - used to upload a file and run the pipeline on the file (see :class:`Upload`)
    - `/predict` - HTTP POST - runs the pipeline on the data in the body of the request (see :class:`Predict`)

    .. note:: This function is called by the Surround CLI.

    :param wrapper_object: the wrapper for the surround pipeline
    :type wrapper_object: :class:`surround.Wrapper`
    :return: the web-server application object
    :rtype: :class:`tornado.web.Application`
    """

    predict_init_args = dict(wrapper=wrapper_object)
    available_endpoints = []
    available_endpoints.append((r"/", HealthCheck))

    if wrapper_object.type_of_uploaded_object == AllowedTypes.FILE:
        available_endpoints.append((r"/upload", Upload))

    available_endpoints.append((r"/predict", Predict, predict_init_args))
    return tornado.web.Application(available_endpoints)
