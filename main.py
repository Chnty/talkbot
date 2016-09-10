
from google.appengine.api import urlfetch
import webapp2
import json
import logging
from urllib2 import urlopen
from urllib import urlencode
import random
from datetime import datetime, tzinfo
from google.appengine.ext import ndb
#import cfscrape
import ConfigParser
import configg
from math import *

TOKEN = open('bot.token').read()
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'
BOT_NAME = 'chntybot'
Config = ConfigParser.ConfigParser()
Config.read("userids.ini")
master_id = int(Config.get('MasterId', 'master'))
friends = Config.get('UserIds', 'friends').split()
max_dungeon_size = 50


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


class Ranking(ndb.Model):
    user_name = ndb.StringProperty()
    user_id = ndb.IntegerProperty()
    score = ndb.IntegerProperty()


class Reaction(ndb.Model):
    input = ndb.StringProperty()
    output = ndb.StringProperty()
    good = ndb.IntegerProperty()
    bad = ndb.IntegerProperty()
    chat_id = ndb.StringProperty()


class Reaction2(ndb.Model):
    input = ndb.StringProperty()
    output = ndb.StringProperty()
    count = ndb.IntegerProperty()


class Reaction3(ndb.Model):
    input = ndb.StringProperty()
    output = ndb.StringProperty()
    type = ndb.StringProperty()
    chat_id = ndb.StringProperty()
    count = ndb.IntegerProperty()


class Request(ndb.Model):
    user_id = ndb.StringProperty()
    request = ndb.StringProperty()


class Monster(ndb.Model):
    name = ndb.StringProperty()
    file_id = ndb.StringProperty()
# Start of Methods


def choose_pokemon(pokemons, lat_1, lon_1):
    pokemon = pokemons[random.randint(0, len(pokemons) - 1)]
    poke_lat = pokemon['latitude']
    poke_lon = pokemon['longitude']
    distance = harvesine(lat_1, lon_1, poke_lat, poke_lon)[0]
    close_pokemon = [pokemon]
    for i in range(0, len(pokemons) - 1):
        cur_pokemon = pokemons[i]
        poke_lat = cur_pokemon['latitude']
        poke_lon = cur_pokemon['longitude']
        cur_distance = harvesine(lat_1, lon_1, poke_lat, poke_lon)[0]
        if cur_distance < distance:
            pokemon = cur_pokemon
            close_pokemon.append(pokemon)
            distance = cur_distance
    return close_pokemon[-3:]


def pokename(pokenr):
    url = "https://pokeapi.co/api/v2/pokemon/" + str(pokenr) + "/"
    response = urlopen(url)
    body = response.read()
    data = json.loads(body)
    forms = data['forms'][0]
    pokemon_name = forms['name']
    return str(pokemon_name)


def norris():
    url = "https://api.icndb.com/jokes/random"
    response = urlopen(url)
    body = response.read()
    data = json.loads(body)
    if data['type'] == 'success':
        value = data['value']
        joke = value['joke']
        return str(joke)
    else:
        return ""


def deg_to_sky(degree):
    part = int((degree + 22.5)/45.0)
    if part == 0:
        return 'S'
    elif part == 1:
        return 'SW'
    elif part == 2:
        return 'W'
    elif part == 3:
        return 'NW'
    elif part == 4:
        return 'N'
    elif part == 5:
        return 'NE'
    elif part == 6:
        return 'E'
    elif part == 7:
        return 'SE'
    elif part == 8:
        return 'S'
    else:
        return 'NORTH'


