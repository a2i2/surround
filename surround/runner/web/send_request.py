import tornado.httpclient
from tornado import gen
import tornado.options

@tornado.gen.coroutine
def json_fetch(http_client, body):
    response = yield http_client.fetch("http://localhost:8888/predict", method='POST', body=body)
    raise gen.Return(response)

@tornado.gen.coroutine
def request():
    body = '{"endpoint": "predict"}'
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_response = yield json_fetch(http_client, body)
    print(http_response.body)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.instance().run_sync(request)
