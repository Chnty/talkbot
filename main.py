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
import json
import logging
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


class WebHookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None):
            if msg:
                resp = urlopen(BASE_URL + 'sendMessage', urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': 'true',
                })).read()
            else:
                logging.error('no msg specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
            if text == '/help':
                reply('nope')
            else:
                reply('What command?')

        elif 'who are you' in text:
            reply('CHNTY IS MY MASTER')
        else:
            if getEnabled(chat_id):
                reply('I got your messsage')
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))

app = webapp2.WSGIApplication([
    ('/', MainHandler)
    ('/set_webhook', SetWebHookHandler),
    ('/webhook', WebHookHandler),
], debug=True)

