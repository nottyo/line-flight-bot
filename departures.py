import time

from linebot.models import (
    BubbleContainer, CarouselContainer
)

from flight_radar import FlightRadar

flight_api = FlightRadar()


class Departures:

    def create_departures_data(self, airport_code):
        carousel = {
            'type': 'carousel',
            'contents': []
        }
        for count in range(1, 6):
            response = flight_api.get_airport_departures(airport_code, count)
            resp_json = response.json()['result']['response']
            airport_name = resp_json['airport']['pluginData']['details']['name']
            airport_code = resp_json['airport']['pluginData']['details']['code']['iata']
            airport_name = airport_name + ' ({0})'.format(airport_code)
            bubble = {
                'type': 'bubble',
                "styles": {
                    "header": {
                        "backgroundColor": "#fffa11"
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
                            "url": "https://www.iconsplace.com/download/black-airplane-takeoff-256.png",
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
                                    "text": "DEPARTURES",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#000000"
                                },
                                {
                                    "type": "text",
                                    "text": airport_name,
                                    "size": "xxs",
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
                                    "text": "TIME",
                                    "color": "#ffffff",
                                    "weight": "bold",
                                    "size": "xs",
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": "TO",
                                    "color": "#ffffff",
                                    "weight": "bold",
                                    "size": "xs",
                                    "flex": 5
                                },
                                {
                                    "type": "text",
                                    "text": "FLIGHT",
                                    "color": "#ffffff",
                                    "weight": "bold",
                                    "size": "xs",
                                    "flex": 2,
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
            schedules = resp_json['airport']['pluginData']['schedule']['departures']['data']
            bubble_body_contents = bubble['body']['contents']
            for schedule in schedules:
                flight_no = schedule['flight']['identification']['number']['default']
                status_text = str(schedule['flight']['status']['generic']['status']['text']).capitalize()
                status_color = schedule['flight']['status']['generic']['status']['color']
                airline_name = schedule['flight']['airline']['short']
                destination_city = str(schedule['flight']['airport']['destination']['position']['region']['city']).upper()
                destination_iata = str(schedule['flight']['airport']['destination']['code']['iata'])
                departure_time = time.strftime('%H:%M', time.localtime(schedule['flight']['time']['scheduled']['departure']))
                bubble_body_contents.append(
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": departure_time,
                                "color": "#ffffff",
                                "size": "xxs",
                                "flex": 2
                            },
                            {
                                "type": "text",
                                "text": destination_city + ' ({0})'.format(destination_iata),
                                "color": "#ffffff",
                                "size": "xxs",
                                "wrap": True,
                                "flex": 5
                            },
                            {
                                "type": "text",
                                "text": flight_no,
                                "color": "#ffffff",
                                "size": "xxs",
                                "flex": 2,
                                "align": "end"
                            }
                        ]
                    }
                )
            bubble_container = BubbleContainer.new_from_json_dict(bubble)
            bubble_container.styles.__delattr__('type')
            carousel['contents'].append(bubble_container)
        carousel_container = CarouselContainer.new_from_json_dict(carousel)
        return carousel_container
