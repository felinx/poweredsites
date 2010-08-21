# -*- coding: utf-8 -*-
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

import uuid
import re
import hashlib
from datetime import datetime, timedelta

import tornado.auth
from tornado.web import asynchronous, HTTPError
from tornado.options import options
from tornado import escape

from poweredsites.libs.handler import BaseHandler
from poweredsites.libs import const
from poweredsites.db.caches import Cache
from poweredsites.libs.decorators import cache
from poweredsites.libs.decorators import authenticated
from poweredsites.forms.profile import ProfileForm

_chinese_character_re = re.compile(u"[\u4e00-\u9fa5]")


class LoginHandler(BaseHandler):
    def get(self):
        next = self.get_argument("next", options.home_url)
        if next.startswith(options.login_url):
            self.redirect("/login")
            return

        self._context.next = next

        self._context.title = "OpenID login"
        self.render("user/login.html", url_escape=escape.url_escape)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user", domain=options.cookie_domain)
        self.redirect(self.get_argument("next", "/"))


class OpenidLoginHandler(BaseHandler):
    _error_message = "OpenID auth failed!"

    def _cache_next(self):
        now = datetime.now()
        key = self._next_key_gen()
        val = self.get_argument("next", "/")

        c = Cache()
        c.key = key
        c.value = val
        c.expire = now + timedelta(seconds=600)

        value = c.findby_key(key)
        if value:
            c.save(value["_id"])
        else:
            c.insert()

    def _next_key_gen(self):
        code = hashlib.md5()

        # make a unique id for a un-logined user
        # it may be duplicated for different users
        code.update("user/next")
        code.update(self.request.remote_ip)
        code.update(self.request.headers.get("User-Agent", "Unknown-Agent"))
        code.update(self.request.headers.get("Accept-Language", "en-us,en;q=0.5"))

        return code.hexdigest()

    @asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self._cache_next()
        self.authenticate_redirect()

    def _login(self, user):
        self.db.execute(
                "UPDATE user SET login_ip = %s, login_date = UTC_TIMESTAMP(), login_c = %s "
                "WHERE id = %s", self.request.remote_ip, user.login_c + 1, user.id)

        self.set_secure_cookie("user", user.username, domain=options.cookie_domain)

    def _create_user(self, openid_api, openid_id, openid_name, email, username):
        self.db.execute("INSERT INTO user (openid_api,openid_id,openid_name,email,username,"
                    "signup_ip,login_ip,signup_date,login_date,uuid_) "
                    "VALUES (%s,%s,%s,%s,%s,"
                    "%s,%s,UTC_TIMESTAMP(),UTC_TIMESTAMP(),%s)",
                    openid_api, openid_id, openid_name, email, username,
                    self.request.remote_ip, self.request.remote_ip, uuid.uuid4().hex
                    )

        self.set_secure_cookie("user", username, domain=options.cookie_domain)

    def _login_redirect(self, status_):
        key = self._next_key_gen()

        c = Cache()
        value = c.findby_key(key)
        if value:
            next = escape.utf8(value["value"])
            c.remove(value["_id"])
        else:
            next = "/"

        #next = self.get_argument("next", "/")
        if status_ == const.Status.INIT:
            self.redirect("/user/profile?next=%s" % next)
        else:
            self.redirect(next)


