from celery import Celery
import ya_price
import city
from telegram import Bot
import settings

app = Celery('tasks', backend='redis://localhost:6379/0', broker='redis://127.0.0.1:6379//')


@app.task
def add(x, y):
    return x + y


@app.task
def comparison(chat_id, user_price, from_long, from_lat, to_long, to_lat):
    mybot = Bot(settings.API_KEY)

    price_ya = ya_price.price(from_long, from_lat, to_long, to_lat)
    price_city = city.get_est_cost(from_lat, from_long, to_lat, to_long)

    ya_test = price_ya - 10 < user_price < price_ya + 10
    city_test = float(price_city) - 10 < user_price < float(price_city) + 10

    if city_test and ya_test:
        if float(price_city) < price_ya:
            mybot.send_message(chat_id, 'Вам подойдет Ситимобил!')
        else:
            mybot.send_message(chat_id, 'Вам подойдет Яндекс.Такси!')
    else:
        if city_test:
            mybot.send_message(chat_id, 'Вам подойдет Ситимобил!')

        elif ya_test:
            mybot.send_message(chat_id, 'Вам подойдет Яндекс.Такси!')

        else:
            mybot.send_message(chat_id, 'Ищем подходящую цену...')
            comparison.retry(countdown=6, max_retries=3)
