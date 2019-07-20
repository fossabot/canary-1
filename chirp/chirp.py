from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
import hashlib
import os
from twilio.rest import Client
from random import randint
import datetime
import pytz

globals = {}
# Amazon Web Services bucket name to hold the subsciber information
globals['bucket_name'] = "airpollutionsubscribers"
# Get the Twilio account id and authorisation token
globals['twilio_account_sid'] = os.getenv("TWILIO_ACCOUNT_ID", None)
globals['twilio_auth_token'] = os.getenv("TWILIO_AUTH_TOKEN", None)
# Temporay storage for the verification codes
globals['verification_codes'] = {}

# Create the twilio client
twilio_client = Client(
    globals['twilio_account_sid'],
    globals['twilio_auth_token'])

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


def get_details_from_request(request_body, parameters):
    """
    This function parses the arguments from the body of the POST requests making
    sure that the correct parameters are there

    param: (???) request_body: The body of the request
    parameters: (list[str]) parameters: The parameters to check for and extract
    from the request

    returns: (dict) request: The request dictionary with a status code describing
    if the parameters were found and the parameters themselves if they exist
    """

    # Initialise a dictionary to hold the parameters and status code
    request = {}

    # Check that all the parameters exist in the request body
    if not all(parameter in request_body.keys() for parameter in parameters):
        # If not return the request dictionary with a 400 status code to propogate in the response
        request['status_code'] = 400
        return request

    # Given that the parameters exist add each of them to the request dictionary
    for parameter in parameters:
        request[parameter] = request_body[parameter]

    # Set the status code from this operation to be 200
    request['status_code'] = 200

    # Return the request dictionary
    return request


def hash_phone_number(phone_number):
    """
    This function creates an md5 hash of a phone number

    param: (str) phone_number: The phone number to create an MD5 hash of

    returns: (str) phone_hash: The MD5 hash of the phone number
    """

    # Create a hash from the phone number
    phone_hash = hashlib.md5(phone_number.encode('utf-8')).hexdigest()
    return phone_hash


def save_user_to_s3(s3, bucket_name, json_payload):
    """
    This function creates a json file for a subscriber and stores it in an S3
    bucket so that it can be queried by Amazon Athena

    param: (boto3.resource) s3: The boto3 S3 resource to use for interacting
    with Amazon S3
    param: (str) bucket_name: The bucket name in S3 to store the user information
    param: (dict) json_payload: The json payload to store in the json file

    return: (dict) save_status: Holds details about the status of saving the user info
    """

    save_status = {}
    # Create a hash of the subscriber's phone number to use in the file name
    phone_hash = hash_phone_number(json_payload['phone'])
    # Create and store the file in S3
    try:
        s3.Object(bucket_name, 'subscriber-{}.json'.format(
            phone_hash)).put(Body=json.dumps(json_payload))
    except:
        save_status['success'] = False
        save_status['message'] = 'The saving of the user failed due to an unknown error'
        return save_status

    save_status['success'] = True
    save_status['message'] = 'The subscriber has been saved succesfully'
    return save_status


def remove_user_from_s3(s3, bucket_name, phone):
    """
    This function deletes a json file for a subscriber which is stored in S3

    param: (boto3.resource) s3: The boto3 S3 resource to use for interacting
    with Amazon S3
    param: (str) bucket_name: The bucket name in S3 to store the user information
    param: (str) phone: The phone number of the subscriber whos information should
    be deleted
    """

    phone_hash = hash_phone_number(json_payload['phone'])

    s3.Object(bucket_name, 'subscriber-{}.json'.format(
        phone_hash)).delete()