class FacebookLoginHandler(OpenidLoginHandler, tornado.auth.FacebookMixin):
    _error_message = "Facebook auth failed!"

    @asynchronous
    def get(self):
        if self.get_argument("session", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self._cache_next()
        self.authenticate_redirect()

    def _on_auth(self, openid):
        if not openid:
            raise HTTPError(500, self._error_message)

        user = self.db.get("select * from user where openid_api = %s and openid_id = %s",
                           const.OpenID.FACEBOOK, openid["uid"])

        if user:
            status_ = user.status_
            user.openid_name = openid["name"]

            self._login(user)
        else:
            status_ = const.Status.INIT
            try:
                # try to use default account name as username (fb username -> username)
                username = openid["username"].replace(".", "_").lower()
                self._create_user(const.OpenID.FACEBOOK, openid["uid"], openid["name"], None, username)
            except Exception:
                username = uuid.uuid4().hex # Generate one randomly
                self._create_user(const.OpenID.FACEBOOK, openid["uid"], openid["name"], None, username)

        self._login_redirect(status_)


class FriendfeedLoginHandler(OpenidLoginHandler, tornado.auth.FriendFeedMixin):
    _error_message = "Friendfeed auth failed!"

    @asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self._cache_next()
        self.authorize_redirect()

    def _on_auth(self, openid):
        if not openid:
            raise HTTPError(500, self._error_message)

        user = self.db.get("select * from user where openid_api = %s and openid_id = %s",
                           const.OpenID.FRIENDFEED, openid["username"])

        if user:
            status_ = user.status_
            user.openid_name = openid["name"]

            self._login(user)
        else:
            status_ = const.Status.INIT
            try:
                # try to use default account name as username (ff id -> username)
                username = openid["username"].lower()
                self._create_user(const.OpenID.FRIENDFEED, openid["username"], openid["name"], None, username)
            except Exception:
                username = uuid.uuid4().hex # Generate one randomly
                self._create_user(const.OpenID.FRIENDFEED, openid["username"], openid["name"], None, username)

        self._login_redirect(status_)


class GoogleLoginHandler(OpenidLoginHandler, tornado.auth.GoogleMixin):
    _error_message = "Google auth failed!"

    def _on_auth(self, openid):
        if not openid:
            raise HTTPError(500, self._error_message)

        # update openid information
        if _chinese_character_re.match(openid["name"]):
            openid["name"] = openid["last_name"] + openid["first_name"]

        user = self.db.get("select * from user where email = %s", openid["email"])

        if user:
            status_ = user.status_
            user.openid_id = openid["name"]
            user.openid_name = openid["name"]

            self._login(user)
        else:
            status_ = const.Status.INIT
            try:
                # try to use default account name as username
                username = openid["email"].split("@")[0].replace(".", "_").lower()
                self._create_user(const.OpenID.GOOGLE, openid["name"], openid["name"], openid["email"], username)
            except Exception:
                username = uuid.uuid4().hex # Generate one randomly
                self._create_user(const.OpenID.GOOGLE, openid["name"], openid["name"], openid["email"], username)

        self._login_redirect(status_)


class TwitterLoginHandler(OpenidLoginHandler, tornado.auth.TwitterMixin):
    _error_message = "Twitter auth failed!"

    @asynchronous
    def get(self):
        if self.get_argument("oauth_token", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self._cache_next()
        self.authorize_redirect()

    def _on_auth(self, openid):
        if not openid:
            raise HTTPError(500, self._error_message)

        user = self.db.get("select * from user where openid_api = %s and openid_id = %s",
                           const.OpenID.TWITTER, openid["username"])

        if user:
            status_ = user.status_
            user.openid_name = openid["name"]

            self._login(user)
        else:
            status_ = const.Status.INIT
            try:
                # try to use default account name as username (twitter screen_name -> username)
                username = openid["username"].lower()
                self._create_user(const.OpenID.TWITTER, openid["username"], openid["name"], None, username)
            except Exception:
                username = uuid.uuid4().hex # Generate one randomly
                self._create_user(const.OpenID.TWITTER, openid["username"], openid["name"], None, username)

        self._login_redirect(status_)


class ProfileHandler(BaseHandler):
    @authenticated
    def get(self):
        self._context.js.append("user.js")
        self._context.next = self.get_argument("next", "/")
        self._context.title = "Edit profile"
        self._context.openid_name = const.OpenID.NAME[self.current_user.openid_api]

        if self.current_user.email is None:
            self.current_user.email = ""

        if self.current_user.blog_name is None:
            self.current_user.blog_name = ""

        if self.current_user.blog_url is None:
            self.current_user.blog_url = ""

        self.render("user/profile.html", const=const)

    @authenticated
    def post(self):
        fm = ProfileForm(self)
        self._context.openid_name = const.OpenID.NAME[self.current_user.openid_api]
        next = escape.url_unescape(fm._parmas.get("next", ""))
        if not next:
            next = "/"
        self._context.next = next

        if fm.validate():
            self.redirect(self._context.next)
        else:
            fm.render("user/profile.html", const=const)


class UserCheckHandler(BaseHandler):
    @authenticated
    def post(self):
        email = self.request.arguments.get("email", False)
        username = self.request.arguments.get("username", False)
        r = {"r" : 1}

        if email:
            user = self.db.get("select id from user where email = %s", email[0])
            if user and user.id != self.current_user.id:
                r["r"] = 0
            else:
                r["r"] = 1
        elif username:
            user = self.db.get("select id from user where username = %s", username[0])
            if user and user.id != self.current_user.id:
                r["r"] = 0
            else:
                r["r"] = 1

        self.write(r)


class UserHandler(BaseHandler):
    @cache.page(anonymous=True)
    def get(self, username):
        user = self.db.get("select * from user where username = %s" , username)
        if not user:
            raise HTTPError(404)

        sites = self.db.query("select * from site where user_id = %s order by id DESC", user.id)
        self._context.title = user.openid_name + " submitted sites"
        self._context.keywords = ",".join((user.openid_name, user.username, self._context.keywords))
        self._context.description = ",".join((self._context.title, self._context.options.domain))
        self.render("user/user.html", sites=sites, user=user)


handlers = [
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/login/google", GoogleLoginHandler),
            (r"/login/facebook", FacebookLoginHandler),
            (r"/login/twitter", TwitterLoginHandler),
            (r"/login/friendfeed", FriendfeedLoginHandler),
            (r"/user/profile", ProfileHandler),
            (r"/user/check", UserCheckHandler),
            (r"/user/([a-z0-9\-_]{3,32})", UserHandler),
            ]
