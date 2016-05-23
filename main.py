
from google.appengine.api import urlfetch
import webapp2
import json
import logging
from urllib2 import urlopen
from urllib import urlencode
import random
from datetime import datetime
from google.appengine.ext import ndb
import ConfigParser
import configg

TOKEN = open('bot.token').read()
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'
BOT_NAME = 'chntybot'
Config = ConfigParser.ConfigParser()
Config.read("userids.ini")
master_id = Config.get('MasterId', 'master')
friends = Config.get('UserIds' , 'friends').split()


class Subscriber(ndb.Model):
    chat_id = ndb.IntegerProperty()


class Phrase(ndb.Model):
    phrase = ndb.StringProperty()
    count = ndb.IntegerProperty()
    date = ndb.DateTimeProperty()
    firstPoster = ndb.IntegerProperty()
    posterName = ndb.StringProperty()


class Memory(ndb.Model):
    order = ndb.IntegerProperty()
    sentence = ndb.StringProperty()
    mean_diff = ndb.IntegerProperty()
    cur_date = ndb.DateTimeProperty()

# Start of Methods


def add_subscriber(c_id):
    check = Subscriber.query(Subscriber.chat_id == c_id).fetch()
    if check:
        return 0
    else:
        subscriber = Subscriber(chat_id=c_id)
        subscriber.put()
        return 1


def remove_subscriber(c_id):
    check = Subscriber.query(Subscriber.chat_id == c_id).fetch()
    if check:
        check[0].key.delete()
        return 1
    return 0


def add_memory(sentence, index):
    all_memory = Memory.query().fetch()
    for mem in all_memory:
        if mem.order == index:
            mem.sentence = sentence
            mem.put()


def get_memory(index):
    all_memory = Memory.query().fetch()
    result = "no memory"
    for mem in all_memory:
        if mem.order == index:
            result = mem.sentence
    return result


def add_phrase(phrase, poster_id, name):
    Phrase(phrase=phrase, count=1, date=datetime.now(), firstPoster=poster_id, posterName=name).put()


def choose_phrase():
    all_phrase = Phrase.query().fetch()
    answer = ""
    length_weight = 2

    for phrase in all_phrase:
        if random.randint(0, phrase.count*length_weight) == 1:
            answer += " " + phrase.phrase
            length_weight += 2
            phrase.count += 1
            phrase.put()
    return answer


def what_did_he_say(name):
    all_phrase = Phrase.query().fetch()
    answer = ""
    answer2 = 0
    for phrase in all_phrase:
        if phrase.posterName is not None:
            if phrase.posterName in name:
                answer += " " + phrase.phrase
                answer2 += 1
    return str(answer2) + answer


def like_phrase(text):
    all_phrase = Phrase.query().fetch()
    count = 0
    if random.randint(0, 5) == 1:
        for phrase in all_phrase:
            if text in str(phrase.phrase):
                count += 1
                if phrase.count > 2:
                    phrase.count -= 1
                    phrase.put()
    return str(count)


def cow_speech(text):
    return ' '.join(map(lambda x: muhifyword(x), text.split()))


def muhifyword(text):
    if random.randint(0, 10) == 1:
        return text
    result = text + "hh"
    index = 0
    char = 'm'
    if result.istitle():
        char = 'M'
    result = result[:index] + char + result[index + 1:]
    index = 1
    char = 'u'
    result = result[:index] + char + result[index + 1:]
    for x in range(len(text)):
        if x > 1:
            index = x
            char = 'h'
            result = result[:index] + char + result[index + 1:]
    return result


