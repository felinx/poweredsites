#!/usr/bin/env python
#
# Blog module borrows from tornado blog demo and modifies a little 
# for powerdsites.org(eg. wmd editor). It also be used to edit help pages.
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

import re
import markdown
import unicodedata
import uuid
from tornado.web import HTTPError, UIModule

from poweredsites.libs.handler import BaseHandler
from poweredsites.libs.decorators import staff, cache
from poweredsites.libs import const

class BlogBaseHandler(BaseHandler):
    def prepare(self):
        super(BlogBaseHandler, self).prepare()
        self._context.title = "PoweredSites' Blog"
        self._context.keywords = self._context.keywords + ", blog"
        self._context.is_help = False

    @property
    @cache.mem(6 * 3600, "blog/bloggers")
    def bloggers(self):
        return self.db.query("select * from user where role >= %s", const.Role.STAFF)

class HomeHandler(BlogBaseHandler):
    @cache.page(condition="select id from entries ORDER BY id DESC")
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY id "
                                "DESC LIMIT 20")
        self.render("blog/home.html", entries=entries)


class EntryHandler(BlogBaseHandler):
    @cache.page(anonymous=True)
    def get(self, slug):
        entry = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
        if not entry: raise HTTPError(404)

        if entry.is_help and not self.is_staff:
            self.redirect("/")

        self._context.title = entry.title
        self._context.description = entry.content[0:200]
        self.render("blog/entry.html", entry=entry)


class ArchiveHandler(BlogBaseHandler):
    @cache.page(condition="select id from entries ORDER BY id DESC")
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY id DESC")
        self._context.title = "PoweredSites' Archive Blog | poweredsites.org"
        self.render("blog/archive.html", entries=entries)


class FeedHandler(BlogBaseHandler):
    @cache.page(condition="select id from entries ORDER BY id DESC")
    def get(self):
        entries = self.db.query("SELECT * FROM entries where is_help = 0 ORDER BY created "
                                "DESC LIMIT 10")
        self.set_header("Content-Type", "application/atom+xml")
        self.render("blog/feed.xml", entries=entries, title="PoweredSites Blog!")


class ComposeHandler(BlogBaseHandler):
    @staff
    def get(self):
        self._context.css.append("markedit.css")
        id = self.get_argument("id", None)
        entry = None
        if id:
            entry = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))

        self._context.title = "Compose Blog"
        self.render("blog/compose.html", entry=entry)

    @staff
    def post(self):
        id = self.get_argument("id", None)
        title = self.get_argument("title")
        text = self.get_argument("content")
        html = markdown.markdown(text)
        if id:
            entry = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
            if not entry: raise HTTPError(404)
            slug = entry.slug
            self.db.execute(
                "UPDATE entries SET user_id = %s, title = %s, content = %s, markdown = %s "
                "WHERE id = %s", self.current_user.id, title, text, html, int(id))
            if entry.is_help:
                self.redirect(self._context.options.home_url + "help/" + slug)
        else:
            slug = unicodedata.normalize("NFKD", title).encode(
                "ascii", "ignore")
            slug = re.sub(r"[^\w]+", " ", slug)
            slug = "-".join(slug.lower().strip().split())
            if not slug: slug = "entry"
            while True:
                e = self.db.get("SELECT * FROM entries WHERE slug = %s", slug)
                if not e: break
                slug += "-" + uuid.uuid4().hex[0:2]
            self.db.execute(
                "INSERT INTO entries (user_id,title,slug,content,markdown,"
                "created) VALUES (%s,%s,%s,%s,%s,UTC_TIMESTAMP())",
                self.current_user.id, title, slug, text, html)

        self.redirect("/entry/" + slug)


class EntryModule(UIModule):
    def render(self, entry):
        print entry
        return self.render_string("modules/entry.html", entry=entry)


sub_handlers = ["^blog.poweredsites.org$",
                [
                (r"/", HomeHandler),
                (r"/archive", ArchiveHandler),
                (r"/feeds", FeedHandler),
                (r"/entry/([^/]+)", EntryHandler),
                (r"/compose", ComposeHandler),
                ]
                ]

ui_modules = {"entry":EntryModule,
              }
