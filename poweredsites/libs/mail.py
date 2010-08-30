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

from datetime import datetime, timedelta
import re
import logging
import smtplib
from email.MIMEText import MIMEText

from tornado.escape import utf8
from tornado.options import options

__all__ = ("send_email", "Address")

_session = None

# borrow email re pattern from django
_email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain

def send_email(fr, to, subject, body):
    msg = MIMEText(utf8(body))
    msg.set_charset('utf8')
    msg['To'] = utf8(to)
    msg['From'] = utf8(fr)
    msg['Subject'] = utf8(subject)

    global _session
    if _session is None:
        _session = _SMTPSession(options.smtp['host'],
                       options.smtp['user'],
                       options.smtp['password'],
                       options.smtp['duration'])

    _session.send_mail(fr, to, msg.as_string())


class Address(object):
    def __init__(self, addr, name=""):
        assert _email_re.match(addr), "Email address(%s) is invalid." % addr

        self.addr = addr
        if name:
            self.name = name
        else:
            self.name = addr.split("@")[0]

    def __str__(self):
        return '%s <%s>' % (self.name, self.addr)


class _SMTPSession(object):
    def __init__(self, host, user='', password='', duration=30):
        self.host = host
        self.user = user
        self.password = password
        self.duration = duration

        self.renew()

    def send_mail(self, fr, to, message):
        if self.timeout:
            self.renew()

        try:
            self.session.sendmail(fr, to, message)
        except Exception, e:
            err = "Send email from %s to %s failed!\n Exception: %s!" \
                % (fr, to, e)
            logging.error(err)

    @property
    def timeout(self):
        if datetime.now() < self.deadline:
            return False
        else:
            return True

    def renew(self):
        try:
            self.session.quit()
        except Exception:
            pass

        self.session = smtplib.SMTP(self.host)
        if self.user and self.password:
            self.session.login(self.user, self.password)

        self.deadline = datetime.now() + timedelta(seconds=self.duration * 60)
