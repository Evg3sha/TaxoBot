import yataxi


def price(from_long, from_lat, to_long, to_lat):
    info_ya = yataxi.get_ride_cost(from_long, from_lat, to_long, to_lat)
    price = info_ya['options']
    for pri in price:
        price_yandex = pri['price']
    return price_yandex
