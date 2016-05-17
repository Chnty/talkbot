#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.api import urlfetch
import webapp2
from urllib2 import urlopen
from urllib import urlencode

TOKEN = open('bot.token').read()
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

class SetWebHookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urlopen(BASE_URL + 'setWebhook', urlencode({'url': url})))))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello worlddeggfkhfkhrp!')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
