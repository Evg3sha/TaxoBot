import requests


def get_est_cost(from_lat, from_long, to_lat, to_long):
    data = {"del_latitude": str(to_lat),
            "del_longitude": str(to_long),
            "latitude": str(from_lat),
            "longitude": str(from_long),
            "tariff": 644,
            "method": "getprice",
            "ver": 5}
    r = requests.post('https://c-api.city-mobil.ru', json=data)
    if r.content and r.ok:
        r_json = r.json()
        return r_json['prices'][0]['price']
