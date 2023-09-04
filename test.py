import requests
import json

# Constants
BASE_URL = 'http://hobbo.oncloud.gr/s1services'
USERNAME = 'hobboweb'
PASSWORD = 'Ab12345!'
APP_ID = '1001'

def login_to_erp():
    # Define the request payload
    payload = {
        "service": "login",
        "username": USERNAME,
        "password": PASSWORD,
        "appId": APP_ID
    }
    
    # Making the request
    response = requests.post(BASE_URL, json=payload)
    
    # Check the response
    if response.status_code == 200:
        response_data = response.json()
        if response_data['success']:
            print("Login successful!")
            client_id = response_data['clientID']
            return client_id
        else:
            print("Login failed!")
            print(response.content)
            return None
    else:
        print(response.content)
        print("Error:", response.status_code)
        return None

# Test
client_id = login_to_erp()
if client_id:
    print("Retrieved clientID:", client_id)
else:
    print("Could not retrieve clientID.")
