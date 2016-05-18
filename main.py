
from google.appengine.api import urlfetch
import webapp2
import json
import logging
from urllib2 import urlopen
from urllib import urlencode
import random
from datetime import datetime
from google.appengine.ext import ndb

TOKEN = open('bot.token').read()
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'
masterid = 90759405

#Start of ndb classes

class Phrase(ndb.Model):
    phrase = ndb.StringProperty()
    count = ndb.IntegerProperty()
    date = ndb.DateTimeProperty()
    firstPoster = ndb.IntegerProperty()

#End of ndb classes

#Start of Methods

def add_phrase(phrase):
    Phrase(phrase=phrase, count=1, date=datetime.now(), firstPoster=0).put()

def choose_phrase():
    allphrase = Phrase.query().fetch()
    answer = ""
    leng = 1
    for phrase in allphrase:
        if random.randint(0, phrase.count*leng) == 1:
            answer += " " + phrase.phrase
            leng += 1
            phrase.count+=1
            phrase.put()
    return answer

#End of Methods

#Start of Handlers

class SetWebHookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urlopen(BASE_URL + 'setWebhook', urlencode({'url': url})))))

#this is irrelevant for telegrambot but nice to check google appengine
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')



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
        textE=""
        if(text != None):
            textE = text.encode('ascii','ignore')
        fr = message.get('from')
        userid = fr['id']
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
            if text.find('@') > 0:
                text = text[0:text.find('@')]
            if text == '/start':
                reply('Bot enabled')
            elif text == '/help':
                reply('nope')
            elif text == '/tell':
                reply(choosePhrase())
            else:
                reply('What command?')

        elif 'who are you' in text:
            reply('I am Chief-Bot of the Bots of Darkness, Lord of the Thirteen Chatrooms, Master of Spam, Emporer of the Groups, Lord of the Unidle, Lord of the Dance(Self-nominated), and the Mayor of a little village down the coast')
        elif 'derp' in text:
            reply("derpiderp")
        elif userid == masterid:
            reply("I am here to serve, oh my great Master!")
        else:
            #reply("I will remember")
            addPhrase(textE)
            logging.info('not enabled for chat_id {}'.format(chat_id))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/set_webhook', SetWebHookHandler),
    ('/webhook', WebHookHandler),
], debug=True)

