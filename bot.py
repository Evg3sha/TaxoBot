from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import logging
import settings
import yataxi
import utaxi
import location

logging.basicConfig(format=('%(name)s - %(levelname)s - %(message)s'), level=logging.INFO, filename='Tax_o_Bot.log')

FROM_YA, TO_YA, RESULT = range(3)


# Функция, которая соединяется с платформой Telegram, "тело" нашего бота
def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    dp = mybot.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            FROM_YA: [CommandHandler('from_address', from_yandex, pass_user_data=True)],
            TO_YA: [CommandHandler('to_address', to_yandex, pass_user_data=True)],
            RESULT: [CommandHandler('results', results, pass_user_data=True)],
            # LOCATION: [RegexHandler('^(Геолокация)$')]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    mybot.start_polling()
    mybot.idle()


# Кнопки геопозиция и поделиться контактами работают только с телефона!!!
def start(bot, update):
    share_location_start = KeyboardButton('Точка начала маршрута', request_location=True)
    reply_markup = ReplyKeyboardMarkup([[share_location_start]], resize_keyboard=True)
    bot.send_message(update.message.chat_id, 'Куда машину подавать будем?', reply_markup=reply_markup)
    return FROM_YA


# Нужно сохранить результат ответа пользователя по средством user_data

# def final_destination(bot, update):
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
    return add1, add2


# Вызывается после /start
def from_yandex(bot, update, user_data):
    command = update.message.text.replace(',', '')
    command = command.split()[1:]
    info = location.get_location(command)
    locat = info['response']['GeoObjectCollection']['featureMember']
    for loc in locat:
        loc_name = loc['GeoObject']['Point']['pos']
        loc_name = loc_name.split(' ')
    add = arg(loc_name)
    ll1 = add[0]
    ll2 = add[1]
    user_data['from_lat'] = ll1
    user_data['from_long'] = ll2
    update.message.reply_text('enter destination coordinates')
    return TO_YA


def to_yandex(bot, update, user_data):
    command2 = update.message.text.replace(',', '')
    command2 = command2.split()[1:]
    info = location.get_location(command2)
    locat = info['response']['GeoObjectCollection']['featureMember']
    for loc in locat:
        loc_name = loc['GeoObject']['Point']['pos']
        loc_name = loc_name.split(' ')
    add2 = arg(loc_name)
    ll3 = add2[0]
    ll4 = add2[1]
    user_data['to_lat'] = ll3
    user_data['to_long'] = ll4
    update.message.reply_text('results ready')
    return RESULT


def results(bot, update, user_data):
    ll1 = user_data['from_long']
    ll2 = user_data['from_lat']
    ll3 = user_data['to_long']
    ll4 = user_data['to_lat']
    info = yataxi.get_ride_cost(ll1, ll2, ll3, ll4)
    price = info['options']
    for pri in price:
        price_name = pri['price']
    update.message.reply_text('Price: {}'.format(price_name))


# def from_to_uber(bot, update):
#    command = update.message.text.replace(',', '')
#    command = command.split()[1:]
#    add = arg(command)
#    ll1 = add[0]
#    ll2 = add[1]
#    ll3 = add[2]
#    ll4 = add[3]
#    info = utaxi.get_ride_cost(ll1, ll2, ll3, ll4)
#    price = info['prices'][1]
#    update.message.reply_text('Price: {}'.format(price['estimate']))


# Вызываем функцию - эта строчка собственно запускает бота
main()
