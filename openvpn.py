import logging
import os
import random
import string
import subprocess
from pathlib import Path
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          filters)


load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    filemode='a',
    format='%(asctime)s, %(name)s, %(levelname)s, %(funcName)s, %(message)s',
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


async def create_key():
    TEMP_NAME_LENGHT = 10
    symbols = string.ascii_letters + string.digits
    temp_name = ''.join(
        random.choice(symbols) for _ in range(TEMP_NAME_LENGHT))
    process = subprocess.Popen(
        ['bash', 'openvpn_1day.sh'],
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


async def send_key(update, context):
    chat = update.effective_chat
    with open('make_key.jpg', 'rb') as photo:
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=photo,
        )
    try:
        temp_name = await create_key()
        logger.info(f'Ключ создан для чата {chat.id} - {temp_name}.ovpn')
        with open(Path().home() / f'{temp_name}.ovpn', 'rb') as document:
            await context.bot.send_document(
                chat_id=chat.id,
                document=document,
            )
        os.remove(Path().home() / f'{temp_name}.ovpn')
    except Exception as error:
        logger.error(error, exc_info=True)


async def start(update, context):
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([
                ['Получить ключ']
            ], resize_keyboard=True)
    await context.bot.send_message(
        chat_id=chat.id,
        text=('Привет!'),
        reply_markup=buttons,
    )


if __name__ == '__main__':
    application = Application.builder().token(
        os.getenv('TELEGRAM_TOKEN', 'token')).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(
        filters.Regex('^Получить ключ$'), send_key))
    application.run_polling(allowed_updates=Update.ALL_TYPES)
