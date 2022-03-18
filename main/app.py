# -*- coding: utf-8 -*-

from librouteros import connect
from librouteros.query import Key
from mkt_config import settings
from mkt_config import server_list
from mkt_config import srv
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from librouteros.login import plain, token
import re
import requests
import winrm
import urllib
import ssl

# для использования winrm необходимо выполнить на сервере 2 команды:
# winrm set winrm/config/service '@{AllowUnencrypted="true"}'
# winrm set winrm/config/service/auth '@{Basic="true"}'

login = settings['login']
password = settings['password']
bot_token = settings['token']
TELEGRAM_SUPPORT_CHAT_ID = 'removed'
WELCOME_MESSAGE = 'This is test hepldesk bot'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='bot.log', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text(WELCOME_MESSAGE)

    user_info = update.message.from_user.to_dict()

    context.bot.send_message(
        chat_id=TELEGRAM_SUPPORT_CHAT_ID,
        text=f"""
📞 Connected {user_info}.
        """,
    )


def forward_to_chat(update, context):
    update.message.forward(chat_id=TELEGRAM_SUPPORT_CHAT_ID)


def forward_to_user(update, context):
    user_id = update.message.reply_to_message.forward_from.id
    context.bot.copy_message(
        message_id=update.message.message_id,
        chat_id=user_id,
        from_chat_id=update.message.chat_id
    )


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Введи свой пароль через /')


def ticket(update, context):
    match = re.search(r'[\w\.-]+@[\w\.-]+', update.message.text)
    logging.info(update.message.text)

    if hasattr(match, 'group'):
        bot: Bot = context.bot
        bot.send_message(
            chat_id='removed',
            text='Новый тикет прилетел, текст примерно такой: ' + update.message.text
        )
        update.message.reply_text('Ваша заявка принята, ожидайте ответ на указанный почтовый ящик.')

        headers = {'Content-Type': 'application/json', }

        data = '{ "description": "' + update.message.text + '", "subject": "Новый тикет от ' + match.group(
            0) + '", "email": "' + match.group(0) + '", "priority": 1, "status": 2 }'

        response = requests.post('https://removed.freshdesk.com/api/v2/tickets', headers=headers,
                                 data=data.encode('utf-8'), auth=('removed', 'removed'))
        logging.info(response)
    else:
        update.message.reply_text('Вы не указали свою почту.')

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(settings['token'], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    #dp.add_handler(MessageHandler(Filters.text, ticket))  # create ticket to freshdesk
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.chat_type.private, forward_to_chat))
    dp.add_handler(MessageHandler(Filters.chat(TELEGRAM_SUPPORT_CHAT_ID) & Filters.reply, forward_to_user))
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
