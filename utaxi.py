from uber_rides.session import Session
from uber_rides.client import UberRidesClient
import settings


def __create_client():
    session = Session(server_token=settings.U_TOKEN)
    client = UberRidesClient(session)
    return client


def get_region_info(long, lat):
    client = __create_client()
    response = client.get_products(lat, long)
    print(response.status_code)
    return response.json


def get_ride_cost(long_from, lat_from, long_to, lat_to):
    client = __create_client()
    response = client.get_price_estimates(lat_from, long_from, lat_to, long_to)
    return response.json


print(get_region_info(40.690207, -73.966176))  # , 55.696461, 37.771516
# price = info['options']
# for pri in price:
#    price_name = pri['price']
#    print('Price: {}'.format(price_name))
