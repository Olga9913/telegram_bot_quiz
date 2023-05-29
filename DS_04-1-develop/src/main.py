from films import Films
from daemon_class import Daemon
from openai_class import OpenAIFile
from database_class import SQLiteDB
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import *
import sys
import time
import logging
import random

PIDFILE = './var/run/s21_ds_bot.pid'
LOGFILE = './var/log/s21_ds_bot.log'

logging.basicConfig(filename=LOGFILE, level=logging.ERROR)
films_class = Films('./data_base_films.csv')

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text_received = update.message.text
    user = update.effective_user
    await update.message.reply_text(f'User @{user.username} (id:{user.id}) send: {text_received}')

async def film(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is not None:
        mess = update.message
    else:
        mess = update.callback_query.message
    await mess.reply_text(f'{update.effective_user.first_name}, ждите новое задание...')
    #films4 = random.sample(films, k=4)
    films4 = films_class.ramdomizer()
    i = random.randint(0, 3)
    keyboard = [
        [
            InlineKeyboardButton(films4["name_ru"].values[0], callback_data="0"),
            InlineKeyboardButton(films4["name_ru"].values[1], callback_data="1"),
        ],
        [
            InlineKeyboardButton(films4["name_ru"].values[2], callback_data="2"),
            InlineKeyboardButton(films4["name_ru"].values[3], callback_data="3"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    Oaifile = OpenAIFile(films4["name_en"].values[i])
    if Oaifile.error == "":
        await mess.reply_photo(photo=open(Oaifile.filename, 'rb'), caption="Какой это фильм?", reply_markup=reply_markup)
        sdb = SQLiteDB()
        sdb.add_question(update.effective_user.username, Oaifile.filename, films4["name_ru"].values[0],
                         films4["name_ru"].values[1], films4["name_ru"].values[2], films4["name_ru"].values[3], i)
        del sdb
    else:
        await mess.reply_text(f'Не удалось получить изображение для фильма {films4["name_en"].values[i]} '
                              f'({films4["name_ru"].values[i]}). Ошибка: {Oaifile.error}')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.data == '/film':
        logging.error(f'--- {query.data}')
        await film(update, context)
    else:
        sdb = SQLiteDB()
        new_caption = sdb.last_question(update.effective_user.username, int(query.data))
        del sdb
        await query.edit_message_caption(caption=new_caption)
        keyboard = [[InlineKeyboardButton("Ещё", callback_data="/film"),],]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sdb = SQLiteDB()
    top_users = sdb.get_top(update.effective_user.username, 10)
    del sdb
    str = ''
    for t in top_users:
        tmp = f"{t['Place']}. @{t['Username']} - правильно: {t['Count_correct']} (попыток: {t['Count_questions']})"
        if t['Username'] == update.effective_user.username:
            str = str + '<b>' + tmp + '</b>'
        else:
            str = str + tmp
        str = str + '\n'
    await update.message.reply_text(str, parse_mode='HTML')

class S21_DS_bot(Daemon):
    def run(self):
        app = ApplicationBuilder().token("5815551136:AAFzVZicVIiyHu_t0p5iK2hTrY7CBHmVMrM").build()
        app.add_handler(CallbackQueryHandler(button))
        app.add_handler(CommandHandler("film", film))
        app.add_handler(CommandHandler("top", top))
        app.add_handler(MessageHandler(filters.TEXT, text))
        app.run_polling()

if __name__ == "__main__":
    daemon = S21_DS_bot(PIDFILE)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print("Starting ...")
            try:
                daemon.start()
            except:
                pass
        elif 'stop' == sys.argv[1]:
            print("Stopping ...")
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print("Restaring ...")
            daemon.restart()
        elif 'status' == sys.argv[1]:
            try:
                pf = open(PIDFILE, 'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                pid = None
            except SystemExit:
                pid = None
            if pid:
                print('S21_DS_bot is running as pid %s' % pid)
            else:
                print('S21_DS_bot is not running.')
        else:
            print("Unknown command")
            sys.exit(2)
    else:
        print("usage: %s start|stop|restart|status" % sys.argv[0])
        sys.exit(2)

