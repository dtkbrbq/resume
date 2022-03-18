from librouteros import connect
from librouteros.query import Key
from mkt_config import settings
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from librouteros.login import plain, token


login = settings['login']
password = settings['password']
bot_token = settings['token']


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

def mkt(update, context):
  user = update.message.from_user
  logging.info('{} sent by user {} and his user ID: {} '.format(update.message.text, user['username'], user['id']))
  ip = settings['ip']
  api = connect(     
     username= login,
     password= password,
     host= ip,
     login_method= token
  ) 

  root = api.path('/')
  message = update.message.text
  update.message.delete()
  addr_list = api.path('ip', 'firewall', 'address-list')
  tuple(addr_list('add', **{'list' : message.lower(), 'address' : '0.0.0.0/0', 'timeout' : '00:02:00'}))
  update.message.delete()
  
         
  
def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(settings['token'], use_context=True)


    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, mkt))

    
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
