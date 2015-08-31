import telegram
from telegram.chataction import ChatAction
import sqlite3 as db
import wikipedia

DB_NAME = 'chats.db'
API_KEY = '128176157:AAHd_NQGjtYzi6rG9q3xMrknjIOTRZINX6E'
TABLE_NAMES = ['CHATS']

HELP_MESSAGE = '''
Wikipedia Auto Post Bot - v1.0
    > help - Show this help
    > start - Start the bot
    > search - Search the german wikipedia
    > end - End the bot
'''

bot = None

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

def sendMessage(chat_id, message):
    bot.sendChatAction(chat_id, ChatAction.TYPING)
    print bot.sendMessage(chat_id, message)

def getWikiArticle(name):
    try:
        page = wikipedia.page(name).url
        return page
    except Exception as e:
        print str(e)
    
    return None

def startMainLoop():
    messageOffset = 0

    print 'Starting MainLoop'

    while True:
        updates = bot.getUpdates(offset = messageOffset, limit = 1)
    
        if len(updates) != 0:
            for u in updates:
                
                messageOffset = u.update_id + 1
    
                chat_id = u.message.chat_id
                message = u.message.text

                print message

                if message.startswith(u'/start'):
                    insertChat(chat_id)
                elif message.startswith(u'/stop'):
                    deleteChat(chat_id)
                elif message.startswith(u'/help'):
                    sendMessage(chat_id, HELP_MESSAGE)
                elif message.startswith(u'/search@wikiautopostbot'):
                    page = getWikiArticle(message.replace(u'/search@wikiautopostbot ', ''))
                    if page is not None:
                        sendMessage(chat_id, page)
                    else:
                        sendMessage(chat_id, 'Keinen Wikipedia Eintrag gefunden.')
                elif message.startswith(u'/search'):
                    page = getWikiArticle(message.replace(u'/search ', ''))
                    if page is not None:
                        sendMessage(chat_id, page)
                    else:
                        sendMessage(chat_id, 'Keinen Wikipedia Eintrag gefunden.')

init()
bot = telegram.Bot(token = API_KEY)
wikipedia.set_lang("de")

startMainLoop()