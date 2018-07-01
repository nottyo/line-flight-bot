import os
import re
import sys

from flask import Flask, request
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, BubbleContainer, FlexSendMessage, TextSendMessage, CarouselContainer
)

from arrivals import Arrivals
from departures import Departures
from flight_by_route import FlightByRoute
from flight_info import FlightInfo

app = Flask(__name__)

channel_access_token = os.getenv("CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("CHANNEL_SECRET")
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

departures = Departures()
arrivals = Arrivals()
flight_by_route = FlightByRoute()
flight_info = FlightInfo()


@app.route("/")
def main_route():
    return "Hello World!"


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


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    result = None
    print("text: {}".format(text))
    flight_route_pattern = re.compile('^ROUTE ([A-Z]{3})-([A-Z]{3})$')
    flight_no_pattern = re.compile('^FLIGHT ([A-Z0-9]{3,})$')
    if 'departure' in text.lower():
        result = departures.create_departures_data()
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
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
