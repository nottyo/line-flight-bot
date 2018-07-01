import requests
import time

base_url = 'https://api.flightradar24.com'
request_base_headers = {'User-agent': 'nottyo/1.0'}

flight_stat_base_url = 'https://www.flightstats.com/v2/api/flights/route/BKK/HKG/2018/7/1?numHours=24&hourOfDay=0&rqid=d2c6n4q18to'


class FlightRadar:

    def get_airport_departures(self, airport_code, page):
        url = base_url + '/common/v1/airport.json'
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

    def get_flight_by_route(self, origin, destination):
        url = base_url + '/common/v1/search-mobile-pro.json'
        payload = {
            'query': 'default',
            'origin': origin,
            'destination': destination
        }
        print('Getting Flights by Route, Origin: {0}, Destination: {1}'.format(origin, destination))
        response = requests.get(url, params=payload, headers=request_base_headers)
        return response
