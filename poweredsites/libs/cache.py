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

import hashlib
from datetime import datetime, timedelta
from decorator import decorator
from tornado.escape import utf8
from tornado.options import options

from poweredsites.libs.handler import BaseHandler
from poweredsites.db.caches import Page, Cache
from poweredsites.db import conn

__all__ = ("cache", "page", "mem", "key_gen", "remove")

_mem_caches = {}

def cache(expire=7200, condition="", key="", anonymous=False):
    """Decorator which caches the value of a method in a handler or a module.    
    
    expire: Cache will be expired time from now in seconds.
    condition: If the result of sql condition has changed, then cache expired. 
    key: The unique key of the cache identify in the DB 
    
    cache_pre: A method which is defined in self(handler or module), 
                it always be executed before cache or get from cache.
                
    cache_condition: A property which is defined in self(handler or module), it
                is used to construct a complex condition.
    """
    def wrapper(func, self, *args, **kwargs):
        now = datetime.now()
        if key:
            c = key
        else:
            c = self.__class__.__name__ + func.__name__
        k, handler, cond = key_gen(self, condition, anonymous, c, *args, **kwargs)

        value = Cache().findby_key(k)
        new_cond = {}

        if _valid_cache(value, handler, cond, new_cond, anonymous, now):
            if new_cond:
                c = Cache()
                c.key = k
                c.condition = new_cond["condition"]
                c.save(value["_id"])
            return value["value"]
        else:
            val = func(self, *args, **kwargs)

            c = Cache()
            # need key, or save will not work
            c.key = k
            c.value = val
            c.expire = now + timedelta(seconds=expire)
            c.condition = new_cond.get("condition", "")

            if value:
                c.save(value["_id"])
            else:
                c.insert()

            return val

    return decorator(wrapper)

def page(expire=7200, condition="", key="", anonymous=False):
    """Decorator which caches a whole page(headers + html) in a handler
    
    expire: Cache will be expired time from now in seconds.   
    condition: If the result of sql condition has changed, then cache expired.
    key: The unique key of the cache identify in the DB 
    
    """
    def wrapper(func, self, *args, **kwargs):
        now = datetime.now()
        if key:
            c = key
        else:
            c = self.__class__.__name__ + func.__name__
        k, handler, cond = key_gen(self, condition, anonymous, c, *args, **kwargs)

        value = Cache().findby_key(k)
        new_cond = {}

        is_valid = _valid_cache(value, handler, cond, new_cond, anonymous, now)
        if is_valid and value["status"] in (200, 304):
            if new_cond:
                c = Page()
                c.key = k
                c.condition = new_cond["condition"]
                c.save(value["_id"])

            # finish request with cache chunk and headers
            self.set_status(value["status"])
            self.set_header("Content-Type", utf8(value["headers"]["Content-Type"]))
            self.write(utf8("".join(value["chunk"])))
        else:
            func(self, *args, **kwargs)

            c = Page()
            c.key = k
            c.status = self._status_code
            c.headers = self._headers
            c.chunk = self._write_buffer
            c.expire = now + timedelta(seconds=expire)
            c.condition = new_cond.get("condition", "")

            if value:
                c.save(value["_id"])
            else:
                c.insert()

    return decorator(wrapper)

def mem(expire=7200, key=""):
    """Mem cache to python dict by key"""
    def wrapper(func, self, *args, **kwargs):
        now = datetime.now()
        if key:
            c = key
        else:
            c = self.__class__.__name__ + func.__name__
        k, handler, cond = key_gen(self, "", False, c, *args, **kwargs)

        value = _mem_caches.get(k, None)
        if _valid_cache(value, handler, cond, [], False, now):
            return value["value"]
        else:
            val = func(self, *args, **kwargs)
            _mem_caches[k] = {"value":val, "expire":now}

            return val

    return decorator(wrapper)

def key_gen(self, condition, anonymous, key, *args, **kwargs):
    code = hashlib.md5()

    code.update(str(key))

    # copy args to avoid sort original args
    c = list(args[:])
    # sort c to avoid generate different key when args is the same
    # but sequence is different
    c.sort()
    c = [str(v) for v in c]
    code.update("".join(c))

    c = ["%s=%s" % (k, v) for k, v in kwargs]
    c.sort()
    code.update("".join(c))

    if isinstance(self, BaseHandler):
        handler = self
    else:
        handler = getattr(self, "handler")

    # execute cache_pre before get cache_condition
    # so we can construct a complex condition.
    cache_pre = getattr(self, "cache_pre", None)
    if cache_pre:
        cache_pre(*args, **kwargs)

    if not condition:
        condition = getattr(self, "cache_condition", "")

    # also update condition to key, so the same func 
    # has diff caches if there condition is diff(cache_condtion)
    code.update(str(condition))

    # cache for every users if anonymous is False
    if not anonymous and handler.current_user:
        # add userid= prefix to avoid key conflict
        # (eg. siteid + userid maybe equal another siteid)
        code.update(str("userid=%s" % handler.current_user.id))

    # page argument as key by default
    # Todo: add a argument option for key gen like condition
    page = handler.get_argument("page", "")
    if page:
        code.update(str("page=%s" % page))

    # cache for different host(the same uri may have different subdomain)
    code.update(handler.request.host)

    return code.hexdigest(), handler, condition

def remove(key):
    """Remove a cache's value."""
    c = Cache()
    v = c.findby_key(key)
    if v:
        c.remove(v["_id"])

def _valid_cache(value, handler, condition, new_condtion, anonymous, now):
    if not options.cache_enabled:
        return False

    if anonymous and handler.current_user:
        return False

    if condition:
        old_cond = value.get("condition", "") if value else ""
        rows = conn.mysql.query(condition)

        new_cond = ""
        for r in rows:
            new_cond += str(r)

        # unify to utf8, the string result return by pymongo is unicode
        new_cond = utf8(new_cond)
        old_cond = utf8(old_cond if old_cond else "")

        print "old_cond:", old_cond
        print "new_cond:", new_cond
        if old_cond != new_cond:
            new_condtion["condition"] = new_cond
            return False

    if value:
        if value["expire"] > now:
            return True
        else:
            return False
    else:
        return False
