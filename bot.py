from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import logging
import settings
import yataxi
import location

logging.basicConfig(format=('%(name)s - %(levelname)s - %(message)s'), level=logging.INFO, filename='Tax_o_Bot.log')

FROM, TO = range(2)


def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    dp = mybot.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            FROM: [MessageHandler(Filters.location, from_location, pass_user_data=True),
                   RegexHandler('^(Отмена заказа)$', cancel),
                   MessageHandler(Filters.text, from_yandex, pass_user_data=True)],

            TO: [MessageHandler(Filters.location, to_location, pass_user_data=True),
                 RegexHandler('^(Отмена заказа)$', cancel),
                 MessageHandler(Filters.text, to_yandex, pass_user_data=True)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(RegexHandler('^(Отмена заказа)$', cancel))
    mybot.start_polling()
    mybot.idle()


def start(bot, update):
    share_location_start = KeyboardButton('Точка начала маршрута', request_location=True)
    cancel_button = KeyboardButton('Отмена заказа')
    reply_markup = ReplyKeyboardMarkup([[share_location_start, cancel_button]], one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id,
                     'Привет, я помогу выбрать самое дешевое такси, введите адрес или отправьте геолокацию.',
                     reply_markup=reply_markup)
    return FROM


def cancel(bot, update):
    update.message.reply_text('Bye!')
    return ConversationHandler.END


def arg(list):
    add1 = float(list[0])
    add2 = float(list[1])
    return add1, add2


def from_yandex(bot, update, user_data):
    command = update.message.text.replace(',', '')
    command = command.split()
    info = location.get_location(command)
    locat = info['response']['GeoObjectCollection']['featureMember']
    for loc in locat:
        loc_name = loc['GeoObject']['Point']['pos']
        loc_name = loc_name.split(' ')
    add = arg(loc_name)
    from_lat = add[0]
    from_long = add[1]
    user_data['from_lat'] = from_lat
    user_data['from_long'] = from_long
    update.message.reply_text('enter destination coordinates')
    return TO


def to_yandex(bot, update, user_data):
    command2 = update.message.text.replace(',', '')
    command2 = command2.split()
    info = location.get_location(command2)
    locat = info['response']['GeoObjectCollection']['featureMember']
    for loc in locat:
        loc_name = loc['GeoObject']['Point']['pos']
        loc_name = loc_name.split(' ')
    add2 = arg(loc_name)
    to_lat = add2[0]
    to_long = add2[1]

    from_long = user_data['from_long']
    from_lat = user_data['from_lat']
    info = yataxi.get_ride_cost(from_long, from_lat, to_long, to_lat)
    price = info['options']
    for pri in price:
        price_name = pri['price']
    update.message.reply_text('Price: {}'.format(price_name))


def from_location(bot, update, user_data):
    command = update.message.location
    long = command['longitude']
    lat = command['latitude']
    user_data['from_lat'] = lat
    user_data['from_long'] = long
    update.message.reply_text('enter destination coordinates')

    return TO


def to_location(bot, update, user_data):
    command = update.message.location
    long2 = command['longitude']
    lat2 = command['latitude']
    long1 = user_data['from_long']
    lat1 = user_data['from_lat']
    info = yataxi.get_ride_cost(lat1, long1, lat2, long2)
    price = info['options']
    for pri in price:
        price_name = pri['price']
    update.message.reply_text('Price: {}'.format(price_name))


main()
