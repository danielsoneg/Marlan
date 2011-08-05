#!/usr/bin/env python
# Tornado
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
from tornado.options import define, options
# Base System
import os
# Ours
import auth
import text
import main
import public


define("port", default=8000, help="run on the given port", type=int)

def run():
    tornado.options.parse_command_line()
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "TmV2ZXJHZXRNZUx1dsakflhsdjY2t5Q2hhcm1z",
        "login_url": "/login",
        "debug": "true",
    }
    application = tornado.web.Application([
        (r"/login", auth.LoginHandler),
        (r"/(.+)/([^\/]+)\.txt$", text.TextHandler),
        (r'/u([\d]{5,6})/(.*?)', public.PublicHandler),
            (r"/(.*?)", main.MainHandler),
    ],**settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    run()
