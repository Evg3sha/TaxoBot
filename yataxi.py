import requests
import json
import settings


# Отправка запроса в Яндекс
def __make_request(url, params):
    headers = {
        'YaTaxi-Api-Key': settings.YA_API_KEY,
        'Accept': 'application/json'
    }
    params['clid'] = settings.YA_CLID
    session = requests.Session()
    req = requests.Request('GET', url, headers=headers, params=params).prepare()
    resp = session.send(req)

    if resp.status_code != 200:
        return None
    return json.loads(resp.text)


# Поиск информации о регионе
def get_region_info(long, lat):
    params = {
        'll': '{},{}'.format(lat, long)
    }
    return __make_request('https://taxi-routeinfo.taxi.yandex.net/zone_info', params)


# Поиск информации о поездке
def get_ride_cost(long_from, lat_from, long_to, lat_to):
    params = {
        'rll': '{},{}~{},{}'.format(lat_from, long_from, lat_to, long_to)
    }

    return __make_request('https://taxi-routeinfo.taxi.yandex.net/taxi_info', params)

# info = get_ride_cost(55.787875, 37.600884, 55.696461, 37.771516)
# price = info['options']
# for pri in price:
#    price_name = pri['price']
#    print('Price: {}'.format(price_name))
