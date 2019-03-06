import tornado.ioloop
import tornado.web
from tornado.escape import json_decode, json_encode


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class Predict(tornado.web.RequestHandler):
    surround = None
    data = None

    def get(self):
        self.write("hi")

    def post(self):
        print(json_decode(self.request.body))
        print(Predict.surround)
        Predict.surround.process(Predict.data)
        print(Predict.data.text)


        self.write("response")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/predict", Predict),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
