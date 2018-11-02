from celery import Celery
from celery.exceptions import MaxRetriesExceededError

import ya_price
import city
from telegram import Bot
from telegram.ext import RegexHandler
import settings

app = Celery('tasks', backend='redis://localhost:6379/0', broker='redis://127.0.0.1:6379//')


@app.task
def comparison(chat_id, user_price, from_long, from_lat, to_long, to_lat):
    mybot = Bot(settings.API_KEY)
    dp = mybot.dispatcher
    dp.add_handler(RegexHandler('^(Отмена заказа)$', cancel))

    price_ya = ya_price.price(from_long, from_lat, to_long, to_lat)

    price_city = city.get_est_cost(from_lat, from_long, to_lat, to_long)

    ya_test = price_ya - 20 < user_price < price_ya + 20
    city_test = float(price_city) - 20 < user_price < float(price_city) + 20

    if city_test and ya_test:
        if float(price_city) < price_ya:
            mybot.send_message(chat_id,
                               '[Цена в пределах допустимого диапазона. Перейдите в приложение Ситимобил](http://onelink.to/5m3naz)',
                               parse_mode='Markdown')
        else:
            mybot.send_message(chat_id,
                               '[Цена в пределах допустимого диапазона. Перейдите в приложение Яндекс.Такси](https://3.redirect.appmetrica.yandex.com/route?utm_source=serp&utm_medium=org&start-lat={}&start-lon={}&end-lat={}&end-lon={}&ref=402d5282d269410b9468ae538389260b&appmetrica_tracking_id=1178268795219780156)',
                               parse_mode='Markdown')
    else:
        if city_test:
            mybot.send_message(chat_id,
                               '[Цена в пределах допустимого диапазона. Перейдите в приложение Ситимобил](http://onelink.to/5m3naz)',
                               parse_mode='Markdown')

        elif ya_test:
            mybot.send_message(chat_id,
                               '[Цена в пределах допустимого диапазона. Перейдите в приложение Яндекс.Такси](https://3.redirect.appmetrica.yandex.com/route?utm_source=serp&utm_medium=org&start-lat={}&start-lon={}&end-lat={}&end-lon={}&ref=402d5282d269410b9468ae538389260b&appmetrica_tracking_id=1178268795219780156)',
                               parse_mode='Markdown')

        else:
            mybot.send_message(chat_id,
                               'Ищем подходящую цену...Цена в Яндекс.Такси: {}. Цена в Ситимобил: {}.'.format(price_ya,
                                                                                                              float(
                                                                                                                  price_city)))
            try:
                comparison.retry(countdown=300, max_retries=6)
            except MaxRetriesExceededError as exc:
                mybot.send_message(chat_id, 'Ваше время истекло, попробуйте попозже.', exc=exc)


def cancel(bot, update):
    update.message.reply_text('До скорой встречи! Чтобы начать все с начала нажмите /start')