import requests
import time

base_url = 'https://api.flightradar24.com'
request_base_headers = {'User-agent': 'Flightradar24/78002 Dalvik/2.1.0 (Linux; U; Android 6.0.1; MI 4LTE MIUI/V9.5.5.0.MXDMIFA)'}


class FlightRadar:

    def get_airport(self, airport_code):
        url = base_url + '/common/v1/airport.json'
        payload = {
            'code': airport_code,
            'plugin[]': '',
            'plugin-setting[schedule][mode]': '',
            '[timestamp]': str(int(time.time())),
            'limit': "5"
        }
        print('Getting Airport \"{0}\"'.format(airport_code))
        response = requests.get(url, params=payload, headers=request_base_headers)
        print('Getting Airport {0} Response: {1}'.format(airport_code, response.text))
        return response

    def get_airport_departures(self, airport_code, page):
        url = base_url + '/common/v1/airport.json'
        payload = {
            'code': airport_code,
            'plugin[]': '',
            'plugin-setting[schedule][mode]': 'departures',
            '[timestamp]': str(int(time.time())),
            'page': str(page),
            'limit': "10"
        }
        print('Getting Airport \"{0}\" Departures Flight, Page: {1}'.format(airport_code, page))
        response = requests.get(url, params=payload, headers=request_base_headers)
        print('Getting Airport {0} Departures Response: {1}'.format(airport_code, response.text))
        return response

    def get_airport_arrivals(self, airport_code, page):
        url = base_url + '/common/v1/airport.json'
        payload = {
            'code': airport_code,
            'plugin[]': '',
            'plugin-setting[schedule][mode]': 'arrivals',
            '[timestamp]': str(int(time.time())),
            'page': str(page),
            'limit': "10"
        }
        print('Getting Airport \"{0}\" Arrivals Flight, Page: {1}'.format(airport_code, page))
        response = requests.get(url, params=payload, headers=request_base_headers)
        print('Getting Airport {0} Arrivals Response: {1}'.format(airport_code, response.text))
        return response

    def get_flight_by_route(self, origin, destination):
        url = base_url + '/common/v1/search-mobile-pro.json'
        payload = {
            'query': 'default',
            'origin': origin,
            'destination': destination,
            'limit': '100'
        }
        print('Getting Flights by Route, Origin: {0}, Destination: {1}'.format(origin, destination))
        response = requests.get(url, params=payload, headers=request_base_headers)
        return response

    def get_flight(self, flight):
        url = base_url + '/common/v1/flight/list.json'
        payload = {
            'query': flight,
            'fetchBy': 'flight',
            'page': '1',
            'limit': '100'
        }
        print('Getting Flight {0}'.format(flight))
        response = requests.get(url, params=payload, headers=request_base_headers)
        return response

    def query(self, search_keyword):
        url = 'https://www.flightradar24.com/v1/search/web/find'
        payload = {
            'query': search_keyword,
            'limit': '10'
        }
        print('Search for keyword: {0}'.format(search_keyword))
        response = requests.get(url, params=payload)
        return response

    def get_live_flight(self, flight_id):
        url = 'https://data-live.flightradar24.com/clickhandler/'
        payload = {
            'version': '1.5',
            'flight': flight_id
        }
        print('Get Live Flight: {0}'.format(flight_id))
        response = requests.get(url, params=payload, headers=request_base_headers)
        return response