def harvesine(lat_1, lon_1, lat_2, lon_2):
    lon_1, lat_1, lon_2, lat_2 = map(radians, [lon_1, lat_1, lon_2, lat_2])
    dlon = lon_2 - lon_1
    dlat = lat_2 - lat_1
    a = sin(dlat / 2) ** 2 + cos(lat_1) * cos(lat_2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    base = 6371 * c

    bearing = atan2(sin(lon_2 - lon_1) * cos(lat_2), cos(lat_1) *
                    sin(lat_2) - sin(lat_1) * cos(lat_2) * cos(lon_2 - lon_1))
    bearing = degrees(bearing)
    bearing = (bearing + 360) % 360

    result = [base, bearing]
    return result


def add_idlegame(chatid):
    for i in configg.idlegame:
        if i[0] == chatid:
            return False
    configg.idlegame.append([chatid, True, datetime.now(), datetime.now(), ''])
    return True


def get_idlegame(chatid):
    for i in configg.idlegame:
        if i[0] == chatid:
            return i
    return None


def set_idlegame(chatid, gameison, newtime, oldtime, newwinner):
    for i in configg.idlegame:
        if i[0] == chatid:
            i[1] = gameison
            i[2] = newtime
            i[3] = oldtime
            i[4] = newwinner


def give_rank(level):
    if level < 5:
        return [1, 'Novice']
    elif level < 10:
        return [2, 'Agent']
    elif level < 50:
        return [3, 'Warrior']
    elif level < 100:
        return [4, 'Gladiator']
    elif level < 200:
        return [5, 'Paladin']
    elif level < 300:
        return [6, 'Knight']
    elif level < 500:
        return [7, 'Lord']
    elif level < 1000:
        return [8, 'DragonSlayer']
    else:
        return [99, 'SupderMegaDuperGrandmaster']


def has_monster(room):
    x = room[0]
    y = room[1]
    field_size = 5
    cur_minute = int(datetime.now().minute)
    check_min = cur_minute % field_size

    def has_monster_help(x_help, offset):
        if (x_help + check_min) % field_size == offset:
            return True
    if y % field_size == 0:
        return has_monster_help(x, 1)
    elif y % field_size == 1:
        return has_monster_help(x, 3)
    elif y % field_size == 2:
        return has_monster_help(x, 0)
    elif y % field_size == 3:
        return has_monster_help(x, 2)
    elif y % field_size == 4:
        return has_monster_help(x, 4)


def fight(playerlevel, monsterlevel):
    if playerlevel < monsterlevel:
        return 1
    else:
        return monsterlevel


def player_damage(userid, chatid, damage):
    for i in configg.dungeon_user:
        if i[0] == userid and i[1] == chatid:
            i[5] -= damage
            return i[5]
    return 0


def upload_monster(file_id):
    Monster(name=configg.monster_name, file_id=file_id).put()


def get_monster():
    monsters = Monster.query().fetch()
    count = len(monsters)
    monster = monsters[random.randint(0, count)]
    if monster is not None:
        return [monster.name, monster.file_id]


def add_user_to_dungeon(userid, chatid):
    rand_x = random.randint(1, max_dungeon_size)
    rand_y = random.randint(1, max_dungeon_size)
    playerlvl = get_level(userid)
    start_hp = playerlvl + 20
    configg.dungeon_user.append([userid, chatid, True, rand_x, rand_y, start_hp])


def revive(userid, chatid):
    for i in configg.dungeon_user:
        if i[0] == userid and i[1] == chatid:
            i[5] = get_level(userid)
            i[3] = True


def user_is_in_dungeon(userid, chatid):
    for i in configg.dungeon_user:
        if i[0] == userid and i[1] == chatid and i[2] == True:
            return True
    return False


def dungeon_move(userid, chatid, delta_x, delta_y):
    for i in configg.dungeon_user:
        if i[0] == userid and i[1] == chatid:
            cur_x = i[3]
            cur_y = i[4]
            new_x = cur_x + delta_x
            new_y = cur_y + delta_y
            if new_x < 1 or new_x > max_dungeon_size:
                new_x = random.randint(1, max_dungeon_size)
            if new_y < 1 or new_y > max_dungeon_size:
                new_y = random.randint(1, max_dungeon_size)
            i[3] = new_x
            i[4] = new_y


def leave_dungeon(userid, chatid):
    for i in configg.dungeon_user:
        if i[0] == userid and i[1] == chatid:
            i[2] = False


def get_level(userid):
    check = Ranking.query(Ranking.user_id == userid).fetch()
    if check:
        return int(check[0].score)
    else:
        return 0


def status_dungeon(userid, chatid):
    level = get_level(userid)
    symbol_for_monster = 'X'
    symbol_for_free = 'O'
    if level != 0:
        msg = 'Your level is ' + str(level)
        msg += '\nYour Rank is ' + give_rank(level)[1]
    else:
        msg = 'You do not have any level yet'
    reply(chatid, msg)
    for i in configg.dungeon_user:
        if i[0] == userid and i[1] == chatid:
            if i[2]:
                x = i[3]
                y = i[4]
                princess_x = configg.princess[0]
                princess_y = configg.princess[1]
                distance = math.fabs(x - princess_x) + math.fabs(y - princess_y)
                distance += random.randint(-1, 1)
                msg = 'The princess is about ' + str(distance) + ' rooms away. \n'

                def pm(monster_boolean, xx=-1, yy=-1):
                    if monster_boolean:
                        if xx == x and yy == y:
                            return 'H'
                        else:
                            return symbol_for_monster
                    else:
                        return symbol_for_free
                monster_map = \
                    pm(has_monster([x - 2, y - 2])) + \
                    pm(has_monster([x - 1, y - 2])) + \
                    pm(has_monster([x, y - 2])) + \
                    pm(has_monster([x + 1, y - 2])) + \
                    pm(has_monster([x + 2, y - 2])) + '\n' + \
                    pm(has_monster([x - 2, y - 1])) + \
                    pm(has_monster([x - 1, y - 1])) + \
                    pm(has_monster([x, y - 1])) + \
                    pm(has_monster([x + 1, y - 1])) + \
                    pm(has_monster([x + 2, y - 1])) + '\n' + \
                    pm(has_monster([x - 2, y])) + \
                    pm(has_monster([x - 1, y])) + \
                    pm(has_monster([x, y]), x, y) + \
                    pm(has_monster([x + 1, y])) + \
                    pm(has_monster([x + 2, y])) + '\n' + \
                    pm(has_monster([x - 2, y + 1])) + \
                    pm(has_monster([x - 1, y + 1])) + \
                    pm(has_monster([x, y + 1])) + \
                    pm(has_monster([x + 1, y + 1])) + \
                    pm(has_monster([x + 2, y + 1])) + '\n' + \
                    pm(has_monster([x - 2, y + 2])) + \
                    pm(has_monster([x - 1, y + 2])) + \
                    pm(has_monster([x, y + 2])) + \
                    pm(has_monster([x + 1, y + 2])) + \
                    pm(has_monster([x + 2, y + 2]))
                msg += monster_map
            else:
                msg = 'You left the dungeon'
            msg += '\nYou have ' + str(i[5]) + 'HP'
            reply(chatid, msg)
            return
    msg = 'You did not enter the dungeon. Use /start_dungeon to enter'

    reply(chatid, msg)


def level_up(userid, username, level):
    check = Ranking.query(Ranking.user_id == userid).fetch()
    if check:
        rank = check[0]
        rank.score += level
        rank.put()
    else:
        Ranking(user_name=username, user_id=userid, score=level).put()


def dungeon_get_room(userid, chatid):
    for i in configg.dungeon_user:
        if i[0] == userid and i[1] == chatid:
            return [i[3], i[4]]
    return None


def add_request(user_id, request):
    return Request(user_id=user_id, request=request).put()


def add_reaction(inputt, chat_id=""):
    configg.wait_for = inputt
    configg.wait_for_answer = True
    return Reaction(input=inputt, output="derp", good=0, bad=0, chat_id=chat_id).put()


def add_reaction2(inputt):
    configg.wait_for2 = inputt
    configg.wait_for_answer2 = True
    return Reaction2(input=inputt, output="derp", count=1).put()


def add_reaction3(inputt, outputt, chat_id, typpe="text"):
    chat_id = str(chat_id)
    check = Reaction3.query(Reaction3.chat_id == chat_id, Reaction3.input == inputt).fetch()
    if check:
        check_count = random.choice(check).count
        if check_count > configg.reaction_threshold3:
            Reaction3(input=inputt, output=outputt, type=typpe, chat_id=chat_id, count=0).put()
    else:
        Reaction3(input=inputt, output=outputt, type=typpe, chat_id=chat_id, count=0).put()


# update_reaction kann fuer beide verwendet werden
def update_reaction(reaction_key, output):
    reac = reaction_key.get()
    reac.output = output
    reac.put()


def get_reaction(inputt):
    check = Reaction.query(Reaction.input == inputt).fetch()
    if check:
        return check[0].output
    else:
        return 'derp'


def get_reaction2(inputt):
    check = Reaction2.query(Reaction2.input == inputt).fetch()
    if check:
        choice = random.choice(check)
        choice.count += 1
        if choice.count > 50:
            choice.count = 1
            configg.new_reaction = False
            configg.cur_reaction_key2 = add_reaction2(inputt)
        choice.put()
        return choice.output
    else:
        return 'derp'


def get_reaction3(inputt, chat_id=0):
    check = Reaction3.query(Reaction3.input == inputt, Reaction3.chat_id == str(chat_id)).fetch()
    if check:
        choice = random.choice(check)
        choice.count += 1
        choice.put()
        return [choice.output, choice.type]
    else:
        check = Reaction3.query(Reaction3.input == inputt).fetch()
        if check:
            choice = random.choice(check)
            choice.count += 1
            choice.put()
            return [choice.output, choice.type]
        else:
            return ['derp', 'text']


def remove_reaction3(inputt, chat_id):
    check = Reaction3.query(Reaction3.input == inputt, Reaction3.chat_id == str(chat_id)).fetch()
    if check:
        for i in check:
            i.key.delete()


def random_drinker():
    names = ['Peter', 'Kerry', 'Max', 'Felix']
    return names[random.randint(0, 3)]


def random_drink():
    drinks = ['Beer', 'Cocktail', 'Jelloshot']
    return drinks[random.randint(0, 2)]


def add_drinker(name):
    configg.drinker += ' ' + name


def get_drinker():
    drinker_list = configg.drinker.split()
    return drinker_list[random.randint(0, len(drinker_list)-1)]


def add_drink(drinks):
    configg.drinks += ' ' + drinks


def get_drink():
    drink_list = configg.drinks.split()
    return drink_list[random.randint(0, len(drink_list)-1)]


def add_task(task):
    configg.task += ' ' + task


def get_task():
    task_list = configg.task.split()
    return task_list[random.randint(0, len(task_list)-1)]


def dice():
    return random.randint(1, 6)


def drink():
    return str(dice()) + ' units of  ' + get_drink()


def drinkgame(username=''):
    randomize = random.randint(0, 3)
    if randomize == 0:
        result = get_drinker() + ' plays ' + get_task() + ' with ' + get_drinker() + ' for ' + drink()
    elif randomize == 1:
        result = get_drinker() + ' plays ' + get_task() + ' with ' + get_drinker() + \
                 ' wether ' + get_drinker() + ' has to drink ' + drink()
    elif randomize == 2:
        result = username + ' has to drink ' + drink()
    else:
        result = get_drinker() + ' can choose who drinks ' + drink()
    return result
    # return random_name() + ' has to drink ' + str(dice()) + '' + random_drink()


def show_score():
    allrank = Ranking.query(Ranking.score >= 60).order(-Ranking.score).fetch()
    first = allrank[0]
    second = allrank[1]
    third = allrank[2]
    if third is None:
        return 'Not enough ranked players'
    return ('1. ' + first.user_name + ' ' + str(first.score) + 'Points \n '
            '2. ' + second.user_name + ' ' + str(second.score) + 'Points \n'
            '3. ' + third.user_name + ' ' + str(third.score) + 'Points \n')


def update_score(username, userid, score):
    check = Ranking.query(Ranking.user_id == userid).fetch()
    if check:
        rank = check[0]
        old_score = rank.score
        if score > old_score:
            rank.score = score
            rank.put()
    else:
        Ranking(user_name=username, user_id=userid, score=score).put()


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
    if len(phrase) > 50:
        return
    Phrase(phrase=phrase, count=1, date=datetime.now(), firstPoster=poster_id, posterName=name).put()


def choose_phrase():
    if configg.limit > 10:
        return 'Limit reached'
    configg.limit += 1
    all_phrase = Phrase.query().fetch()
    answer = ""
    tell_length_weight = 1

    for phrase in all_phrase:
        phrase_length_weight = int(len(str(phrase.phrase))/10)+1
        words_in_phrase = len(phrase.phrase.split())
        if random.randint(0, phrase.count*tell_length_weight*phrase_length_weight * words_in_phrase) == 1:
            answer += " " + phrase.phrase
            if 100 - tell_length_weight < 1 or random.randint(0, 100 - tell_length_weight) == 1:
                return answer
            tell_length_weight += 1
            phrase.count += 1
            phrase.put()
    if answer == "":
        answer = 'derp'
    return answer


def choose_challenge():
    if random.randint(0, 2) == 1:
        return 'iuoa e kcet lheiny wirlwfrb nriswr opc  ihr hywudcos hsoe orase sbiasoe. y letiap,eo ot .unr dhr'
    else:
        return 'What are advantages and disadvantages of  KAME IPsec-Utilities  and OpenVPN'


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


def represent_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def reply(chat_id, msg=None):
    if msg:
        # msg = xkcd_substitutions(msg)
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


def reply_photo(chat_id, file_id=None):
    if file_id:
        resp = urlopen(BASE_URL + 'sendPhoto', urlencode({
            'chat_id': str(chat_id),
            'photo': file_id.encode('utf-8'),
            'disable_notification': 'true',
        })).read()
    else:
        logging.error('no photo specified')
        resp = None
    logging.info('send response:')
    logging.info(resp)


def reply_music(chat_id, file_id):
    # file_id = 'BQADAgADIQAD7eBoBfAC1TA9j9gQAg'
    resp = urlopen(BASE_URL + 'sendAudio', urlencode({
        'chat_id': str(chat_id),
        'audio': file_id.encode('utf-8'),
        'disable_notification': 'true',
    })).read()
    logging.info('send response:')
    logging.info(resp)


def reply_move(chat_id, msg=None):
    if msg:
        reply_markup = {'keyboard': [['north'], ['west', 'east'], ['south']],
                        'resize_keyboard': True, 'one_time_keyboard': True}
        reply_markup = json.dumps(reply_markup)
        resp = urlopen(BASE_URL + 'sendMessage', urlencode({
            'chat_id': str(chat_id),
            'text': msg.encode('utf-8'),
            'reply_markup': reply_markup,
            'parse_mode': 'HTML',
            'disable_web_page_preview': 'true',
        })).read()
    else:
        logging.error('no msg specified')
        resp = None
    logging.info('send response:')
    logging.info(resp)


def reply_lang(chat_id, msg=None):
    if msg:
        reply_markup = {'keyboard': [
            [configg.flag[configg.english]],
            [configg.flag[configg.german]],
            [configg.flag[configg.chinese]],
            [configg.flag[configg.portuguese]]
        ],
                        'resize_keyboard': True, 'one_time_keyboard': True}
        reply_markup = json.dumps(reply_markup)
        resp = urlopen(BASE_URL + 'sendMessage', urlencode({
            'chat_id': str(chat_id),
            'text': msg.encode('utf-8'),
            'reply_markup': reply_markup,
            'parse_mode': 'HTML',
            'disable_web_page_preview': 'true',
        })).read()
    else:
        logging.error('no msg specified')
        resp = None
    logging.info('send response:')
    logging.info(resp)


def reply_numbers(chat_id, msg=None):
    if msg:
        reply_markup = {'keyboard': [
            [configg.chain_numbers[1]],
            [configg.chain_numbers[2]],
            [configg.chain_numbers[3]],
            [configg.chain_numbers[4]]
        ],
                        'resize_keyboard': True, 'one_time_keyboard': True}
        reply_markup = json.dumps(reply_markup)
        resp = urlopen(BASE_URL + 'sendMessage', urlencode({
            'chat_id': str(chat_id),
            'text': msg.encode('utf-8'),
            'reply_markup': reply_markup,
            'parse_mode': 'HTML',
            'disable_web_page_preview': 'true',
        })).read()
    else:
        logging.error('no msg specified')
        resp = None
    logging.info('send response:')
    logging.info(resp)


def reply_remove_keyboard(chat_id, msg=None):
    if msg:
        reply_markup = {'hide_keyboard': True}
        reply_markup = json.dumps(reply_markup)
        resp = urlopen(BASE_URL + 'sendMessage', urlencode({
            'chat_id': str(chat_id),
            'text': msg.encode('utf-8'),
            'reply_markup': reply_markup,
            'parse_mode': 'HTML',
            'disable_web_page_preview': 'true',
        })).read()
    else:
        logging.error('no msg specified')
        resp = None
    logging.info('send response:')
    logging.info(resp)


def reply_inline_text(inline_query_id, inputt, output):
    if output == 'derp':
        output = 'No Reaction yet'
    msg = inputt + ' -> ' + output
    message_content = {'message_text': msg, 'parse_mode': 'HTML'}
    results = [{'type': 'article', 'id': inline_query_id, 'title': output, 'input_message_content': message_content}]
    results = json.dumps(results)
    resp = urlopen(BASE_URL + 'answerInlineQuery', urlencode({
        'inline_query_id': str(inline_query_id),
        'results': results,
    })).read()
    logging.info('send response:')
    logging.info(resp)


def reply_inline_image(inline_query_id, inputt, output):
    results = [{'type': 'photo', 'id': inline_query_id, 'photo_file_id': output, 'title': inputt}]
    results = json.dumps(results)
    resp = urlopen(BASE_URL + 'answerInlineQuery', urlencode({
        'inline_query_id': str(inline_query_id),
        'results': results,
    })).read()
    logging.info('send response:')
    logging.info(resp)


def chnty_forward(from_id, msg_id):
    resp = urlopen(BASE_URL + 'forwardMessage', urlencode({
        'chat_id': str(master_id),
        'from_chat_id': str(from_id),
        'message_id': msg_id,
    })).read()
    logging.info('send response:')
    logging.info(resp)


def master(texxt, chat_id):
    if 'memo' in texxt:
        texxt = texxt[0:(texxt.find('memo') - 1)]
        add_memory(texxt, 1)
    elif 'mode' in texxt:
        if 'spy' in texxt:
            reply(chat_id, get_memory(2))
        reply(chat_id, get_memory(1))
    elif 'bot' in texxt:
        reply(chat_id, "Here, Master!")
    elif 'iswho' in texxt:
        texxt = texxt[0:texxt.find('iswho') - 1]
        reply(chat_id, str(what_did_he_say(texxt)))
    elif 'player' in texxt:
        texxt = texxt[0:texxt.find('player') - 1]
        add_drinker(texxt)
    elif 'drink' in texxt:
        texxt = texxt[0:texxt.find('drink') - 1]
        add_drink(texxt)
    elif 'add' in texxt:
        texxt = texxt[0:texxt.find('add') - 1]
        add_task(texxt)
    elif 'add' in texxt:
        texxt = texxt[0:texxt.find('add') - 1]
        add_task(texxt)
    elif 'abort' in texxt:
        configg.hijacked = False
    elif 'hijack' in texxt:
        configg.hijacked = True
        configg.chat_id = chat_id
    elif 'fuckon' in texxt:
        texxt = texxt[0:texxt.find('add') - 1]
        configg.fucker = texxt
        configg.fuckon = True
    elif 'fuckoff' in texxt:
        configg.fuckon = False
        configg.fucker = 'Alex'
    elif 'dice' in texxt:
        reply(chat_id, str(dice()))
    elif configg.hijacked:
        reply(chat_id, texxt)
    elif texxt.startswith('update '):
        texxt = texxt[len('update '):]
        if texxt == 'derp':
            configg.daily_update = 'derp'
        else:
            if configg.daily_update == 'derp':
                configg.daily_update = texxt
            else:
                configg.daily_update += texxt + '\n'
    elif texxt.startswith('tell '):
        texxt = texxt[len('tell '):]
        to_chat_id = texxt[:texxt.find(":")]
        texxt = texxt[texxt.find(":") + 2:]
        reply(to_chat_id, texxt)
    else:
        return False
    return True


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

        # Check what kind of message is sent
        if 'edited_message' in body:
            message = body['edited_message']
        elif 'message' in body:
            message = body['message']
        elif 'inline_query' in body:
            inline_query = body['inline_query']
            query = inline_query.get('query')
            output = get_reaction3(query)
            if output[1] == 'text':
                idd = inline_query.get('id')
                reply_inline_text(idd, str(query), output[0])
            elif output[1] == 'photo':
                idd = inline_query.get('id')
                reply_inline_image(idd, str(query), output[0])
            return
        else:
            return

        # Parse message in it's useful components
        text = message.get('text')
        chat = message['chat']
        chat_id = chat['id']
        fr = message.get('from')

        user_id = fr['id']

        username = fr['first_name']

        msg_id = int(message['message_id'])

        for i in username:
            if ord(i) > 128:
                username = 'Derp'

        if 'photo' in message:
            photo = message['photo']
            photo = photo[0]
            file_id = photo['file_id']
            if chat_id in configg.wait_for3:
                old_text = configg.wait_for3[chat_id]
                if old_text != 'derp':
                    add_reaction3(old_text, file_id, chat_id, 'photo')
            configg.wait_for3[chat_id] = 'derp'

        if 'audio' in message:
            audio = message['audio']
            file_id = audio['file_id']
            if chat_id in configg.wait_for3:
                old_text = configg.wait_for3[chat_id]
                if old_text != 'derp':
                    add_reaction3(old_text, file_id, chat_id, 'audio')
            configg.wait_for3[chat_id] = 'derp'

        if 'location' in message:
            location = message['location']
            lat_2 = location['latitude']
            lon_2 = location['longitude']
            old_name = configg.trainerpos[0]
            old_time = configg.trainerpos[1]
            old_lat = configg.trainerpos[2]
            old_lon = configg.trainerpos[3]
            new_time = datetime.now()
            new_name = username
            if old_name != new_name and old_time is not None:
                delta_minutes = int((new_time - old_time).total_seconds()/60)
                harve = harvesine(old_lat, old_lon, lat_2, lon_2)
                distance = round(harve[0] * 1000, 1)
                direction = round(harve[1], 2)
                skydir = deg_to_sky(direction)
                msg = 'Trainer ' + old_name + ' was ' + str(distance) + 'm ' + \
                      skydir + ' ' + str(delta_minutes) + 'minute(s) ago'
                reply(chat_id, msg)
            configg.trainerpos = [new_name, new_time, lat_2, lon_2]
            pokemons = None
            for trainer in configg.pokemon_pos:
                latestpoke = trainer[2]
                if user_id in trainer and datetime.fromtimestamp(latestpoke) > datetime.now():
                    pokemons = trainer[1]
            if pokemons is None:
                reply(chat_id, 'Start Poke-Log-Pose')
                pokevis_url = 'https://pokevision.com/map/data/' + str(lat_2) + '/' + str(lon_2)
                response = urlopen(pokevis_url)
                html = response.read()
                pokevis = json.loads(html)
                if pokevis['status'] == 'success':
                    pokemons = pokevis['pokemon']
                    if len(pokemons) == 0:
                        reply(chat_id,  'No Pokemon nearby')
                        return
                    max_time = max(pokemons, key=lambda item: item['expiration_time'])['expiration_time']
                    configg.pokemon_pos.append([user_id, pokemons, max_time])
                else:
                    reply(chat_id,  'Some fail with pokevis')
                    return
            for pokemon in choose_pokemon(pokemons, lat_2, lon_2):
                poke_id = pokemon['pokemonId']
                expiration_time = pokemon['expiration_time']
                lat_1 = pokemon['latitude']
                lon_1 = pokemon['longitude']
                harve = harvesine(lat_1, lon_1, lat_2, lon_2)
                distance = round(harve[0]*1000, 1)
                direction = round(harve[1], 2)
                skydir = deg_to_sky(direction)
                left_time = (datetime.fromtimestamp(expiration_time) - datetime.now()).seconds/60
                reply(chat_id, 'From ' + username + ': ' + str(distance) + 'm ' + skydir +
                      ' to Pokemon #' + str(poke_id) + ' ' + pokename(poke_id) + ' for ' + str(left_time) + 'min')

        if text is None or len(text) > 700:
            return

        if text in configg.inv_flag:
            configg.language[user_id] = configg.inv_flag[text]
            reply_remove_keyboard(chat_id, "Language changed to " + configg.language[user_id])
            return
        # text = text.encode('ascii', 'ignore')
        username = fr['first_name']

        if text in configg.chain_numbers:
            configg.active_chain[user_id] = text
            reply_remove_keyboard(chat_id, username + ' has ' + text)
            return

        if not text:
            logging.info('no text')
            return

        if username in configg.fucker and configg.fuckon:
            reply(chat_id, 'Fuck you!')

        idle = get_idlegame(chat_id)
        if idle is not None:
            if text == '/stop_idlegame':
                set_idlegame(chat_id, False, idle[2], idle[3], idle[4])
                return
            game_is_on = idle[1]
            newtime = datetime.now()
            oldtime = idle[3]
            curwinner = idle[4]
            if game_is_on:
                time_delta_minutes = int((newtime - oldtime).total_seconds()/60)
                if time_delta_minutes > 5:
                    curwinner = username
                    update_score(username, user_id, time_delta_minutes)
                    reply(chat_id, str(username) + ' broke silence after ' + str(time_delta_minutes) + 'minutes')
                oldtime = newtime
                set_idlegame(chat_id, True, newtime, oldtime, curwinner)

        if text.startswith('/'):
            if text.find('@') > 0:
                if text.find(BOT_NAME) > 0:
                    text = text[0:text.find('@')]
                else:
                    return
            if text == '/start':
                start = configg.default_start
                if user_id in configg.language:
                    start = configg.start_text[configg.language[user_id]]
                reply(chat_id, start)
            elif text == "/drinkgame":
                reply(chat_id, str(drinkgame(username)))
            elif text == '/help':
                helpp = configg.default_help
                if user_id in configg.language:
                    helpp = configg.help_text[configg.language[user_id]]
                reply(chat_id, helpp)
            elif text == '/tell':
                reply(chat_id, choose_phrase())
            elif text == '/cow_on':
                configg.iscow = True
            elif text == '/cow_off':
                configg.iscow = False
            elif text == '/suggest':
                reply(chat_id, 'https://github.com/Chnty/talkbot/issues')
                reply(chat_id, 'https://storebot.me/bot/chntybot')
                reply(chat_id, 'dreaddcp@hotmail.com')
            elif text == '/challenge':
                reply(chat_id, choose_challenge())
            elif text == '/subscribe':
                if add_subscriber(chat_id) == 1:
                    reply(chat_id, 'Subscribed to chntybot!')
                else:
                    reply(chat_id, 'Already subscribed!')
            elif text == '/unsubscribe':
                if remove_subscriber(chat_id) == 1:
                    reply(chat_id, 'Unsubscribed from chntybot!')
                else:
                    reply(chat_id, 'Not subscribed!')
            elif text == '/start_idlegame':
                if add_idlegame(chat_id):
                    reply(chat_id, 'Start Idlegame')
                    return
                else:
                    reply(chat_id, 'Idlegame already started')
                    return
            elif text=='/old_reaction':
                configg.old_Reaction = True
                reply(chat_id, 'Now using Reaction0.1v')
            elif text=='/new_reaction':
                configg.old_Reaction = False
                reply(chat_id, 'Now using Reaction0.2v')
            elif text == '/score':
                reply(chat_id, str(show_score()))
            elif text == 'chat_id, /drinkgame':
                reply(chat_id, str(drinkgame()))
            elif text == '/status':
                if configg.wait_for_answer:
                    reply(chat_id, 'waiting for reaction to ' + str(configg.wait_for))
                else:
                    reply(chat_id, 'listening')
            elif text == '/showall' and str(user_id) in friends:
                configg.show_all_counter += 1
                allreaction = Reaction.query().fetch()
                for count in range(10):
                    response = str(allreaction[count].input) + ' -> ' + str(allreaction[count].output)
                    reply(chat_id, response)
            elif text == '/start_dungeon':
                if user_is_in_dungeon(user_id, chat_id):
                    reply(chat_id, 'You already entered this dungeon')
                else:
                    add_user_to_dungeon(user_id, chat_id)
                    reply(chat_id, 'You enter the dungeon. How many princesses can you rape?..erm I mean save!')
            elif text == '/leave_dungeon':
                leave_dungeon(user_id, chat_id)
                reply(chat_id, 'You left the dungeon and can never return')
            elif text == '/status_dungeon':
                status_dungeon(user_id, chat_id)
            elif text == '/chuck':
                reply(chat_id, norris())
            elif text == '/now':
                reply(chat_id, str(datetime.now()))
            elif '/chntyrequest' in text:
                #text =  text.decode('ascii', 'ignore')
                # text[text.find('/chntyrequest') + len('/chntyrequest'):]
                request = username + ' wants: ' + text
                add_request(str(user_id), request)
                chnty_forward(chat_id, msg_id=msg_id)
                # reply(master_id, str(request))
            elif text == '/language':
                reply_lang(chat_id, 'Choose your language')
            elif text == '/credits':
                reply(chat_id, configg.credit)
            elif '/force' in text:
                text = text[text.find('/force') + len('/force '):]
                if text == '':
                    reply(chat_id, 'This command is for force learning a reaction. Please provide the command like this:\n\n/force [input]')
                else:
                    configg.wait_for3[chat_id] = text
                    remove_reaction3(text, chat_id)
                    reply(chat_id, 'How should I react to "' + text + '"?')
            elif text == '/chain':
                reply_numbers(chat_id, 'How long should the chain of reactions be?')
            else:
                return
        elif 'create_monster' in text:
            text = text[15:]
            configg.monster_name = text
            configg.create_monster.append(chat_id)
            reply(chat_id, 'Please Upload a picture for ' + text)
        elif 'who are you' in text:
            reply(chat_id, 'I am Chief-Bot of the Bots of Darkness, Lord of the Thirteen Chatrooms, '
                  'Master of Spam, Emporer of the Groups, Lord of the Unidle, '
                  'Lord of the Dance(Self-nominated), and the mayor of a little village down the coast')

        elif user_is_in_dungeon(user_id, chat_id):
            if 'N' == text or 'n' == text:
                dungeon_move(user_id, chat_id, 0, -1)
            elif 'E' == text or 'e' == text:
                dungeon_move(user_id, chat_id, 1, 0)
            elif 'S' == text or 's' == text:
                dungeon_move(user_id, chat_id, 0, 1)
            elif 'W' == text or 'w' == text:
                dungeon_move(user_id, chat_id, -1, 0)
            else:
                return
            cur_room = dungeon_get_room(user_id, chat_id)
            reply(chat_id, 'You are now in Room ' + str(cur_room[0]) + ' ' + str(cur_room[1]))
            if cur_room == configg.princess:
                msg = 'You found the princess! '
                levelup = random.randint(1, 20)
                msg += 'You gain ' + str(levelup) + ' Level!'
                level_up(user_id, username, levelup)
                reply(chat_id, msg)
                princr = random.randint(0, 6)
                if princr == 0:
                    msg = 'When you enter, she wakes up and flees to another room'
                elif princr == 1:
                    msg = 'You cum so hard the princess is shot to another room'
                elif princr == 2:
                    msg = 'A shroom tells you that the princess is actually in another room'
                elif princr == 3:
                    msg = 'The princess was an illusion, you are still on drugs'
                elif princr == 4:
                    # interest through shock value
                    msg = 'You rape the princess, she fights back violently but ultimatly dies ' \
                         'when you hit her too hard. Now you go looking for your next victim'
                else:
                    msg = 'Dungeon Reset'
                reply(chat_id, msg)
                configg.princess = [random.randint(5, 44), random.randint(4, 46)]
            elif has_monster(cur_room):
                monster = get_monster()
                monster_name = monster[0]
                monster_file_id = monster[1]
                is_boss = False
                is_natural = False
                boss_chance = 10
                if 'boss' in monster_name or 'Boss' in monster_name or 'BOSS' in monster_name:
                    is_boss = True
                    is_natural = True
                if random.randint(0, boss_chance) == 1:
                    is_boss = True
                if is_boss and not is_natural:
                    monster_name = 'BOSS ' + monster_name
                msg = 'You encounter ' + str(monster_name)
                reply(chat_id, msg)
                reply_photo(chat_id, monster_file_id)
                player_level = get_level(user_id)
                monster_level = len(monster_name) + random.randint(1, 10)
                if is_boss:
                    monster_level *= 2
                damage = fight(player_level, monster_level)
                msg = str(monster_name) + ' is level ' + str(monster_level) + '\nit deals ' + str(damage) + ' Damage'
                reply(chat_id, msg)
                if player_damage(user_id, chat_id, damage) < 1:
                    msg = 'You die! You can revive yourself by creating a monster!'
                    leave_dungeon(user_id, chat_id)
                else:
                    msg = 'You easily kill the monster and gain 1 level'
                    level_up(user_id, username, 1)
                reply(chat_id, msg)
        elif str(user_id) in friends and False:
            if 'memo' in text and False:
                text = text[0:text.find('memo')]
                add_memory(text, 2)
            elif 'say' in text and False:
                reply(chat_id, get_memory(2))
            elif 'iswho' in text and False:
                text = text[0:text.find('iswho')-1]
                reply(chat_id, str(what_did_he_say(text)))
            elif 'abort' in text:
                configg.hijacked = False
            elif 'hijack' in text:
                configg.user_id = user_id
            elif configg.hijacked and user_id == configg.user_id:
                reply(chat_id, text)
            elif 'hijack' in text:
                configg.user_id = user_id
            elif 'player' in text:
                text = text[0:text.find('player') - 1]
                add_drinker(text)
            elif 'drink' in text:
                text = text[0:text.find('drink') - 1]
                add_drink(text)
            elif 'add' in text:
                text = text[0:text.find('add') - 1]
                add_task(text)
            elif configg.hijacked and user_id == configg.user_id:
                reply(chat_id, text)
        else:
            if user_id == master_id:
                if master(text, chat_id):
                    return
                # configg.old_Reaction
            if False:
                respo = str(get_reaction(text))
                if configg.wait_for_answer:
                    update_reaction(configg.cur_reaction_key, text)
                    configg.wait_for_answer = False
                    if respo != "derp":
                        reply(chat_id, respo)
                elif respo != "derp":
                    reply(chat_id, respo)
                else:
                    configg.cur_reaction_key = add_reaction(text, str(chat_id))
                 # configg.use_reaction2[chat_id]
            elif False: # Reaction2 is not default anymore
                configg.new_reaction = True
                respo = str(get_reaction2(text))
                if configg.wait_for_answer2 and configg.new_reaction:
                    update_reaction(configg.cur_reaction_key2, text)
                    configg.wait_for_answer2 = False
                    if respo != "derp":
                        reply(chat_id, respo)
                    else:
                        respo = str(get_reaction(text))
                        if respo != "derp":
                            reply(chat_id, respo)
                elif respo != "derp":
                    reply(chat_id, respo)
                else:
                    configg.cur_reaction_key2 = add_reaction2(text)
            else:
                # als erstes neue reaktion lernen
                if chat_id in configg.wait_for3:
                    old_text = configg.wait_for3[chat_id]
                    new_text = text
                    if old_text != 'derp':
                        add_reaction3(old_text, new_text, chat_id)
                configg.wait_for3[chat_id] = text
                react3 = text
                chainrepeats = 1
                if user_id in configg.active_chain:
                    chainrepeats = configg.chain_numbers.index(configg.active_chain[user_id])
                for i in range(chainrepeats):
                    if react3 in configg.chains:
                        break
                    configg.chains.append(react3)
                    react3 = get_reaction3(react3, chat_id)
                    respo3 = react3[0]
                    type3 = react3[1]
                    if type3 == 'text':
                        if respo3 == 'derp':
                            respo3 = str(get_reaction2(text))
                            if respo3 == 'derp':
                                respo3 = str(get_reaction(text))
                        if respo3 != 'derp':
                            reply(chat_id, respo3)
                    elif type3 == 'photo':
                        reply_photo(chat_id, respo3)
                    elif type3 == 'audio':
                        reply_music(chat_id, respo3)
                    react3 = respo3
                configg.chains= []


class ReminderHandler(webapp2.RequestHandler):
    def get(self):
        all_subscriber = Subscriber.query(projection=["chat_id"], distinct=True)

        msg = configg.daily_update
        if msg == 'derp':
            return
        else:
            configg.daily_update = 'derp'
        for sub in all_subscriber:
            urlopen(BASE_URL + 'sendMessage', urlencode({
                'chat_id': str(sub.chat_id),
                'text': msg.encode('utf-8'),
                'disable_web_page_preview': 'true',
            })).read()


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/set_webhook', SetWebHookHandler),
    ('/webhook', WebHookHandler),
    ('/reminder', ReminderHandler),
], debug=True)
