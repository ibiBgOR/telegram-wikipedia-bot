import telegram
from telegram.chataction import ChatAction
import sqlite3 as db
import wikipedia
import time
import simplejson as json
import re

DB_NAME = 'chats.db'
TABLE_NAMES = ['CHATS']

WAIT_TIME = 3000 # seconds

HELP_MESSAGE = '''
Wikipedia Auto Post Bot - v1.1
    > help - Show this help
    > start - Start the bot
    > search - Search the german wikipedia
    > end - End the bot
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
            CHAT_ID     NUMBER	UNIQUE	NOT NULL
        )''')

    con.close()

def insertChat(chat_id):
    try:
        con = db.connect(DB_NAME)

        print 'insert into database'
        con.execute('INSERT INTO ' + TABLE_NAMES[0] + ' VALUES ( ? )', (chat_id, ))
        print 'inserted'

        con.commit()
    except Exception as e:
        print str(e)
    finally:
        con.close()

def chatJoined(chat_id):
    try:
        con = db.connect(DB_NAME)

        print 'searching database'
        con.execute('INSERT INTO ' + TABLE_NAMES[0] + ' VALUES ( ? )', (chat_id, ))
        print 'searched'

        con.commit()
    except Exception as e:
        print str(e)
    finally:
        con.close()

def deleteChat(chat_id):
    try:
        con = db.connect(DB_NAME)

        print 'remove from database'
        con.execute('DELETE FROM ' + TABLE_NAMES[0] + ' WHERE chat_id = ?', (chat_id, ))
        print 'removed'

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
        #time.sleep(WAIT_TIME)
        updates = bot.getUpdates(offset = messageOffset, limit = 1, timeout = WAIT_TIME)
    
        if len(updates) is not 0:
            for u in updates:
                
                messageOffset = u.update_id + 1
    
                chat_id = u.message.chat_id
                message = u.message.text.lower()

                if message.startswith(u'/start'):
                    insertChat(chat_id)
                    sendMessage(chat_id, 'Senden Sie mir Ihren Suchbegriff: "/search <wort>"')
                elif message.startswith(u'/stop'):
                    deleteChat(chat_id)
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