import time

from linebot.models import (
    BubbleContainer, CarouselContainer
)

from flight_radar import FlightRadar

flight_api = FlightRadar()


class FlightByRoute:

    def slice_list_to_chunks(self, list, n):
        for i in range(0, len(list), n):
            yield list[i:i + n]

    def normalize_flight_data(self, raw_data):
        normalized_data = []
        for data in raw_data:
            data_dict = dict()
            data_dict['flight_no'] = data['identification']['number']['default']
            data_dict['airline'] = data['airline']['name']
            data_dict['departure_time'] = data['time']['scheduled']['departure']
            data_dict['arrival_time'] = data['time']['scheduled']['arrival']
            normalized_data.append(data_dict)
        normalized_data = sorted(normalized_data, key=lambda k: k['departure_time'])
        return normalized_data

    def get_flight_by_route(self, origin, destination):
        response = flight_api.get_flight_by_route(origin, destination)
        flight = response.json()['result']['response']['flight']
        origin_city = flight['data'][0]['airport']['origin']['position']['region']['city']
        destination_city = flight['data'][0]['airport']['destination']['position']['region']['city']
        no_of_flights = flight['item']['current']
        carousel = {
            'type': 'carousel',
            'contents': []
        }
        sorted_flight_data = self.normalize_flight_data(flight['data'])
        flight_data = []
        for data in sorted_flight_data:
            flight_no = data['flight_no']
            airline = data['airline']
            time_start = time.strftime('%H:%M', time.localtime(data['departure_time']))
            time_end = time.strftime('%H:%M', time.localtime(data['arrival_time']))
            flight_data.append(
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "md",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": flight_no,
                            "color": "#ffffff",
                            "size": "xxs",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": airline,
                            "color": "#ffffff",
                            "size": "xxs",
                            "wrap": True,
                            "flex": 5
                        },
                        {
                            "type": "text",
                            "text": "{0}-{1}".format(time_start, time_end),
                            "color": "#ffffff",
                            "size": "xxs",
                            "flex": 3,
                            "align": "end"
                        }
                    ]
                }
            )
        sliced_list = self.slice_list_to_chunks(flight_data, 10)
        for slices in sliced_list:
            bb = {
                "type": "bubble",
                "styles": {
                    "header": {
                        "backgroundColor": "#27a5db"
                    },
                    "body": {
                        "backgroundColor": "#000000"
                    }
                },
                "header": {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "image",
                            "url": "https://www.iconsplace.com/icons/preview/black/airplane-mode-on-256.png",
                            "size": "xs",
                            "align": "start",
                            "flex": 0
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "{0}-{1}".format(origin, destination),
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#000000"
                                },
                                {
                                    "type": "text",
                                    "text": "{0} - {1}".format(origin_city, destination_city),
                                    "size": "xs",
                                    "wrap": True,
                                    "color": "#000000"
                                },
                                {
                                    "type": "text",
                                    "text": "{0} Flights".format(no_of_flights),
                                    "size": "xs",
                                    "wrap": True,
                                    "color": "#000000"
                                }
                            ]
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "spacing": "md",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "FLIGHT",
                                    "color": "#ffffff",
                                    "weight": "bold",
                                    "size": "xxs",
                                    "flex": 0
                                },
                                {
                                    "type": "text",
                                    "text": "AIRLINE",
                                    "color": "#ffffff",
                                    "weight": "bold",
                                    "size": "xxs",
                                    "flex": 5
                                },
                                {
                                    "type": "text",
                                    "text": "TIME",
                                    "color": "#ffffff",
                                    "weight": "bold",
                                    "size": "xxs",
                                    "flex": 3,
                                    "align": "end"
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        }
                    ]
                }
            }
            for slice in slices:
                bb['body']['contents'].append(slice)
            bubble_container = BubbleContainer.new_from_json_dict(bb)
            bubble_container.styles.__delattr__('type')
            carousel['contents'].append(bubble_container)
        return CarouselContainer.new_from_json_dict(carousel)

