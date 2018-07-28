import time

from linebot.models import (
    BubbleContainer, CarouselContainer
)

from flight_radar import FlightRadar

flight_api = FlightRadar()


class FlightInfo:

    def format_timezone(self, timezone_epoch):
        if timezone_epoch < 0:
            return str(timezone_epoch / 3600).rjust(2, '0')
        else:
            return "+" + str(timezone_epoch / 3600).rjust(2, '0')

    def filter_data(self, data_list):
        for data in data_list:
            if data['aircraft']['model']['text'] is not None:
                return data

    def get_flight_info(self, flight_no):
        response = flight_api.get_flight(flight_no)
        data = response.json()['result']['response']['data']
        if data is None:
            return "Flight \"{0}\" is unavailable".format(flight_no)
        data = self.filter_data(data)
        flight_number = data['identification']['number']['default']
        airline = data['airline']['name']
        origin_airport_code = data['airport']['origin']['code']['iata']
        origin_city = data['airport']['origin']['position']['region']['city']
        origin_tz = self.format_timezone(data['airport']['origin']['timezone']['offset'])
        origin_time = time.strftime('%H:%M', time.localtime(data['time']['scheduled']['departure']))
        destination_airport_code = data['airport']['destination']['code']['iata']
        destination_city = data['airport']['destination']['position']['region']['city']
        destination_tz = self.format_timezone(data['airport']['destination']['timezone']['offset'])
        destination_time = time.strftime('%H:%M', time.localtime(data['time']['scheduled']['arrival']))
        aircraft = data['aircraft']['model']['text']
        aircraft_image = response.json()['result']['response']['aircraftImages'][0]['images']['medium'][0]['src']
        bubble = {
            "type": "bubble",
            "styles": {
                "body": {
                    "backgroundColor": "#111111"
                }
            },
            "hero": {
                "type": "image",
                "url": aircraft_image,
                "size": "full",
                "aspectRatio": "16:9",
                "aspectMode": "fit"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "spacing": "md",
                                "contents": [
                                    {
                                        "type": "image",
                                        "url": "https://image.ibb.co/ddeQ18/airplane_mode_on_icon_512.png",
                                        "size": "xs",
                                        "flex": 0
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": flight_number,
                                                "weight": "bold",
                                                "size": "xxl",
                                                "color": "#ffffff"
                                            },
                                            {
                                                "type": "text",
                                                "text": airline,
                                                "size": "xs",
                                                "color": "#ffffff"
                                            },
                                            {
                                                "type": "text",
                                                "text": aircraft,
                                                "size": "xxs",
                                                "color": "#ffffff"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "separator"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "DEPARTURE",
                                "size": "xs",
                                "color": "#ffffff",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "ARRIVAL",
                                "size": "xs",
                                "color": "#ffffff",
                                "align": "center"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": origin_airport_code,
                                        "size": "xxl",
                                        "weight": "bold",
                                        "align": "center",
                                        "color": "#ffffff"
                                    },
                                    {
                                        "type": "text",
                                        "text": origin_city,
                                        "size": "sm",
                                        "wrap": True,
                                        "align": "center",
                                        "color": "#ffffff"
                                    },
                                    {
                                        "type": "text",
                                        "text": "{0} (UTC {1})".format(origin_time, origin_tz),
                                        "size": "xxs",
                                        "align": "center",
                                        "color": "#ffffff"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": destination_airport_code,
                                        "size": "xxl",
                                        "weight": "bold",
                                        "align": "center",
                                        "color": "#ffffff"
                                    },
                                    {
                                        "type": "text",
                                        "text": destination_city,
                                        "size": "sm",
                                        "wrap": True,
                                        "align": "center",
                                        "color": "#ffffff"
                                    },
                                    {
                                        "type": "text",
                                        "text": "{0} (UTC {1})".format(destination_time, destination_tz),
                                        "size": "xxs",
                                        "align": "center",
                                        "color": "#ffffff"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        bubble_container = BubbleContainer.new_from_json_dict(bubble)
        bubble_container.styles.__delattr__('type')
        return bubble_container