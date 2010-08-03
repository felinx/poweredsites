#!/usr/bin/env python2.6
#
# Copyright(c) 2010 poweredsites.org
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
os.environ["PYTHON_EGG_CACHE"] = "/tmp/egg"

import tornado
from tornado import web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import options

try:
    import poweredsites
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from poweredsites.libs.utils import parse_config_file

class Application(web.Application):
    def __init__(self):
        from poweredsites.urls import handlers, sub_handlers, ui_modules

        settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=options.xsrf_cookies,
            cookie_secret=options.cookie_secret,
            login_url=options.login_url,
            static_url_prefix=options.static_url_prefix,

            ui_modules=ui_modules,

            # auth secret
            twitter_consumer_key=options.twitter_consumer_key,
            twitter_consumer_secret=options.twitter_consumer_secret,
            friendfeed_consumer_key=options.friendfeed_consumer_key,
            friendfeed_consumer_secret=options.friendfeed_consumer_secret,
            facebook_api_key=options.facebook_api_key,
            facebook_secret=options.facebook_secret,
        )
        super(Application, self).__init__(handlers, **settings)

        # add handlers for sub domains
        for sub_handler in sub_handlers:
            # host pattern and handlers
            self.add_handlers(sub_handler[0], sub_handler[1])

def main():
    parse_config_file("/mnt/ebs/conf/sites/poweredsites.conf")
    tornado.options.parse_command_line()

    http_server = HTTPServer(Application(), xheaders=True)
    port = options.port
    num_processes = options.num_processes

    if options.debug:
        num_processes = 1

    if options.chat_app:
        port = getattr(options, "chat_app_port", options.port + 1)
        num_processes = 1

    http_server.bind(int(port))
    http_server.start(int(num_processes))

    IOLoop.instance().start()

if __name__ == "__main__":
    main()
