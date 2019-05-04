"""
This file handles topic subscription
"""

import flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_details_from_request(request_args):
    # collect phone number from request
    # collect topic from request
    return phone_number, topic

# API GET route for subscribing
@app.route("subscribe", methods=['GET'])
def subscribe_user():
    phone_number, topic = get_details_from_request(request_args)
    # subscribe the number to the appropriate topic using Twilio

# API GET rote for unsubscribing
@app.route("unsubscribe", methods=['GET'])
def unsubscribe_user():
    phone_number, topic = get_details_from_request(request_args)
    # unsubscribe the number to the appropriate topic using Twilio
