from linebot.models import (
    ConfirmTemplate, MessageAction
)

from flight_radar import FlightRadar
from user_state import UserState

flight_api = FlightRadar()


class Airport:

    def check_airport(self, airport_code):
        response = flight_api.get_airport(airport_code)
        airport = response.json()['result']['response']['airport']
        if airport['pluginData']['aircraftCount'] is not None:
            airport_name = airport['pluginData']['details']['name']
            city = airport['pluginData']['details']['position']['region']['city']
            country = airport['pluginData']['details']['position']['country']['name']
            confirm_template = ConfirmTemplate(text='{0}, {1} {2}. Is it correct?'.format(airport_name, city, country),
                                               actions=[
                MessageAction(label='Yes', text='CONFIRM YES AIRPORT {0}'.format(str(airport_code).upper())),
                MessageAction(label='No', text='CONFIRM NO AIRPORT {0}'.format(str(airport_code).upper()))
            ])
            return confirm_template
        return "Can't Find Airport: {0}".format(str(airport_code).upper())

    def save_user_airport(self, db, user_id, airport_code):
        users = db.collection('users')
        user = users.filter(lambda user: user['user_id'].decode('utf-8') == user_id)
        print("filter user: {}".format(user))
        if len(user) == 1:
            # found
            record_id = user[0]['__id']
            users.update(record_id, {
                'user_id': user_id,
                'state': UserState.AIRPORT.value,
                'airport': airport_code
            })
        else:
            # create new
            user = {
                'user_id': user_id,
                'state': UserState.AIRPORT.value,
                'airport': airport_code
            }
            users.store(user)
        return "AIRPORT {0} IS ALREADY SET FOR YOU! 🤗"
