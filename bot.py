from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
import logging
import settings
import yataxi
import location
import city

logging.basicConfig(format=('%(name)s - %(levelname)s - %(message)s'), level=logging.INFO, filename='Tax_o_Bot.log')

FROM, TO = range(2)


def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)
    dp = mybot.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            FROM: [MessageHandler(Filters.location, from_address, pass_user_data=True),
                   RegexHandler('^(Отмена заказа)$', cancel),
                   MessageHandler(Filters.text, from_address, pass_user_data=True)],

            TO: [MessageHandler(Filters.location, to_address, pass_user_data=True),
                 RegexHandler('^(Отмена заказа)$', cancel),
                 MessageHandler(Filters.text, to_address, pass_user_data=True)],
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


def from_address(bot, update, user_data):
    command = update.message.text
    if update.message.location is None:
        command = command.replace(',', '').split()
        info = location.get_location(command)
        locat = info['response']['GeoObjectCollection']['featureMember']
        for loc in locat:
            loc_name = loc['GeoObject']['Point']['pos']
            loc_name = loc_name.split(' ')
        add = arg(loc_name)
        from_long = add[0]
        from_lat = add[1]
        user_data['from_lat'] = from_lat
        user_data['from_long'] = from_long
        update.message.reply_text('Введите конечную точку маршрута или отправте геопозицию.')
    else:
        command = update.message.location
        from_long_location = command['longitude']
        from_lat_location = command['latitude']
        user_data['from_lat'] = from_lat_location
        user_data['from_long'] = from_long_location
        update.message.reply_text('Введите конечную точку маршрута или отправте геопозицию.')
    return TO


def to_address(bot, update, user_data):
    command2 = update.message.text
    if update.message.location is None:
        command2 = command2.replace(',', '').split()
        info = location.get_location(command2)
        locat = info['response']['GeoObjectCollection']['featureMember']
        for loc in locat:
            loc_name = loc['GeoObject']['Point']['pos']
            loc_name = loc_name.split(' ')
        add2 = arg(loc_name)
        to_long = add2[0]
        to_lat = add2[1]
        from_long = user_data['from_long']
        from_lat = user_data['from_lat']
        info_ya = yataxi.get_ride_cost(from_long, from_lat, to_long, to_lat)
        price_city = city.get_est_cost(from_lat, from_long, to_lat, to_long)
        price = info_ya['options']
        for pri in price:
            price_yandex = pri['price']
        update.message.reply_text(
            'Цена в Яндекс.Такси: {}, Цена в Ситимобил: {}'.format(price_yandex, float(price_city)))
    else:
        command = update.message.location
        to_long_location = command['longitude']
        to_lat_location = command['latitude']
        from_long_location = user_data['from_long']
        from_lat_location = user_data['from_lat']
        info_ya = yataxi.get_ride_cost(from_long_location, from_lat_location, to_long_location, to_lat_location)
        price_city = city.get_est_cost(from_lat_location, from_long_location, to_lat_location, to_long_location)
        price = info_ya['options']
        for pri in price:
            price_yandex = pri['price']
        update.message.reply_text(
            'Цена в Яндекс.Такси: {}, Цена в Ситимобил: {}'.format(price_yandex, float(price_city)))


main()
