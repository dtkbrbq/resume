from librouteros import connect
from librouteros.query import Key
from mkt_decor_config import settings
from mkt_decor_config import server_list
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from librouteros.login import plain, token
import winrm
import re


login = settings['login']
password = settings['password']
bot_token = settings['token']

def mkt(ip, method=plain, ping='127.0.0.1', *args):
 api = connect(
    username= login,
    password= password,
    host= ip,
    login_method= method
 )

 root = api.path('/')
 firewall = api.path('ip', 'firewall', 'filter')
 comment = Key('comment')
 id = Key('.id')
 for row in firewall.select(comment, id).where(
        comment == 'ping_check'
        ):
         tuple(firewall('set', **{'disabled': True, '.id' : row.get('.id')}))
         
 scheduler = api.path('system', 'scheduler')
 name = Key('name')
 #id = Key('.id')
 for row in scheduler.select(comment, id).where(
        name == 'check lock'
        ):
         tuple(scheduler('set', **{'disabled': False, '.id' : row.get('.id')}))
 
 
 if ping != '127.0.0.1':
  ping_result = tuple(root('ping', **{'address': ping, 'count' : '1'}))
  return ping_result
      
            
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    keyboard = [[InlineKeyboardButton("decor1", callback_data='decor1'),
                 InlineKeyboardButton("decor2", callback_data='decor2')],
    
                [InlineKeyboardButton("Список пользователей", callback_data='decor')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    

def button(update, context):
    query = update.callback_query

    query.answer()
    
    if query.data == 'decor1':
        ip = settings[query.data]
        method = token
        ping = '192.168.1.18'
        result = mkt(ip, method, ping)
        query.edit_message_text(text= str(result).strip(")(}{,").format(query.data))
        
    if query.data == 'decor2':
        ip = settings[query.data]
        method = token
        ping = '192.168.0.98'
        result = mkt(ip, method, ping)
        query.edit_message_text(text= str(result).strip(")(}{,").format(query.data))

    if query.data == 'decor':        
        server_ip = server_list['decor']
        generate_menu(update, context, server_ip, query)

    if query.data in find_username:
        logoff(query.data, session)
        
def generate_menu(update, context, server_ip, query):
        global find_username
        global session
        server_user = server_list['login']
        server_password = server_list['password']
        session = winrm.Session(server_ip, auth=(server_user, server_password))
        username = session.run_ps('Get-WmiObject -Class Win32_UserAccount | Select name').std_out
        username = str(username).replace('\\r\\n', '')
        find_username = re.findall(r'[a-z,A-Z]{2,}[0-9]{0,}[a-z,A-Z]{0,}', username)
        button_list = []
        for each in find_username:
         button_list.append(InlineKeyboardButton(each, callback_data = each))
        reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=1)) #n_cols = 1 is for single column and mutliple rows
        query.message.reply_text('Какого пользователя нужно выкинуть с сервера?',reply_markup=reply_markup)
        
def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
  if header_buttons:
    menu.insert(0, header_buttons)
  if footer_buttons:
    menu.append(footer_buttons)
  return menu

def logoff(uname, session):
    match = re.search(r'[ ]{1}[0-9]{1,2}[ ]{1}', str(session.run_ps('query user '+uname+'').std_out))
    session.run_cmd('logoff ' +match.group(0))

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
    dp.add_handler(CommandHandler("removed", start))
    dp.add_handler(CommandHandler("removed", start))
    dp.add_handler(CommandHandler("removed", start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler("help", help_command))
    #dp.add_handler(CommandHandler("mkt", mkt))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
