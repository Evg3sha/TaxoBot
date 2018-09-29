from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import logging
import settings
import yataxi

logging.basicConfig(format=('%(name)s - %(levelname)s - %(message)s'), level=logging.INFO, filename='Tax_o_Bot.log')

FROM_TO, LOCATION = range(2)


# Функция, которая соединяется с платформой Telegram, "тело" нашего бота
def main():
    mybot = Updater(settings.API_KEY)
    dp = mybot.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            FROM_TO: [CommandHandler('from_to_address', from_to_address)],
            # LOCATION: [RegexHandler('^(Геолокация)$')]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    mybot.start_polling()
    mybot.idle()

#Кнопки геопозиция и поделиться контактами работают только с телефона!!!
def start(bot, update):
    share_location_start = KeyboardButton('Точка начала маршрута', request_location=True)
    reply_markup = ReplyKeyboardMarkup([[share_location_start]], resize_keyboard=True)
    bot.send_message(update.message.chat_id, 'Куда машину подавать будем?', reply_markup=reply_markup)
   #если введенное значение пользователем значение == float, 
   #то выдать сообщение с просьбой отметить на карте точку назначения, через геопозицию
    if update.message.location == float:
        update.message.reply_text('Теперь нужно указать куда поедем')
        user_destination = update.message.location
        return True
    return FROM_TO


def cancel(bot, update):
    update.message.reply_text('Bye!')
    return ConversationHandler.END


# Вызывается после /start
# Пример вызова /from_to_address 55.787875, 37.600884, 55.696461, 37.771516
def from_to_address(bot, update):
    command = update.message.text.replace(',', '')
    arg = command.split()[1:]
    add1 = float(arg[0])
    add2 = float(arg[1])
    add3 = float(arg[2])
    add4 = float(arg[3])
    # Передаем агрументы в yataxi.get_ride_cost
    info = yataxi.get_ride_cost(add1, add2, add3, add4)
    price = info['options']
    for pri in price:
        price_name = pri['price']
    update.message.reply_text('Price: {}'.format(price_name))


def to_address(bot, update):
    update.message.reply_text('Проверка2!')
    pass

# Вызываем функцию - эта строчка собственно запускает бота
main()