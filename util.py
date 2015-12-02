#!/usr/bin/env python

import os
import requests
import random
import glob
from rauth import OAuth2Service
from twilio.rest import TwilioRestClient 
from secret import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, HUEBER_CLIENT_ID, HUEBER_CLIENT_SECRET

def text_image(phone_number, passenger_name, img_url):
    client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) 

    client.messages.create(
        to=phone_number, 
        from_="+18085183338", 
        body="Your Uber passenger, {0}, will flag you with this image on their phone."\
             .format(passenger_name),
        media_url=img_url, 
    )

def get_uber_login_url():
    uber_api = OAuth2Service(\
        client_id=HUEBER_CLIENT_ID,\
        client_secret=HUEBER_CLIENT_SECRET,\
        name='hueber',\
        authorize_url='https://login.uber.com/oauth/authorize',\
        access_token_url='https://login.uber.com/oauth/token',\
        base_url='https://api.uber.com/v1/',
    )

    parameters = {
        'response_type': 'code',
        'redirect_uri': 'https://hueber.io/auth',
        'scope': 'profile request',
    }

    # Redirect user here to authorize your application
    login_url = uber_api.get_authorize_url(**parameters)
    return login_url

def get_user_name(access_token):
    url = 'https://api.uber.com/v1/me'

    response = requests.get(
            url,
            headers = {
                'Authorization': 'Bearer %s' % access_token
                }
            )

    data = response.json()
    first_name = data['first_name']
    last_name = data['last_name']
    full_name = first_name + ' ' + last_name
    return data['first_name']

def make_fake_ride_request(access_token):
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Content-Type': 'application/json'
    }

    url = 'https://sandbox-api.uber.com/v1/requests'

    parameters = {
        'product_id': 'd4abaae7-f4d6-4152-91cc-77523e8165a4',
        'start_latitude': 37.99,
        'end_latitude': 37.78,
        'start_longitude': -122.42,
        'end_longitude': -122.42,
    }

    response = requests.post(url, json=parameters, headers=headers)
    data = response.json()
    status_code = response.status_code
    request_id = data['request_id']
    ride_status = data['status']
    print("Request id is {0}".format(request_id))
    print("Status is {0}".format(ride_status))
    print("Status code was {0}".format(status_code))
    print("*****************************")

    return request_id

def cancel_ride(access_token, request_id):
    """Cancel ride for given request_id, return cancel response status code"""
    headers = {
            'Authorization': 'Bearer %s' % access_token,
            'Content-Type': 'application/json'
    }
    url = 'https://sandbox-api.uber.com/v1/requests/' + request_id
    cancel_response = requests.delete(url, headers=headers)
    return cancel_response.status_code

def change_ride_status(access_token, request_id, status):
    # pretend like the ride request got accepted
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Content-Type': 'application/json'
    }
    url = 'https://sandbox-api.uber.com/v1/sandbox/requests/' + request_id
    parameters = {"status": status}
    update_response = requests.put(url, json=parameters, headers=headers)

def get_ride_info(access_token, request_id):
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Content-Type': 'application/json'
    }

    url = 'https://sandbox-api.uber.com/v1/requests/' + request_id
    info_response = requests.get(url, headers=headers)
    driver_data = info_response.json()

    return driver_data

def get_random_image_path():
    images = glob.glob('site/flags/*.png')
    return os.path.basename(random.choice(images))

def get_available_products(access_token, lat=37.99, lon=-122.42):
    url = 'https://sandbox-api.uber.com/v1/products'
    parameters = {
        'latitude': lat,
        'longitude': lon,
    }
    headers = {
        'Authorization': 'Bearer %s' % access_token,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, params=parameters, headers=headers)
    data = response.json()
    result = []
    for product in data['products']:
        result.append(product['product_id'])
    return result
