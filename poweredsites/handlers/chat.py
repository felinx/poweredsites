#!/usr/bin/env python
#
# Copyright 2009 Facebook
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

import logging
import uuid
from tornado.web import authenticated, asynchronous, HTTPError

from poweredsites.libs.handler import BaseHandler
from poweredsites.libs.decorators import cache


class ChatBaseHandler(BaseHandler):
    def prepare(self):
        super(ChatBaseHandler, self).prepare()
        self._context.title = "PoweredSites' chat online"
        self._context.keywords = self._context.keywords + ",chat"

class MainHandler(ChatBaseHandler):
    @cache.page()
    def get(self):
        projects = self.db.query("select * from project order by subdomain ASC")
        self.render("chat/projects.html", projects=projects)


class MessageMixin(object):
    waiters = {}
    cache = {}
    cache_size = 200

    def get_messages(self, project):
        cls = MessageMixin
        if not cls.cache.get(project, None):
            cls.cache[project] = []
        cache = cls.cache[project]

        messages = cache
        if not messages:
            messages = self.db.query("select * from messages where project = %s limit 0, 200", project)
            if messages:
                messages = [{"id":m.uuid_, "from":m.from_, "body":m.body} for m in messages]
                cache = messages

        return messages

    def wait_for_messages(self, callback, project, cursor=None):
        cls = MessageMixin

        if not cls.cache.get(project, None):
            cls.cache[project] = []
        cache = cls.cache[project]

        if not cls.waiters.get(project, None):
            cls.waiters[project] = []
        waiters = cls.waiters[project]

        if cursor:
            index = 0
            for i in xrange(len(cache)):
                index = len(cache) - i - 1
                if cache[index]["id"] == cursor: break
            recent = cache[index + 1:]
            if recent:
                callback(recent)
                return
        waiters.append(callback)

    def new_messages(self, project, messages):
        cls = MessageMixin
        if not cls.cache.get(project, None):
            cls.cache[project] = []
        cache = cls.cache[project]

        if not cls.waiters.get(project, None):
            cls.waiters[project] = []
        waiters = cls.waiters[project]

        logging.info("Sending new message to %r listeners", len(waiters))

        for callback in waiters:
            try:
                callback(messages)
            except:
                logging.error("Error in waiter callback", exc_info=True)
        waiters = []
        cache.extend(messages)
        if len(cache) > self.cache_size:
            cache = cache[-self.cache_size:]


class ChatHandler(ChatBaseHandler, MessageMixin):
    @authenticated
    def get(self, project):
        if not project.islower():
            self.redirect("http://chat.poweredsites.org/%s" % project.lower())

        project = self.db.get("select * from project where subdomain = %s", project)
        if not project:
            raise HTTPError(404)

        self._context.current_project = project
        self._context.title = project.project + " chat online"
        self._context.keywords = self._context.keywords + ",%s,%s" % (project.subdomain, project.project)
        self.render("chat/index.html", messages=self.get_messages(project.subdomain))

class MessageNewHandler(BaseHandler, MessageMixin):
    @authenticated
    def post(self, project):
        body = self.get_argument("body")
        uuid_ = str(uuid.uuid4().hex)
        from_ = self.current_user.openid_name
        message = {
            "id": uuid_,
            "from": from_,
            "body": body,
        }
        message["html"] = self.render_string("chat/message.html", message=message)
        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)

        self.db.execute("INSERT INTO messages (uuid_, from_, user_id, project, body, "
                        "created) VALUES (%s, %s, %s, %s, %s, UTC_TIMESTAMP)",
                        uuid_, from_, self.current_user.id, project, body
                        )

        self.new_messages(project, [message])


class MessageUpdatesHandler(BaseHandler, MessageMixin):
    @authenticated
    @asynchronous
    def post(self, project):
        cursor = self.get_argument("cursor", None)
        self.wait_for_messages(self.async_callback(self.on_new_messages),
                               project=project, cursor=cursor)

    def on_new_messages(self, messages):
        # Closed client connection
        if self.request.connection.stream.closed():
            return
        self.finish(dict(messages=messages))

sub_handlers = ["^chat.poweredsites.org$",
                [
                 (r"/?", MainHandler),
                 (r"/([a-zA-Z\-_0-9]{3,20})$", ChatHandler),
                 (r"/([a-zA-Z\-_0-9]{3,20})/a/message/new", MessageNewHandler),
                 (r"/([a-zA-Z\-_0-9]{3,20})/a/message/updates", MessageUpdatesHandler),
                 ],
                ]
