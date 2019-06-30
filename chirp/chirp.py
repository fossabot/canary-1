from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
import hashlib
import os

globals = {}
globals['bucket_name'] = "airpollutionsubscribers"

# Create the flask app
app = Flask(__name__)
# Enable CORS
CORS(app)

# Pass in the access credentials via environment variables
AWS_SERVER_PUBLIC_KEY = os.getenv("AWS_SERVER_PUBLIC_KEY", None)
AWS_SERVER_SECRET_KEY = os.getenv("AWS_SERVER_SECRET_KEY", None)

# Check if the environment variables exist, they are only required for external access
if AWS_SERVER_PUBLIC_KEY is not None and AWS_SERVER_SECRET_KEY is not None:

    session = boto3.Session(
        aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=AWS_SERVER_SECRET_KEY,
        region_name='eu-west-2'
    )

    globals['s3'] = session.resource('s3')

# If no environment variables rely on a AWS role instead
else:
    globals['s3'] = boto3.resource('s3')


def get_details_from_request(request_body):
    """
    This function parses the arguments from the GET requests
    """
    phone_number = request_body['phone']
    topic = request_body['topic']
    return phone_number, topic

def save_user_to_s3(s3, bucket_name, json_payload):
    phone_hash = hashlib.md5(json_payload['phone'].encode('utf-8'))
    s3.Object(bucket_name, 'subscriber-{}.json'.format(
        phone_hash.hexdigest())).put(Body=json.dumps(json_payload))

def remove_user_from_s3(s3, bucket_name, phone):
    phone_hash = hashlib.md5(json_payload['phone'].encode('utf-8'))
    s3.Object(bucket_name, 'subscriber-{}.json'.format(
        phone_hash.hexdigest())).delete()

# API GET route for subscribing
@app.route("/subscribe", methods=['POST'])
def subscribe_user():
    """
    This function subscribes a user to the appropriate topic
    """
    phone_number, topic = get_details_from_request(request.form)
    json_payload = {
        "phone": phone_number,
        "topic": topic
    }
    save_user_to_s3(
        s3=globals['s3'],
        bucket_name=globals['bucket_name'],
        json_payload=json_payload)

    resp = jsonify(success=True)
    resp.status_code = 200
    return resp
    # subscribe the number to the appropriate topic using Twilio


# API GET rote for unsubscribing
@app.route("/unsubscribe", methods=['POST'])
def unsubscribe_user():
    """
    This function unsubscribes a user from the appropriate topic
    """
    phone_number, topic = get_details_from_request(request.form)
    remove_user_from_s3(
        s3=globals['s3'],
        bucket_name=globals['bucket_name'],
        phone=phone_number)

    resp = jsonify(success=True)
    resp.status_code = 200
    return resp
    # unsubscribe the number to the appropriate topic using Twilio
