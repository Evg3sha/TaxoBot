from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import logging

import settings

logging.basicConfig(format=('%(name)s - %(levelname)s - %(message)s'), level=logging.INFO, filename='Tax_o_Bot.log')


# Функция, которая соединяется с платформой Telegram, "тело" нашего бота
def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', stert, pass_user_data=True))

    mybot.start_polling()
    mybot.idle()


def stert(bot, update):
    text = 'Добро пожаловать в TaxiBot.'
    update.message.reply_text(text)

# Вызываем функцию - эта строчка собственно запускает бота
main()
