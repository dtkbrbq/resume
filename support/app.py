from mkt_config import settings, TELEGRAM_SUPPORT_CHAT_ID
import logging
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
import sqlite3
from datetime import datetime
import re

WELCOME_MESSAGE = 'Введите ИНН вашей организации.'


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text(WELCOME_MESSAGE)


def check_inn(update, context):
    user_input = update.message.text

    sqlite_connection = sqlite3.connect('sqlite_python.db')
    cursor = sqlite_connection.cursor()
    cursor.execute("select id from users where chat_id=?", (update.message.chat_id,))
    fast_check = cursor.fetchall()
    if len(fast_check) == 0:
      inn=re.match(r'\d\d\d\d\d\d\d\d\d\d',user_input)
      if inn:
        user_info = update.message.from_user.to_dict()
        sqlite_connection = sqlite3.connect('sqlite_python.db')
        cursor = sqlite_connection.cursor()
        cursor.execute("select * from inn where inn=?", (inn.group(0),))
        existing_inn = cursor.fetchall()
        if existing_inn:
            user_info = update.message.from_user.to_dict()
            sqlite_connection = sqlite3.connect('sqlite_python.db')
            cursor = sqlite_connection.cursor()
            cursor.execute("INSERT OR IGNORE INTO users (chat_id,name,username,inn) VALUES (?,?,?,?)", (update.message.chat_id, user_info["first_name"], user_info["username"], inn.group(0)))
            sqlite_connection.commit()

            cursor.execute("CREATE TABLE chat_"+str(update.message.chat_id)+" (id integer unique primary key, chat_id integer, name TEXT, message TEXT, time TEXT);")
            sqlite_connection.commit()

            context.bot.send_message(
                chat_id=TELEGRAM_SUPPORT_CHAT_ID,
                text=f"""📞 Connected {user_info}.""",)
            update.message.reply_text("ИНН успешно проверен. Какой у Вас вопрос?")
        else:
            update.message.reply_text("Такого ИНН в базе нет, давай до свидания.")
      else:
        update.message.reply_text("Неверный ИНН, в ИНН должно быть 10 цифр.")
    else:
        forward_to_chat(update, context)



def forward_to_chat(update, context):
    user_info = update.message.from_user.to_dict()

    sqlite_connection = sqlite3.connect('sqlite_python.db')
    cursor = sqlite_connection.cursor()
    cursor.execute("INSERT OR IGNORE INTO chat_"+str(update.message.chat_id)+" (chat_id,name,message,time) VALUES (?,?,?,?)", (update.message.chat_id, user_info["first_name"], update.message.text, datetime.now()))
    sqlite_connection.commit()
    update.message.forward(chat_id=TELEGRAM_SUPPORT_CHAT_ID)


def forward_to_user(update, context):
    user_id = update.message.reply_to_message.forward_from.id


    user_info = update.message.from_user.to_dict()
    sqlite_connection = sqlite3.connect('sqlite_python.db')
    cursor = sqlite_connection.cursor()
    cursor.execute("INSERT OR IGNORE INTO chat_"+str(user_id)+" (chat_id,name,message,time) VALUES (?,?,?,?)", (user_id, user_info["first_name"], update.message.text, datetime.now()))
    sqlite_connection.commit()
    context.bot.copy_message(
        message_id=update.message.message_id,
        chat_id=user_id,
        from_chat_id=update.message.chat_id
    )



def main():
    updater = Updater(settings['token'], use_context=True)
    dp = updater.dispatcher


    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.chat_type.private, check_inn))
    dp.add_handler(MessageHandler(Filters.chat_type.private, forward_to_chat))
    dp.add_handler(MessageHandler(Filters.chat(TELEGRAM_SUPPORT_CHAT_ID) & Filters.reply, forward_to_user))

    
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
