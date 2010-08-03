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
import urlparse
import formencode
from formencode import htmlfill, validators

class BaseForm(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    _xsrf = validators.PlainText(not_empty=True, max=32)

    def __init__(self, handler):

        self._parmas = {}
        self._values = {}
        self._form_errors = {}
        arguments = {}

        # re-parse qs, keep_blank_values for formencode to validate
        # so formencode not_empty setting work.
        request = handler.request
        content_type = request.headers.get("Content-Type", "")

        if request.method == "POST":
            if content_type.startswith("application/x-www-form-urlencoded"):
                arguments = urlparse.parse_qs(request.body, keep_blank_values=1)

        for k, v in arguments.iteritems():
            if len(v) == 1:
                self._parmas[k] = v[0]
            else:
                # keep a list of values as list (or set)
                self._parmas[k] = v

        self._handler = handler
        self._result = True

    def validate(self):
        try:
            self._values = self.to_python(self._parmas)
            self._result = True
            self.__after__()
        except formencode.Invalid, error:
            self._values = error.value
            self._form_errors = error.error_dict or {}
            self._result = False

        return self._result

    # add custom error msg
    def add_error(self, attr, msg):
        self._result = False
        self._form_errors[attr] = msg

    def render(self, template_name, **kwargs):
        html = self._handler.render_string(template_name, **kwargs)
        if not self._result:
            html = htmlfill.render(
                                   html,
                                   defaults=self._values,
                                   errors=self._form_errors,
                                   encoding="utf8",
            )
        self._handler.finish(html)

    # post process hook
    def __after__(self):
        pass


class URL(validators.URL):
    url_re = re.compile(r'''
        ^(http|https)://
        (?:[%:\w]*@)?                           # authenticator
        (?P<domain>[a-z0-9][a-z0-9\-]{0,62}\.)* # (sub)domain - alpha followed by 62max chars (63 total)
        (?P<tld>[a-z]{2,})                      # TLD
        (?::[0-9]+)?                            # port

        # files/delims/etc
        (?P<path>/[a-z0-9\-\._~:/\?#\[\]@!%\$&\'\(\)\*\+,;=]*)?
        $
    ''', re.I | re.VERBOSE)
