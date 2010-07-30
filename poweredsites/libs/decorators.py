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

import functools
import urllib
from tornado.web import HTTPError

from poweredsites.libs import cache # cache decorator alias

def admin(method):
    """Decorate with this method to restrict to site admins."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method == "GET":
                self.redirect(self.get_login_url())
                return
            raise HTTPError(403)
        elif not self.is_admin:
            if self.request.method == "GET":
                self.redirect("/")
                return
            raise HTTPError(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper

def staff(method):
    """Decorate with this method to restrict to site staff."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method == "GET":
                self.redirect(self.get_login_url())
                return
            raise HTTPError(403)
        elif not self.is_staff:
            if self.request.method == "GET":
                self.redirect("/")
                return
            raise HTTPError(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper


def authenticated(method):
    """Decorate methods with this to require that the user be logged in.
    
    Fix the redirect url with full_url. 
    Tornado use uri by default.
    
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method == "GET":
                url = self.get_login_url()
                if "?" not in url:
                    url += "?" + urllib.urlencode(dict(next=self.request.full_url()))
                self.redirect(url)
                return
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper
