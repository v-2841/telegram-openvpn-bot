import asyncio
import logging
import os
import random
import string
from pathlib import Path
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          filters)


load_dotenv()
Path('logs/').mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(name)s, %(levelname)s, %(funcName)s, %(message)s',
    handlers=[RotatingFileHandler(
        'logs/main.log', maxBytes=100000, backupCount=10)],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def create_key():
    TEMP_NAME_LENGHT = 10
    symbols = string.ascii_letters + string.digits
    temp_name = ''.join(
        random.choice(symbols) for _ in range(TEMP_NAME_LENGHT))
    process = await asyncio.create_subprocess_exec(
        'bash', 'openvpn_1day.sh',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    await process.stdout.readline()
    process.stdin.write(b'1\n')
    await process.stdin.drain()
    process.stdin.write(f'{temp_name}\n'.encode('utf-8'))
    await process.stdin.drain()
    await process.wait()
    return temp_name


async def send_key(update, context):
    chat = update.effective_chat
    with open('make_key.jpg', 'rb') as photo:
        await context.bot.send_photo(
            chat_id=chat.id,
            photo=photo,
        )
    temp_name = await create_key()
    logger.info(f'Ключ создан для чата {chat.id} - {temp_name}.ovpn')
    with open(Path().home() / f'{temp_name}.ovpn', 'rb') as document:
        await context.bot.send_document(
            chat_id=chat.id,
            document=document,
        )
    os.remove(Path().home() / f'{temp_name}.ovpn')


async def start(update, context):
    chat = update.effective_chat
    logger.info(f'Старт чата {chat.id}')
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
