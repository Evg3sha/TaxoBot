import requests
import json
import settings


def __make_request(url, params):
    headers = {
        'Location': settings.LOCATION,
        'Accept': 'application/json'
    }
    session = requests.Session()
    req = requests.Request('GET', url, headers=headers, params=params).prepare()
    resp = session.send(req)

    if resp.status_code != 200:
        return None
    return json.loads(resp.text)


def get_location(text):
    params = {
        'format': 'json',
        'geocode': '{}'.format(text),
        'results': '1',
    }
    return __make_request('https://geocode-maps.yandex.ru/1.x/', params)

# info = get_location('ул. Тверская, дом 7')
# location = info['response']['GeoObjectCollection']['featureMember']
# for loc in location:
#    loc_name = loc['GeoObject']['Point']['pos']
#    print(loc_name)
