import os
import random
import string
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater


load_dotenv()
updater = Updater(token=os.getenv('TELEGRAM_TOKEN_EXCHANGE', 'token'))


def create_key():
    TEMP_NAME_LENGHT = 10
    symbols = string.ascii_letters + string.digits
    temp_name = ''.join(
        random.choice(symbols) for _ in range(TEMP_NAME_LENGHT))
    process = subprocess.Popen(
        ['bash', 'openvpn-1day.sh'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    process.stdout.readline()
    process.stdin.write('1\n')
    process.stdin.flush()
    process.stdin.write(f'{temp_name}\n')
    process.stdin.flush()
    process.wait()
    return temp_name


def send_key(update, context):
    chat = update.effective_chat
    temp_name = create_key()
    with open(Path().home() / f'{temp_name}.ovpn', 'rb') as document:
        context.bot.send_document(
            chat_id=chat.id,
            document=document,
        )
    os.remove(Path().home() / f'{temp_name}.ovpn')


def start(update, context):
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([
                ['/get_key']
            ], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text=('Привет!'),
        reply_markup=buttons,
    )


if __name__ == '__main__':
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('get_key', send_key))
    updater.start_polling()
    updater.idle()
