from celery import Celery
from celery.exceptions import MaxRetriesExceededError

import ya_price
import city
from telegram import Bot
import settings

app = Celery('tasks', backend='redis://localhost:6379/0', broker='redis://127.0.0.1:6379//')


@app.task
def comparison(chat_id, user_price, from_long, from_lat, to_long, to_lat):
    mybot = Bot(settings.API_KEY)

    price_ya = ya_price.price(from_long, from_lat, to_long, to_lat)

    price_city = city.get_est_cost(from_lat, from_long, to_lat, to_long)

    ya_test = price_ya <= user_price < price_ya + 50
    city_test = float(price_city) <= user_price < float(price_city) + 50

    if city_test and ya_test:
        if float(price_city) < price_ya:
            mybot.send_message(chat_id,
                               'Цена в пределах допустимого диапазона.[Перейдите в приложение Ситимобил](http://onelink.to/5m3naz)'.format(
                                   price_ya, float(price_city)), parse_mode='Markdown')
        else:
            mybot.send_message(chat_id,
                               'Цена в пределах допустимого диапазона.[Перейдите в приложение Яндекс.Такси](https://3.redirect.appmetrica.yandex.com/route?utm_source=serp&utm_medium=org&start-lat={}&start-lon={}&end-lat={}&end-lon={}&ref=402d5282d269410b9468ae538389260b&appmetrica_tracking_id=1178268795219780156)'.format(
                                   price_ya, float(price_city), from_lat, from_long, to_lat, to_long),
                               parse_mode='Markdown')
    else:
        if city_test:
            mybot.send_message(chat_id,
                               'Цена в пределах допустимого диапазона.[Перейдите в приложение Ситимобил](http://onelink.to/5m3naz)'.format(
                                   price_ya, float(price_city)), parse_mode='Markdown')

        elif ya_test:
            mybot.send_message(chat_id,
                               'Цена в пределах допустимого диапазона.[Перейдите в приложение Яндекс.Такси](https://3.redirect.appmetrica.yandex.com/route?utm_source=serp&utm_medium=org&start-lat={}&start-lon={}&end-lat={}&end-lon={}&ref=402d5282d269410b9468ae538389260b&appmetrica_tracking_id=1178268795219780156)'.format(
                                   price_ya, float(price_city), from_lat, from_long, to_lat, to_long),
                               parse_mode='Markdown')

        else:
            mybot.send_message(chat_id,
                               'Вы хотели поехать за {} руб. Цена в Яндекс.Такси: {}. Цена в Ситимобил: {}. Продолжаю поиск, ожидайте, я сообщу как найду подходящий вариант'.format(
                                   user_price, price_ya,
                                   float(
                                       price_city)))
            try:
                comparison.retry(countdown=600, max_retries=2)
            except MaxRetriesExceededError as exc:
                mybot.send_message(chat_id,
                                   'Не удалось найти такси за вашу цену, попробуйте попозже или не будьте такими жадными.',
                                   exc=exc)
