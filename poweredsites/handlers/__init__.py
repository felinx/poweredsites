## -*- coding: utf-8 -*-
##
## Copyright(c) 2010 poweredsites.org
##
## Licensed under the Apache License, Version 2.0 (the "License"); you may
## not use this file except in compliance with the License. You may obtain
## a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
## WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
## License for the specific language governing permissions and limitations
## under the License.
#
#import os
#import traceback
#
#from poweredsites.libs.importlib import import_module
#from poweredsites.libs.utils import find_models
#
#handlers = []
#sub_handlers = []
#
#def _setup():
#    mds = find_models(os.path.dirname(__file__))
#    for m in mds:
#        try:
#            if m != "power":
#                mod = import_module("." + m, package="poweredsites.handlers")
#                hds = getattr(mod, "handlers", None)
#                if hds is not None:
#                    handlers.extend(hds)
#
#                hds = getattr(mod, "sub_handlers", None)
#                if hds is not None:
#                    sub_handlers.extend(hds)
#        except Exception:
#            raise
#
#    try:
#        # power should be the last one, so custom subdomin work
#        mod = import_module(".power", package="poweredsites.handlers")
#        hds = getattr(mod, "handlers", None)
#        if hds is not None:
#            handlers.extend(hds)
#    except Exception:
#        raise
#
#_setup()
