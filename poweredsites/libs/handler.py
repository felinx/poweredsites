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

import re
import httplib
import urllib
import traceback

from tornado.web import RequestHandler, HTTPError
from tornado.options import options
from tornado import template, ioloop, escape

from poweredsites.libs import mail, const
from poweredsites.libs.exceptions import TemplateContextError
from poweredsites import db
from poweredsites.db.access import Access, logging_access_job

class BaseHandler(RequestHandler):
    _first_running = True
    db = None

    def __init__(self, application, request, **kwargs):
        if BaseHandler._first_running:
            self._after_prefork()
            BaseHandler._first_running = False

        super(BaseHandler, self).__init__(application, request, **kwargs)

    def _after_prefork(self):
        #### initialize jobs after forking        
        # Connect to mongodb and mysql        
        db.connect()
        # Setup a global mysql connection across all handlers
        BaseHandler.db = db.conn.mysql

        # logging access routine
        ioloop.PeriodicCallback(logging_access_job, int(options.access_log["interval"]) * 1000).start()

    def get_current_user(self):
        username = self.get_secure_cookie("user")
        if not username:
            return None

        return self.db.get("select * from user where username = %s", username)

    def prepare(self):
        self._prepare_context()
        self._remove_slash()

    def render_string(self, template_name, **kwargs):
        """Override default render_string, add context to template."""
        assert "context" not in kwargs, "context is a reserved word for \
                template context valuable."
        kwargs['context'] = self._context
        kwargs['url_escape'] = escape.url_escape

        return super(BaseHandler, self).render_string(template_name, **kwargs)

    def flush(self, include_footers=False):
        """Flushes the current output buffer to the network."""
        if self.application._wsgi:
            raise Exception("WSGI applications do not support flush()")

        chunk = "".join(self._write_buffer)
        # keep write buffer for cache
        # self._write_buffer = []
        if not self._headers_written:
            self._headers_written = True
            for transform in self._transforms:
                self._headers, chunk = transform.transform_first_chunk(
                    self._headers, chunk, include_footers)
            headers = self._generate_headers()
        else:
            for transform in self._transforms:
                chunk = transform.transform_chunk(chunk, include_footers)
            headers = ""

        # Ignore the chunk and only write the headers for HEAD requests
        if self.request.method == "HEAD":
            if headers: self.request.write(headers)
            return

        if headers or chunk:
            self.request.write(headers + chunk)

    def get_error_html(self, status_code, **kwargs):
        """Override to implement custom error pages.

        It will send email notification to admins if debug is off when internal 
        server error happening.
        
        """
        code = status_code
        message = httplib.responses[status_code]
        exception = kwargs["exception"]

        if options.debug:
            template = "%s_debug.html" % code
            # add exception stack trace for debug
            exception = traceback.format_exc()
        else:
            template = "%s.html" % code

            # comment send email for ec2 limit
#            if code == 500:
#                fr = options.email_from
#                to = options.admins
#
#                subject = "[%s]Internal Server Error" % options.sitename
#                body = self.render_string("500_email.html",
#                                      code=code,
#                                      message=message,
#                                      exception=exception)
#
#                self.send_email(fr, to, subject, body)
        try:
            return self.render_string(template,
                                      code=code,
                                      message=message,
                                      exception=exception)
        except Exception:
            return super(BaseHandler, self).get_error_html(status_code, **kwargs)

    def send_email(self, fr, to, subject, body):
        to = to.split(";")
        to_addr = []
        for t in to:
            t = t.split(":")
            try:
                if len(t) == 1:
                    to_addr.append(mail.Address(t[0]))
                else:
                    to_addr.append(mail.Address(t[0], t[1]))
            except AssertionError:
                pass

        if to_addr:
            mail.send_email(fr, to_addr, subject, body)

    @property
    def is_admin(self):
        return self.current_user.role >= const.Role.ADMIN if self.current_user else False

    @property
    def is_staff(self):
        return self.current_user.role >= const.Role.STAFF if self.current_user else False

    def _prepare_context(self):
        self._context = _Context()
        self._context.css = ['base.css', ]
        self._context.js = ['base.js', ]
        self._context.title = options.title
        self._context.keywords = options.keywords
        self._context.description = options.description
        self._context.project_name = options.sitename
        self._context.project_slogan = options.project_slogan
        self._context.current_project = None
#        self._context.current_logo = options.logo
        self._context.options = options

    def _remove_slash(self):
        if self.request.method == "GET":
            if _remove_slash_re.match(self.request.path):
                # remove trail slash in path
                uri = self.request.path.rstrip("/")
                if self.request.query:
                    uri += "?" + self.request.query

                self.redirect(uri)

    def _request_summary(self):
        if options.access_log["on"] and self.request.method == "GET":
            Access().logging_access(self)

        return super(BaseHandler, self)._request_summary()


class AdminBaseHandler(BaseHandler):
    """Administrator base handler.
    
    It's a shortcut of decorators.admin for every method(get, post, head etc),
    so we need not write decorators.admin everywhere.
    
    """
    def prepare(self):
        if not self.current_user:
            if self.request.method == "GET":
                url = self.get_login_url()
                if "?" not in url:
                    url += "?" + urllib.urlencode(dict(next=self.request.full_url()))
                self.redirect(url)
                return
            raise HTTPError(403)
        elif not self.is_admin:
            if self.request.method == "GET":
                self.redirect(options.home_url)
                return
            raise HTTPError(403)
        else:
            pass

        super(AdminBaseHandler, self).prepare()


class StaffBaseHandler(BaseHandler):
    """Administrator base handler.
    
    It's a shortcut of decorators.staff.
        
    """
    def prepare(self):
        if not self.current_user:
            if self.request.method == "GET":
                url = self.get_login_url()
                if "?" not in url:
                    url += "?" + urllib.urlencode(dict(next=self.request.full_url()))
                self.redirect(url)
                return
            raise HTTPError(403)
        elif not self.is_staff:
            if self.request.method == "GET":
                self.redirect(options.home_url)
                return
            raise HTTPError(403)
        else:
            pass

        super(StaffBaseHandler, self).prepare()


class ErrorHandler(BaseHandler):
    """Default 404: Not Found handler."""
    def prepare(self):
        super(ErrorHandler, self).prepare()
        raise HTTPError(404)


class _Context(dict):
    """Template context container.
    
    A container which will return empty string silently if the key is not exist
    rather than raise AttributeError when get a item's value.
    
    It will raise TemplateContextError if debug is True and the key 
    does not exist.   
    
    The context item also can be accessed through get attribute. 
    
    """
    def __setattr__(self, key, value):
        self[key] = value

    def __str__(self):
        return str(self)

    def __iter__(self):
        return iter(self.items())

    def __getattr__(self, key):
        """Get a context attribute.
        
        Raise TemplateContextError if the attribute not be set to
        avoid confused AttributeError exception when debug is True, or return ""
        
        """
        if key in self:
            return self[key]
        elif options.debug:
            raise TemplateContextError("'%s' does not exist in context" % key)
        else:
            return ""

    def __hasattr__(self, key):
        if key in self:
            return True
        else:
            return False


_remove_slash_re = re.compile(".+/$")