def xkcd_substitutions(word):
    # xkcd 1288
    word = word.replace('witnesses', 'these dudes I know').replace('allegedly', 'kinda probably')
    word = word.replace('new study', 'tumblr post').replace('rebuild', 'avenge')
    word = word.replace('space', 'spaaace').replace('google glass', 'virtual boy')
    word = word.replace('smartphone', 'pokedex').replace('electric', 'atomic')
    word = word.replace('senator', 'elf-lord').replace('car', 'cat')
    word = word.replace('election', 'eating contest').replace('congressional leaders', 'river spirits')
    word = word.replace('homeland security', 'homestar runner')
    word = word.replace('could not be reached for comment', 'is guilty and everyone knows it')
    # xkcd 1625
    word = word.replace('debate', 'dance-off').replace('self driving', 'uncontrollably swerving')
    word = word.replace('poll', 'psychic reading').replace('candidate', 'airbender')
    word = word.replace('drone', 'dog').replace('vows to', "probably won't")
    word = word.replace('at large', 'very large').replace('successfully', 'suddenly')
    word = word.replace('expands', 'physically expands').replace('third-degree', "friggin' awful")
    word = word.replace('an unknown number', 'like hundreds').replace('front runner', 'blade runner')
    word = word.replace('global', 'spherical').replace('no indication', 'lots of signs')
    word = word.replace('years', '!!!!!derp!!!!!').replace('minutes', 'years').replace('!!!!!derp!!!!!', 'minutes')
    word = word.replace('urged restraint by', 'drunkenly egged on').replace('horsepower', 'tons of horsemeat')
    # funny stuff
    word = word.replace('peter', 'my Master').replace('Peter', 'great Master')
    word = word.replace('kerry', 'the chinese girl').replace('Kerry', 'the chinese girl')
    word = word.replace('sebastian', 'Phi').replace('Sebastian', 'the other guy who helped build me')
    word = word.replace('andrian', 'Thiemo').replace('Alex', 'derp')
    return word
# End of Methods
# Start of Handlers


class SetWebHookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urlopen(BASE_URL + 'setWebhook', urlencode({'url': url})))))


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

        # update_id = body['update_id']
        message = body['message']
        # message_id = message.get('message_id')
        # date = message.get('date')
        text = message.get('text')
        text = text.encode('ascii', 'ignore')
        fr = message.get('from')
        user_id = fr['id']
        username = fr['first_name']
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None):
            if msg:
                msg = xkcd_substitutions(msg)
                if configg.iscow:
                    msg = cow_speech(msg)
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
                if text.find(BOT_NAME) > 0:
                    text = text[0:text.find('@')]
                else:
                    return
            if text == '/start':
                reply('Bot enabled')
            elif text == '/help':
                reply('nope')
            elif text == '/tell':
                reply(choose_phrase())
            elif text == '/cow_on':
                configg.iscow = True
            elif text == '/cow_off':
                configg.iscow = False
            if text == '/subscribe':
                if add_subscriber(chat_id) == 1:
                    reply('Subscribed to chntybot!')
                else:
                    reply('Already subscribed!')
            elif text == '/unsubscribe':
                if remove_subscriber(chat_id) == 1:
                    reply('Unsubscribed from chntybot!')
                else:
                    reply('Not subscribed!')
            else:
                reply('What command?')

        elif 'who are you' in text:
            reply('I am Chief-Bot of the Bots of Darkness, Lord of the Thirteen Chatrooms, '
                  'Master of Spam, Emporer of the Groups, Lord of the Unidle, '
                  'Lord of the Dance(Self-nominated), and the mayor of a little village down the coast')

        elif user_id == master_id:
            if 'memo' in text:
                text = text[0:(text.find('memo')-1)]
                add_memory(text, 1)
            elif 'mode' in text:
                if 'spy' in text:
                    reply(get_memory(2))
                reply(get_memory(1))
            elif 'bot' in text:
                reply("Here, Master!")
            elif 'iswho' in text:
                text = text[0:text.find('iswho')-1]
                reply(str(what_did_he_say(text)))

        elif user_id in friends:
            if 'memo' in text:
                text = text[0:text.find('memo')]
                add_memory(text, 2)
            elif 'say' in text:
                reply(get_memory(2))

        else:
            add_phrase(text, user_id, username)
            logging.info('not enabled for chat_id {}'.format(chat_id))


class ReminderHandler(webapp2.RequestHandler):
    def get(self):
        all_subscriber = Subscriber.query(projection=["chat_id"], distinct=True)
        # send reminder message to every subscriber
        # care if to many subscribers -> limitations from telegram api
        msg = choose_phrase()
        for sub in all_subscriber:
            urlopen(BASE_URL + 'sendMessage', urlencode({
                'chat_id': sub,
                'text': msg.encode('utf-8'),
                'disable_web_page_preview': 'true',
            })).read()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/set_webhook', SetWebHookHandler),
    ('/webhook', WebHookHandler),
    ('/reminder', ReminderHandler),
], debug=True)
