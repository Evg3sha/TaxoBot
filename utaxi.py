from uber_rides.session import Session
from uber_rides.client import UberRidesClient
import settings


def __create_client():
    session = Session(server_token=settings.U_TOKEN)
    client = UberRidesClient(session)
    return client


def get_region_info(lat, long):
    client = __create_client()
    response = client.get_products(lat, long)
    print(response.status_code)
    return response.json


def get_ride_cost(lat_from, long_from, lat_to, long_to):
    client = __create_client()
    response = client.get_price_estimates(lat_from, long_from, lat_to, long_to)
    return response.json

# 40.730209, -73.979612, 55.696461, 37.771516
# info = get_region_info(40.730209, -73.979612)
# products = info['products'][1]
# print(products['upfront_fare_enabled'])

# info2 = get_ride_cost(42.384316, -83.101800, 42.421465, -83.270715)
# price = info2['prices'][1]
# print(price['estimate'])
