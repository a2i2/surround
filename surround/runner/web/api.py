import subprocess
import tornado.ioloop
import tornado.web

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/08'

class Predict(tornado.web.RequestHandler):
    task = None
    path = None

    def post(self):
        subprocess.Popen(['python3', '-m', 'doit', Predict.task], cwd=Predict.path)
        self.write("Task executed successfully")

def make_app():
    return tornado.web.Application([
        (r"/predict", Predict),
    ])
