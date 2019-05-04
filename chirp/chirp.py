import flask
from flask_cors import CORS

# Create the flask app
app = Flask(__name__)
# Enable CORS
CORS(app)

def get_details_from_request(request_args):
    """
    This function parses the arguments from the GET requests
    """
    # collect phone number from request
    # collect topic from request
    return phone_number, topic

# API GET route for subscribing
@app.route("subscribe", methods=['GET'])
def subscribe_user():
    """
    This function subscribes a user to the appropriate topic
    """
    phone_number, topic = get_details_from_request(request_args)
    # subscribe the number to the appropriate topic using Twilio

# API GET rote for unsubscribing
@app.route("unsubscribe", methods=['GET'])
def unsubscribe_user():
    """
    This function unsubscribes a user from the appropriate topic
    """
    phone_number, topic = get_details_from_request(request_args)
    # unsubscribe the number to the appropriate topic using Twilio
