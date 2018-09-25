from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup

import logging

import settings

logging.basicConfig(format=('%(name)s - %(levelname)s - %(message)s'), level=logging.INFO, filename='Tax_o_Bot.log')

FROM, TO, LOCATION = range(3)


# Функция, которая соединяется с платформой Telegram, "тело" нашего бота
def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    dp = mybot.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            FROM: [RegexHandler('^(Начальный адрес)$', from_address)],
            TO: [RegexHandler('^(Конечный адрес)$', to_address)],
            # LOCATION: [RegexHandler('^(Геолокация)$')]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    mybot.start_polling()
    mybot.idle()


def start(bot, update):
    text = 'Добро пожаловать в TaxiBot.'
    update.message.reply_text(text, reply_markup=my_keyboard())
    return FROM


def cancel(bot, update):
    update.message.reply_text('Bye!', reply_markup=my_keyboard())
    return ConversationHandler.END


def from_address(bot, update):
    update.message.reply_text('Проверка!', reply_markup=my_keyboard())
    return TO


def to_address(bot, update):
    update.message.reply_text('Проверка2!', reply_markup=my_keyboard())
    pass


def my_keyboard():
    address1 = KeyboardButton('Начальный адрес')
    address2 = KeyboardButton('Конечный адрес')
    my_keyboard = ReplyKeyboardMarkup([
        [address1, address2]
    ], resize_keyboard=True)
    return my_keyboard


# Вызываем функцию - эта строчка собственно запускает бота
main()
