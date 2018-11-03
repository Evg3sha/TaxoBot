from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup

from celery import uuid

import location
import logging

import settings
import city
import ya_price
import tasks
from tasks import comparison

logging.basicConfig(format=('%(name)s - %(levelname)s - %(message)s'), level=logging.INFO, filename='Bot.log')

FROM, TO, PRICE, SELECT = range(4)


def main():
    mybot = Updater(settings.API_KEY)
    dp = mybot.dispatcher
    conv_handler = ConversationHandler(
        # entry_points=[CommandHandler('start', to_address)],

        entry_points=[CommandHandler('start', start, pass_user_data=True),
                        RegexHandler('^(Старт)$', start, pass_user_data=True)],

        states={
            FROM: [MessageHandler(Filters.location, from_address, pass_user_data=True),
                   RegexHandler('^(Отмена заказа)$', cancel, pass_user_data=True),
                   RegexHandler('^(Старт)$', start, pass_user_data=True),
                   MessageHandler(Filters.text, from_address, pass_user_data=True),
                   ],

            TO: [MessageHandler(Filters.location, to_address, pass_user_data=True),
                 RegexHandler('^(Отмена заказа)$', cancel, pass_user_data=True),
                 RegexHandler('^(Старт)$', start, pass_user_data=True),
                 MessageHandler(Filters.text, to_address, pass_user_data=True),
                 ],

            PRICE: [MessageHandler(Filters.text, start_price, pass_user_data=True),
                    RegexHandler('^(Отмена заказа)$', cancel, pass_user_data=True),
                    RegexHandler('^(Старт)$', start, pass_user_data=True),
                    ],

            SELECT: [RegexHandler('^(Отмена заказа)$', cancel, pass_user_data=True),
                     MessageHandler(Filters.text, select, pass_user_data=True),
                     RegexHandler('^(Старт)$', start, pass_user_data=True),
                     MessageHandler(Filters.location, select, pass_user_data=True), ]

        },

        fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(RegexHandler('^(Отмена заказа)$', cancel, pass_user_data=True))
    mybot.start_polling()
    mybot.idle()


def start(bot, update, user_data):
    share_location_start = KeyboardButton('Точка начала маршрута', request_location=True)
    cancel_button = KeyboardButton('Отмена заказа')
    start_price = KeyboardButton('Задать желаемую цену')
    start_button = KeyboardButton('Старт')
    reply_markup = ReplyKeyboardMarkup([[share_location_start, start_price],[cancel_button, start_button]], resize_keyboard=True,
                                                                                                        one_time_keyboard=True)
    bot.send_message(update.message.chat_id,
                     'Привет, я помогу выбрать самое дешевое такси, введите адрес, отправьте геолокацию '
                     'или нажмите кнопку "Задать желаемую цену".',
                     reply_markup=reply_markup)
    if 'task_id' in user_data:
        task_id = user_data['task_id']
        tasks.app.control.revoke(task_id, terminate=True)

    return SELECT


def select(bot, update, user_data):
    text = update.message.text
    if text == 'Задать желаемую цену':
        update.message.reply_text('Введите цену и я в течении 30 минут попробую найти вам такси за эти деньги или дешевле')
        return PRICE
    else:
        return from_address(bot, update, user_data)


def cancel(bot, update, user_data):
    if 'task_id' in user_data:
        task_id = user_data['task_id']
        tasks.app.control.revoke(task_id, terminate=True)
    update.message.reply_text('До скорой встречи! Чтобы начать все с начала нажмите /start')
    return ConversationHandler.END


def start_price(bot, update, user_data):
    command = update.message.text
    if command == 'Отмена заказа':
        update.message.reply_text('До скорой встречи! Чтобы начать все с начала нажмите /start')
        return ConversationHandler.END
    else:
        user_data['user_price'] = float(command)
        update.message.reply_text('Точка начала маршрута')
        return FROM


def arg(list):
    add1 = float(list[0])
    add2 = float(list[1])
    return add1, add2


def from_address(bot, update, user_data):
    command = update.message.text
    try:
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
    except Exception as ex:
        logging.exception(ex)
        update.message.reply_text(
            'Что-то пошло не так... Нажмите "Отмена заказа" и начните все сначала.')

    return TO


def to_address(bot, update, user_data):
    # def to_address(bot, update):
    command2 = update.message.text
    # command2 = 'Тверская 1'
    try:
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

            # from_lat = 55.739761
            # from_long = 37.617006
            # to_lat = 55.736952
            # to_long = 37.62764

            price_yandex = ya_price.price(from_long, from_lat, to_long, to_lat)
            price_city = city.get_est_cost(from_lat, from_long, to_lat, to_long)

            if price_city < price_yandex:
                update.message.reply_text(
                    'Цена в Яндекс.Такси: {}. Цена в Ситимобил: {}. [Перейдите в приложение Ситимобил](http://onelink.to/5m3naz)'.format(
                        price_yandex, float(price_city)), parse_mode='Markdown')
            else:
                update.message.reply_text(
                    'Цена в Яндекс.Такси: {}. Цена в Ситимобил: {}. [Перейдите в приложение Яндекс.Такси](https://3.redirect.appmetrica.yandex.com/route?utm_source=serp&utm_medium=org&start-lat={}&start-lon={}&end-lat={}&end-lon={}&ref=402d5282d269410b9468ae538389260b&appmetrica_tracking_id=1178268795219780156)'.format(
                        price_yandex, float(price_city), from_lat, from_long, to_lat, to_long), parse_mode='Markdown')

            if 'user_price' in user_data:
                user_price = user_data['user_price']
                # user_price = 500
                task_id = uuid()
                comparison.apply_async((update.message.chat_id, user_price, from_long, from_lat, to_long, to_lat),
                                       task_id=task_id)
                user_data['task_id'] = task_id
                # comparison.delay(update.message.chat_id, user_price, from_long, from_lat, to_long, to_lat)


        else:
            command = update.message.location
            to_long_location = command['longitude']
            to_lat_location = command['latitude']
            from_long_location = user_data['from_long']
            from_lat_location = user_data['from_lat']

            price_yandex = ya_price.price(from_long_location, from_lat_location, to_long_location, to_lat_location)
            price_city = city.get_est_cost(from_lat_location, from_long_location, to_lat_location, to_long_location)

            if price_city < price_yandex:
                update.message.reply_text(
                    'Цена в Яндекс.Такси: {}. Цена в Ситимобил: {}. [Перейдите в приложение Ситимобил](http://onelink.to/5m3naz)'.format(
                        price_yandex, float(price_city)), parse_mode='Markdown')
            else:
                update.message.reply_text(
                    'Цена в Яндекс.Такси: {}. Цена в Ситимобил: {}. [Перейдите в приложение Яндекс.Такси](https://3.redirect.appmetrica.yandex.com/route?utm_source=serp&utm_medium=org&start-lat={}&start-lon={}&end-lat={}&end-lon={}&ref=402d5282d269410b9468ae538389260b&appmetrica_tracking_id=1178268795219780156)'.format(
                        price_yandex, float(price_city), from_lat_location, from_long_location, to_lat_location,
                        to_long_location), parse_mode='Markdown')
                
            if 'user_price' in user_data:
                user_price = user_data['user_price']
                # user_price = 500
                task_id = uuid()
                comparison.apply_async((update.message.chat_id, user_price, from_long_location, from_lat_location, to_long_location, to_lat_location),
                                       task_id=task_id)
                user_data['task_id'] = task_id
                # comparison.delay(update.message.chat_id, user_price, from_long, from_lat, to_long, to_lat)

    except Exception as ex:
        logging.exception(ex)
        update.message.reply_text(
            'Что-то пошло не так... Нажмите "Отмена заказа" и начните все сначала.')


main()
