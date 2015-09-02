import telegram
from telegram.chataction import ChatAction
import sqlite3 as db
import wikipedia
import time
import simplejson as json
import re

DB_NAME = 'data.db'
TABLE_NAMES = ['SEARCHES']

WAIT_TIME = 3 # seconds

HELP_MESSAGE = '''
Wikipedia Auto Post Bot - v1.1
    > help - Show this help
    > start - Starts the bot
    > search - Search the german wikipedia
'''

SEARCH_PATTERN = re.compile(ur'/search(@wikiautopostbot){0,}', re.IGNORECASE)

bot = None

def readAPIKey():
    with open('api.key', 'r') as f:
        return f.readline()

def init():
    # init database
    con = db.connect(DB_NAME)

    con.execute('''
        CREATE TABLE IF NOT EXISTS ''' + TABLE_NAMES[0] + ''' (
            SEARCH_TERM     TEXT	UNIQUE	NOT NULL,
            RANK            NUMBER
        )''')

    con.close()

def insert_or_update_word(word):
    try:
        con = db.connect(DB_NAME)

        word = word.strip()

        for term, rank in con.execute('SELECT search_term, rank FROM ' + TABLE_NAMES[0] + ' WHERE search_term LIKE ?', (word.lower(),)).fetchall():
            con.execute('UPDATE ' + TABLE_NAMES[0] + ' SET rank = ? WHERE search_term LIKE ?', (int(rank) + 1, term,))
            con.commit()
            return

        con.execute('INSERT INTO ' + TABLE_NAMES[0] + ' VALUES ( ? , ? )', (word, 1,))
        
        con.commit()
    except Exception as e:
        print str(e)
    finally:
        con.close()

def sendMessage(chat_id, message, reply_markup = None):
    try:
        bot.sendChatAction(chat_id, ChatAction.TYPING)
        if reply_markup is None:
            bot.sendMessage(chat_id, message, reply_markup = telegram.ReplyKeyboardHide())
        else:
            bot.sendMessage(chat_id, message, reply_markup = reply_markup)
    except Exception as e:
        print message
        print str(e)

def getWikiArticle(name):
    try:
        page = wikipedia.page(name).url
        insert_or_update_word(name)
        return page
    except wikipedia.exceptions.DisambiguationError as e:
        return str(e)
    except Exception as e:
        print e
    return None

def startMainLoop():
    messageOffset = 0

    print 'Starting MainLoop'

    while True:
        updates = bot.getUpdates(offset = messageOffset, limit = 1, timeout = WAIT_TIME)
    
        if len(updates) is not 0:
            for u in updates:
                
                messageOffset = u.update_id + 1
    
                chat_id = u.message.chat_id
                message = u.message.text.lower()

                if message.startswith(u'/start'):
                    sendMessage(chat_id, 'Senden Sie mir Ihren Suchbegriff: "/search <wort>"')
                elif message.startswith(u'/stop'):
                    pass # You cannot stop me wahahaha :D
                elif message.startswith(u'/help'):
                    sendMessage(chat_id, HELP_MESSAGE)
                elif message.startswith(u'/search'):
                    page = getWikiArticle(re.sub(SEARCH_PATTERN, '', message))
                    if page is not None:
                        sendMessage(chat_id, page)
                    else:
                        sendMessage(chat_id, 'Keinen Wikipedia Eintrag gefunden.')
                        
init()

bot = telegram.Bot(token = readAPIKey())
wikipedia.set_lang("de")

startMainLoop()