from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import logging
import settings
import yataxi
import utaxi

logging.basicConfig(format=('%(name)s - %(levelname)s - %(message)s'), level=logging.INFO, filename='Tax_o_Bot.log')

FROM_TO, LOCATION = range(2)


# Функция, которая соединяется с платформой Telegram, "тело" нашего бота
def main():
    mybot = Updater(settings.API_KEY)
    dp = mybot.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            FROM_TO: [CommandHandler('from_to_address', from_to_uber)],
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
    return FROM_TO

#Нужно сохранить результат ответа пользователя по средством user_data

#def final_destination(bot, update):
#   if 'location' in update.message 
#       update.message.reply_text('Теперь нужно указать куда поедем')
#       user_destination = update.message.location
#       return True


def cancel(bot, update):
    update.message.reply_text('Bye!')
    return ConversationHandler.END


def arg(list):
    add1 = float(list[0])
    add2 = float(list[1])
    add3 = float(list[2])
    add4 = float(list[3])
    return add1, add2, add3, add4


# Вызывается после /start
# Пример вызова /from_to_address 55.787875, 37.600884, 55.696461, 37.771516
def from_to_yandex(bot, update):
    command = update.message.text.replace(',', '')
    command = command.split()[1:]
    add = arg(command)
    ll1 = add[0]
    ll2 = add[1]
    ll3 = add[2]
    ll4 = add[3]
    info = yataxi.get_ride_cost(ll1, ll2, ll3, ll4)
    price = info['options']
    for pri in price:
        price_name = pri['price']
    update.message.reply_text('Price: {}'.format(price_name))


def from_to_uber(bot, update):
    command = update.message.text.replace(',', '')
    command = command.split()[1:]
    add = arg(command)
    ll1 = add[0]
    ll2 = add[1]
    ll3 = add[2]
    ll4 = add[3]
    info = utaxi.get_ride_cost(ll1, ll2, ll3, ll4)
    price = info['prices'][1]
    update.message.reply_text('Price: {}'.format(price['estimate']))

# Вызываем функцию - эта строчка собственно запускает бота
main()