def issue_verification_code(client, phone_number, sub_type, level=None):
    """
    This issues a verification code for a user who is attempting to subscribe.
    They must enter this code into the web application to prove that they have
    ownership of the phone number that they are subscribing

    param: (Twilio Client) client: The Twilio client to use
    param: (str) phone_number: The phone number of the potential subscriber
    param: (str) sub_type: Whether the user is 'Subscribing' or 'Unsubscribing'
    param: (str) level: The level of alerts that the user is subcribing to if this
    is for a subscription request

    return: (dict) code_status: The status of the code verification result and the code
    if it was successful
    """

    code_status = {}

    # Ensure that the subscription type is one of the allowed values
    if sub_type not in ['Subscribe', 'Unsubscribe']:
        code_status['success'] = False
        code_status['message'] = 'The subscription type of {} is not supported'.format(sub_type)
        return code_status

    # Generate a random 6 digit code for the user to use
    code = str(randint(100000,999999))

    # Generate an appropriate message if the user is subscribing
    if sub_type == 'Subscribe':
        message_body = "To complete your subscription to Chirping Canary for {} alerts your verification code is {}".format(
            level, code
        )

    # Generate an appropriate message if the user is unsubscribing
    elif sub_type == 'Unsubscribe':
        message_body = "To unsubscribe from Chirping Canary {} alerts your verification code is {}".format(
            level, code
        )

    # Attempt to send a message to the user with the verification code
    try:
        message_result = client.messages.create(
            from_='+442033225373',
            body=message_body,
            to=phone_number
        )
    except:
        code_status['success'] = False
        code_status['message'] = 'The verification code message failed to send due to an unknown error'
        return code_status

    code_status['success'] = True
    code_status['message'] = 'The message was succesfully sent'
    code_status['code'] = code

    return code_status


def send_subscription_confirmation(client, phone_number, level):
    """
    This sends a success message to a successful subscriber

    param: (Twilio Client) client: The Twilio client to use
    param: (str) phone_number: The phone number of the new subscriber
    param: (str) level: The alert level that the subscriber has subscribed to

    returns: (dict) confirmation_status: Details around the success of the confirmation message
    """

    confirmation_status = {}

    message_body = "Congratulations, you are now subscribed to {} alerts from Chirping Canary".format(level)

    try:
        message = client.messages.create(
            from_='+442033225373',
            body=message_body,
            to=phone_number
        )
    except:
        confirmation_status['success'] = False
        confirmation_status['message'] = 'The verification code message failed to send due to an unknown error'
        return confirmation_status

    confirmation_status['success'] = True
    confirmation_status['message'] = 'The confirmation message was successfully sent'
    return confirmation_status


def verify_phone_number(phone_number):
    """
    This verifies that a phone number has the right format. It does not guarantee
    that it is a legitimate phone number.
    """
    return True


def verify_code(phone_number_hash, code, max_attempts, max_elapsed_time):
    """
    This verifies that a user has ownership of the phone number that they are registering

    param: (str) phone_number: The phone number of the new subscriber
    param: (str) code: The code that they entered

    returns: (dict) verification_status: Details about the verification
    """

    verification_status = {}

    # Check that the user has been sent a verification code
    for key in globals['verification_codes'].keys():
        print (key)

    print (phone_number_hash)

    if phone_number_hash not in globals['verification_codes'].keys():
        verification_status['success'] = False
        verification_status['message'] = "No record of sending a verification code to this user"
        return verification_status

    # Get the details from the dictionary
    verify_code = globals['verification_codes'][phone_number_hash]['verify_code']
    verification_datetime = globals['verification_codes'][phone_number_hash]['verification_datetime']
    number_attempts = globals['verification_codes'][phone_number_hash]['attempts']

    # Increment the number of attempts that this user has made to verify their subscription
    globals['verification_codes'][phone_number_hash]['attempts'] += 1

    # Check that the user hasn't exceeded the allowed number of attempts
    if number_attempts >= max_attempts:
         verification_status['success'] = False
         verification_status['message'] = "You have made {} unsuccesful attempts to verify your subscription, you will need to wait and try again in an hour".format(
            number_attempts
         )
         return verification_status

    # Check that it hasn't been more than 10 minutes since getting the code
    now = datetime.datetime.now(pytz.UTC)
    time_elapsed = (now - verification_datetime).seconds // 60 % 60
    if time_elapsed >= 10:
        verification_status['success'] = False
        verification_status['message'] = "It has been more than 10 minutes since the code was issued, please try re-subscribing"
        return verification_status

    # Check that the codes aren't different
    if str(code) != verify_code:
        verification_status['success'] = False
        verification_status['message'] = "The verification code you entered does not match, please check carefully and try again"
        return verification_status

    # Return a success
    verification_status['success'] = True
    verification_status['message'] = "Verification successful with {} attempts and {} minutes elapsed".format(number_attempts, time_elapsed)

    return verification_status


