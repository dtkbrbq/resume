 
import sqlite3

try:
    sqlite_connection = sqlite3.connect('sqlite_python.db')
    sqlite_create_table_query = '''CREATE TABLE users (
                                id integer unique primary key,
                                chat_id integer unique,
                                name TEXT,
                                username TEXT,
                                inn integer);'''
    cursor = sqlite_connection.cursor()
    cursor.execute(sqlite_create_table_query)
    sqlite_connection.commit()

    #sqlite_create_table_query = '''CREATE TABLE messages (
                                #id integer unique primary key,
                                #chat_id integer,
                                #name TEXT,
                                #message TEXT,
                                #time TEXT);'''

    sqlite_create_table_query = '''CREATE TABLE inn (
                                id integer unique primary key,
                                inn integer,
                                company_name TEXT);'''

    cursor = sqlite_connection.cursor()
    print("База данных подключена к SQLite")
    cursor.execute(sqlite_create_table_query)
    sqlite_connection.commit()
    print("Таблица SQLite создана")

    cursor.close()

except sqlite3.Error as error:
    print("Ошибка при подключении к sqlite", error)
finally:
    if (sqlite_connection):
        sqlite_connection.close()
        print("Соединение с SQLite закрыто")
