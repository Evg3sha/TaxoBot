from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import logging
import settings
import yataxi
import utaxi
import location

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot_test.log'
                    )

def main():
    mybot = Updater('654148912:AAHpi7o2PulM7KhL-UUl4dskKEDeA3zNI9I')


    dp = mybot.dispatcher
    dp.add_handler(MessageHandler(Filters, location))


    mybot.start_polling()
    mybot.idle()



def location(bot, update):
    share_location_start = KeyboardButton('Точка начала маршрута', request_location=True)
    reply_markup = ReplyKeyboardMarkup([[share_location_start]], resize_keyboard=True)
    print(update.message)


main()