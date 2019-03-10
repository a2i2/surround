import tornado.httpclient
import json
from tornado.escape import json_decode, json_encode
from tornado import gen
import tornado.options


@tornado.gen.coroutine  
def json_fetch(http_client, body):
    response = yield http_client.fetch("http://localhost:8889/predict", method='POST', body=body)
    raise gen.Return(response)

@tornado.gen.coroutine
def request():
    body = '{"test_json": "ok"}'
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_response = yield json_fetch(http_client, body)
    print(http_response.body)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    tornado.ioloop.IOLoop.instance().run_sync(request)