# API POST route for subscribing
@app.route("/subscribe", methods=['POST'])
def subscribe_user():
    """
    This function subscribes a user to the appropriate topic
    """
    # The parameters required from the POST request
    parameters = ["phone", "topic"]
    # Get the details from the POST request assuming that they exist
    request_params = get_details_from_request(request.form, parameters)

    # If the parameters didn't exist return a bad request code
    if request_params["status_code"] != 200:
        resp = jsonify(success=False, message="Incorrect parameters in request")
        resp.status_code = request_params["status_code"]
        return resp

    # Pull off the parameters
    phone = request_params["phone"]
    topic = request_params["topic"]

    # Verify that the phone number has the correct format
    if not verify_phone_number(phone):
        resp = jsonify(success=False, message="The phone number does not have a valid UK mobile number format")
        resp.status_code = 400
        return resp

    # If so, issue a verification code
    verify_code = issue_verification_code(
        client=twilio_client,
        phone_number=request_params["phone"],
        sub_type="Subscribe",
        level=topic
    )

    # If there were any issues sending the verification code
    if not verify_code["success"]:
        resp = jsonify(success=False, message=verify_code["message"])
        resp.status_code = 400
        return resp

    # Hash the phone number for use as a key in a dictionary to temporarily hold the code and level
    phone_hash = hash_phone_number(phone)

    # Save the details to the global dictionary for use in verification confirmation
    globals['verification_codes'][phone_hash] = {
        "verify_code": verify_code['code'],
        "verification_datetime": datetime.datetime.now(pytz.UTC),
        "attempts": 0,
        "level": topic
    }

    resp = jsonify(success=True)
    resp.status_code = 200
    return resp


# API POST route for confirming a subscription
@app.route("/subscribe/verify", methods=['POST'])
def confirm_subscription():
    """
    This function subscribes a user to the appropriate topic
    """

    parameters = ["phone", "code"]
    request_params= get_details_from_request(request.form, parameters)

    if request_params["status_code"] != 200:
        resp = jsonify(success=False, message="The parameters were incorrect")
        resp.status_code = request_params["status_code"]
        return resp

    phone = request_params["phone"]
    code = request_params["code"]

    phone_hash = hash_phone_number(phone)

    verification = verify_code(
        phone_number_hash=phone_hash,
        code=code,
        max_attempts=3,
        max_elapsed_time=10)

    if not verification["success"]:
        resp = jsonify(success=False, message=verification['message'])
        resp.status_code = 400
        return resp

    level = globals['verification_codes'][phone_hash]['level']

    save_user_payload = {
        "phone": phone,
        "topic": level
    }

    save_status = save_user_to_s3(
        s3=globals['s3'],
        bucket_name=globals['bucket_name'],
        json_payload=save_user_payload)

    if not save_status["success"]:
        resp = jsonify(success=False, message=save_status['message'])
        resp.status_code = 400
        return resp

    confirmation_status = send_subscription_confirmation(twilio_client, phone, level)

    if not confirmation_status['success']:
        resp = jsonify(success=False, message=confirmation_status['message'])
        resp.status_code = 400
        return resp

    del globals['verification_codes'][phone_hash]

    resp = jsonify(success=True)
    resp.status_code = 200
    return resp


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
