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
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start2(update, context):
    keyboard = [[InlineKeyboardButton("VPN on", callback_data='enable'),
                 InlineKeyboardButton("VPN off", callback_data='disable')]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
            
    
def mkt(method, action, *args):
  ip = settings['home']
  api = connect(
     username= login,
     password= password,
     host= ip,
     login_method= method
  ) 

  root = api.path('/')
  addr_list = api.path('ip', 'firewall', 'address-list')
  list = Key('list')
  id = Key('.id')
  for row in addr_list.select(list, id).where(
         list == 'xbox'
         ):
          tuple(addr_list(action, **{'.id' : row.get('.id')}))
         
  
def button(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    if query.data == 'enable':
        action = 'enable'
        method = plain
        result = mkt(method, action)
        query.edit_message_text(text= "ok")
    
    if query.data == 'disable':
        action = 'disable'
        method = plain
        result = mkt(method, action)
        query.edit_message_text(text= "ok")
        
    
def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введи свой пароль через /')


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
    dp.add_handler(CommandHandler("removed", start2))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("help", help_command))
    
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
