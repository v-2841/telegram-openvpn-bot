import os
import random
import string
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from telegram import LabeledPrice, ReplyKeyboardMarkup, Update
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          PreCheckoutQueryHandler, filters)


load_dotenv()


async def create_key():
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


async def offer_key(update, context):
    chat_id = update.message.chat_id
    title = "VPN"
    description = "Ключ OpenVPN на 1 день"
    payload = "OpenVPN-Payload"
    currency = "USD"
    price = 1
    prices = [LabeledPrice("Ключ OpenVPN на 1 день", price * 100)]
    await context.bot.send_invoice(
        chat_id, title, description, payload,
        os.getenv('PAYMENT_PROVIDER_TOKEN', 'token'), currency, prices,
    )


async def precheckout_callback(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload != "OpenVPN-Payload":
        await query.answer(ok=False, error_message="Что-то пошло не так...")
    else:
        await query.answer(ok=True)


async def send_key(update, context):
    await update.message.reply_text("Платеж совершен!")
    chat = update.effective_chat
    temp_name = await create_key()
    with open(Path().home() / f'{temp_name}.ovpn', 'rb') as document:
        await context.bot.send_document(
            chat_id=chat.id,
            document=document,
        )
    os.remove(Path().home() / f'{temp_name}.ovpn')


async def start(update, context):
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([
                ['/get_key']
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
    application.add_handler(CommandHandler("get_key", offer_key))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, send_key)
    )
    application.run_polling(allowed_updates=Update.ALL_TYPES)
