import os
import re
import sys
import time
from unqlite import UnQLite

import googlemaps
from flask import Flask, request, jsonify
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, BubbleContainer, FlexSendMessage, TextSendMessage, CarouselContainer, SourceUser,
    ConfirmTemplate, TemplateSendMessage, CarouselTemplate, CarouselColumn, URIAction, MessageAction,
    LocationSendMessage
)

from airport import Airport
from arrivals import Arrivals
from departures import Departures
from flight_by_route import FlightByRoute
from flight_info import FlightInfo
from flight_radar import FlightRadar

app = Flask(__name__)

channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("CHANNEL_SECRET")
google_api_key = os.getenv('GOOGLE_API_KEY')
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if google_api_key is None:
    print('Specify GOOGLE_API_KEY as envionment variable.')
    sys.exit(1)

departures = Departures()
arrivals = Arrivals()
flight_by_route = FlightByRoute()
flight_info = FlightInfo()
airport = Airport()
flight_radar = FlightRadar()
gmaps = googlemaps.Client(key=google_api_key)

db = UnQLite('data.db')
users = db.collection('users')
users.create()


@app.route("/")
def main_route():
    return "Hello World!"


@app.route("/db")
def dump_db():
    data_list = users.all()
    results = []
    for data in data_list:
        for key in data:
            if isinstance(data[key], bytes):
                data[key] = data[key].decode('utf-8')
        results.append(data)
    return jsonify(data=results)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")

    return 'OK'


def search(search_keyword):
    response = flight_radar.query(search_keyword)
    results = response.json()['results']
    carousel_template = CarouselTemplate()
    for result in results:
        column = CarouselColumn()
        if result['type'] == 'airport':
            airport_code = result['id']
            response = flight_radar.get_airport(airport_code).json()['result']['response']
            plugin_data = response['airport']['pluginData']
            column.title = plugin_data['details']['code']['iata']
            column.text = '{0}, {1}'. \
                format(plugin_data['details']['name'], plugin_data['details']['position']['country']['name'])
            column.thumbnail_image_url = 'https://images.pexels.com/photos/804463/pexels-photo-804463.jpeg?' \
                                         'auto=compress&cs=tinysrgb&dpr=2&h=750&w=960'

            url_homepage = plugin_data['details']['url']['homepage']
            url_wiki = plugin_data['details']['url']['wikipedia']
            if url_homepage is not None:
                column.actions = [
                    URIAction(label='Home Page', uri=url_homepage)
                ]
            elif url_wiki is not None:
                column.actions = [
                    URIAction(label='Wiki Page', uri=url_wiki)
                ]
            else:
                column.actions = [
                    URIAction(label='Search Page', uri='https://www.google.co.th/search?q={0}+airport'.format(airport_code))
                ]

            carousel_template.columns.append(column)
        elif result['type'] == 'live':
            column.title = result['detail']['flight']
            print('LIVE FLIGHT: {0}'.format(result['detail']['flight']))
            flight_resp = flight_radar.get_flight(result['detail']['flight'])
            if flight_resp.status_code != 200:
                continue
            flight_data = flight_resp.json()['result']['response']['data'][0]
            departure_time = time.strftime('%H:%M', time.localtime(flight_data['time']['scheduled']['departure']))
            arrival_time = time.strftime('%H:%M', time.localtime(flight_data['time']['scheduled']['arrival']))
            flight_time = '{0}-{1}'.format(departure_time, arrival_time)
            aircraft_image = flight_resp.json()['result']['response']['aircraftImages']
            if aircraft_image is None:
                column.thumbnail_image_url = default_aircraft
            else:
                column.thumbnail_image_url = aircraft_image[0]['images']['medium'][0]['src']
            text = 'LIVE Flight Time: {0}\nRoute: {1} -> {2}'.format(flight_time, result['detail']['schd_from'],
                                                                       result['detail']['schd_to'])
            text = (text[:55] + '..') if len(text) > 55 else text
            column.text = text
            column.actions = [
                MessageAction(label=result['detail']['flight'], text='LIVE FLIGHT {0}'.format(result['id']))
            ]
            carousel_template.columns.append(column)
        elif result['type'] == 'schedule':
            column.title = 'FLIGHT: {0}'.format(result['label'])
            print('FLIGHT: {0}'.format(result['label']))
            flight_resp = flight_radar.get_flight(result['detail']['flight'])
            if flight_resp.status_code != 200:
                continue
            flight_data = flight_resp.json()['result']['response']['data'][0]
            departure_time = time.strftime('%H:%M', time.localtime(flight_data['time']['scheduled']['departure']))
            arrival_time = time.strftime('%H:%M', time.localtime(flight_data['time']['scheduled']['arrival']))
            flight_time = '{0}-{1}'.format(departure_time, arrival_time)
            default_aircraft = 'https://images.pexels.com/photos/62623/' \
                                             'wing-plane-flying-airplane-62623.jpeg?auto=compress&cs=tinysrgb' \
                                             '&dpr=2&h=750&w=960'
            if flight_resp.status_code == 200:
                aircraft_image = flight_resp.json()['result']['response']['aircraftImages']
                if aircraft_image is None:
                    column.thumbnail_image_url = default_aircraft
                else:
                    column.thumbnail_image_url = aircraft_image[0]['images']['medium'][0]['src']
            else:
                column.thumbnail_image_url = default_aircraft
            text = 'Flight Time: {0}\nRoute: {1} -> {2}'.format(flight_time, result['detail']['schd_from'],
                                                                       result['detail']['schd_to'])
            text = (text[:55] + '..') if len(text) > 55 else text
            column.text = text
            column.actions = [
                MessageAction(label=result['detail']['flight'], text='FLIGHT {0}'.format(result['detail']['flight']))
            ]
            carousel_template.columns.append(column)

    return carousel_template


