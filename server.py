import requests

import socket, os
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import ssl

from util import text_image, get_random_image_path, get_user_name,\
                 make_fake_ride_request, get_ride_info, change_ride_status
from pages import success_page
from secret import HUEBER_AUTH

CERTIFICATE_PATH = os.getcwd() + '/hueber.crt'
KEY_PATH = os.getcwd() + '/hueber.key'

def get_auth_token(auth_code):
    parameters = {
        'redirect_uri': 'https://hueber.io/auth',
        'code': auth_code,
        'grant_type': 'authorization_code',
    }

    response = requests.post('https://login.uber.com/oauth/token', auth=HUEBER_AUTH, data=parameters)

    # This access_token is what we'll use to make requests in the following steps
    access_token = response.json().get('access_token')
    return access_token

class HueberRequestHandler(BaseHTTPRequestHandler):
    def handle_auth(self, attr):
        access_token = get_auth_token(attr['code'])
        print("Got access token: "+access_token)

        # Redirect to main hueber
        self.send_response(301)
        self.send_header("Location", "https://hueber.io/app?access_token="+access_token)
        self.end_headers()

    def handle_app(self, attr):
        # Get access token
        access_token = attr['access_token']

        # Pick random image
        random_image = get_random_image_path()

        # NOTE: This assumes the user has already made a ride request
        request_id = make_fake_ride_request(access_token)
        ride_info = get_ride_info(access_token, request_id)
        driver = ride_info.get('driver')
        
        if driver == None:
            # Send failure page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes("You don't have an accepted ride request! Make one and try again", 'UTF-8'))
            return

        driver_name = driver['name']
        driver_phone = driver['phone_number']

        passenger_name = get_user_name(access_token)
        
        # Generate app page with image
        app_page = success_page('flags/'+random_image, driver_name, passenger_name)

        # Send flag image to driver
        text_image(driver_phone, passenger_name, 'https://hueber.io/flags/'+random_image)

        # Send app page
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(app_page, 'UTF-8'))

    def handle_head(self):
        try:
            main_page = open('site/index.html', 'r').read()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(main_page, 'UTF-8'))
        except IOError:
            self.send_error(404, 'derp')

    def do_GET(self):
        path_split = self.path.split('?')
        path = path_split[0].strip('/')

        # Get attributes from URL path
        attr = {}
        if len(path_split) > 1:
            attr_split = path_split[1].split('&')
            for a in path_split:
                a_split = a.split('=')
                if len(a_split) < 2:
                    continue
                key, value = a_split
                attr[key] = value

        # Check for requested file
        content_type = 'text/html'
        extension = path.split('.')[-1]
        read_mode = 'r'
        if extension == 'css':
            content_type = 'text/css'
            read_mode = 'r'
        elif extension == 'png':
            content_type = 'image/png'
            read_mode = 'rb'
        elif extension == 'jpeg' or extension == 'jpg':
            content_type = 'image/jpeg'
            read_mode = 'rb'
        elif extension == 'mp4':
            content_type = 'video/mp4'
            read_mode = 'rb'

        req_file = None
        try:
            with open('site/'+path, read_mode) as f:
                req_file = f.read()
        except:
            pass

        # Handle the request based on the path
        if req_file != None:
            if content_type.split('/')[0] == 'text':
                content = bytes(req_file, 'UTF-8')
            else:
                content = req_file
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        elif path == "":
            self.handle_head()
        elif path == "auth":
            self.handle_auth(attr)
        elif path == "app":
            self.handle_app(attr)
        else:
            self.send_error(404, 'derp')

def main():
    httpd = HTTPServer(('0.0.0.0', 443), HueberRequestHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=CERTIFICATE_PATH, keyfile=KEY_PATH, server_side=True)
    print("Serving hueber server...")
    httpd.serve_forever()

####################################################################################################

if __name__ == '__main__':
    main()
