import requests
import time

base_url = 'https://api.flightradar24.com'


class FlightRadar:

    def get_airport_departures(self, airport_code, page):
        url = base_url + '/common/v1/airport.json'
        request_base_headers = {'User-agent': 'nottyo/1.0'}
        payload = {
            'code': airport_code,
            '[mode]': 'departures',
            '[timestamp]': str(int(time.time())),
            'page': str(page),
            'limit': "10"
        }
        print('Getting Airport \"{0}\" Departures Flight, Page: {1}'.format(airport_code, page))
        response = requests.get(url, params=payload, headers=request_base_headers)
        return response

    def get_airport_arrivals(self, airport_code, page):
        url = base_url + '/common/v1/airport.json'
        request_base_headers = {'User-agent': 'nottyo/1.0'}
        payload = {
            'code': airport_code,
            '[mode]': 'arrivals',
            '[timestamp]': str(int(time.time())),
            'page': str(page),
            'limit': "10"
        }
        print('Getting Airport \"{0}\" Arrivals Flight, Page: {1}'.format(airport_code, page))
        response = requests.get(url, params=payload, headers=request_base_headers)
        return response