def handle_live_flight(flight_id):
    response = flight_radar.get_live_flight(flight_id)
    json = response.json()
    flight_no = json['identification']['number']['default']
    lat = json['trail'][0]['lat']
    lng = json['trail'][0]['lng']
    reversed_result = gmaps.reverse_geocode((lat, lng))
    address = reversed_result[0]['formatted_address']
    address = str((address[:90] + '..') if len(address) > 90 else address)
    location_msg = LocationSendMessage(
        title=flight_no,
        address=address,
        latitude=lat,
        longitude=lng
    )
    return location_msg


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    print("text: {}".format(text))
    if isinstance(event.source, SourceUser):
        id = event.source.user_id
        rich_menu_list = line_bot_api.get_rich_menu_list()
        for rich_menu in rich_menu_list:
            line_bot_api.link_rich_menu_to_user(id, rich_menu.rich_menu_id)

    result = None
    flight_route_pattern = re.compile('^ROUTE ([A-Z]{3})-([A-Z]{3})$')
    flight_no_pattern = re.compile('^FLIGHT ([A-Z0-9]{3,})$')
    live_flight_pattern = re.compile('^LIVE FLIGHT ([A-Z0-9]{3,})$')
    airport_pattern = re.compile('^([A-Z]{3})$')
    airport_confirm_pattern = re.compile('^CONFIRM (:?YES|NO) AIRPORT (.*)$')
    search_pattern = re.compile('^FIND (.*)$')
    if text.upper() == "@BOT AIRPORT":
        result = "Please enter the airport IATA/ICAO code i.e. BKK, NRT, CNX"
    if text.upper() == "@BOT SEARCH":
        result = "Please enter search keyword for airport/flight/route with following pattern: \nfind bangkok" \
                 "\nfind tg123\nfind bkk-nrt"
    if airport_pattern.match(text.upper()):
        result = airport_pattern.match(text.upper())
        airport_code = result.group(1)
        result = airport.check_airport(airport_code)
    if airport_confirm_pattern.match(text.upper()):
        answer = airport_confirm_pattern.match(text.upper()).group(1)
        if answer.upper() == 'YES':
            airport_code = airport_confirm_pattern.match(text.upper()).group(2)
            result = airport.save_user_airport(db, id, airport_code)
    if live_flight_pattern.match(text.upper()):
        flight_id = live_flight_pattern.match(text.upper()).group(1)
        result = handle_live_flight(flight_id)
    if search_pattern.match(text.upper()):
        search_keyword = search_pattern.match(text.upper()).group(1)
        result = search(search_keyword)
    if 'departure' in text.lower():
        result = departures.create_departures_data('BKK')
    if 'arrival' in text.lower():
        result = arrivals.create_arrivals_data()
    if flight_route_pattern.match(text.upper()):
        result = flight_route_pattern.match(text.upper())
        origin = result.group(1)
        destination = result.group(2)
        result = flight_by_route.get_flight_by_route(origin, destination)
    if flight_no_pattern.match(text.upper()):
        result = flight_no_pattern.match(text.upper())
        result = flight_info.get_flight_info(result.group(1))

    if result is not None:
        if isinstance(result, BubbleContainer) or isinstance(result, CarouselContainer):
            message = FlexSendMessage(alt_text="Flex", contents=result)
            line_bot_api.reply_message(
                event.reply_token,
                message
            )
        if isinstance(result, ConfirmTemplate) or isinstance(result, CarouselTemplate):
            template_message = TemplateSendMessage('template message alt text', template=result)
            line_bot_api.reply_message(event.reply_token, template_message)
        if isinstance(result, LocationSendMessage):
            line_bot_api.reply_message(event.reply_token, result)
        if isinstance(result, str):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
