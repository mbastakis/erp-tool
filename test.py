import requests
import json

# Constants
BASE_URL = 'http://hobbo.oncloud.gr/s1services'
USERNAME = 'hobboweb'
PASSWORD = 'Ab12345!'
APP_ID = '1000'


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
            resp_obj = response_data['objs'][0]

            company = resp_obj['COMPANY']
            branch = resp_obj['BRANCH']
            module = resp_obj['MODULE']
            ref_id = resp_obj['REFID']

            return {
                "client_id": client_id,
                "company": company,
                "branch": branch,
                "module": module,
                "ref_id": ref_id
            }
        else:
            print("Login failed!")
            print(response.content)
            return None
    else:
        print(response.content)
        print("Error:", response.status_code)
        return None


def authenticate(client_id, company, branch, module, ref_id):
    # Define the request payload
    payload = {
        "service": "authenticate",
        "clientID": client_id,
        "COMPANY": company,
        "BRANCH": branch,
        "MODULE": module,
        "REFID": ref_id
    }

    # Making the request
    response = requests.post(BASE_URL, json=payload)

    # Check the response
    if response.status_code == 200:
        response_data = response.json()
        if response_data['success']:
            print("Authentication successful!")
            return response_data
        else:
            print("Authentication failed!")
            print(response.content)
            return False
    else:
        print(response.content)
        print("Error:", response.status_code)
        return False


if __name__ == "__main__":
    login_resp = login_to_erp()
    if login_resp == None:
        print("Could not retrieve clientID.")
        exit(-1)

    auth_resp = authenticate(
        login_resp['client_id'],
        login_resp['company'],
        login_resp['branch'],
        login_resp['module'],
        login_resp['ref_id']
    )
    if auth_resp == False:
        print("Authentication failed!")
        exit(-1)

    login_resp['client_id'] = auth_resp['clientID']

    # # get objects
    # payload = {
    #     "service": "getObjects",
    #     "clientID": login_resp['client_id'],
    #     "appId": APP_ID
    # }

    # response = requests.get(BASE_URL, json=payload)
    # print(response.content)

    # # get object item tables
    # payload = {
    #     "service": "getObjectTables",
    #     "clientID": login_resp['client_id'],
    #     "appId": APP_ID,
    #     "OBJECT": "ITEM.MTRSUPCODE"
    # }
    # response = requests.get(BASE_URL, json=payload)
    # print(response.content)

    # # get object item fields
    # payload = {
    #     "service": "getTableFields",
    #     "clientID": login_resp['client_id'],
    #     "appId": APP_ID,
    #     "OBJECT": "ITEM",
    #     "TABLE": "ITEM"
    # }
    # response = requests.get(BASE_URL, json=payload)
    # print(response.content)

    # # get selector fields
    # payload = {
    #     "service": "selectorFields",
    #     "clientID": login_resp['client_id'],
    #     "appId": APP_ID,
    #     "TABLENAME": "MTRL",
    #     "KEYNAME": "MTRSUP",
    #     "KEYVALUE": "000044",
    #     "RESULTFIELDS": "CODE,NAME,CODE1"
    # }
    # response = requests.get(BASE_URL, json=payload)
    # print(response.content)

    # get data
    payload = {
        "service": "getData",
        "clientID": login_resp['client_id'],
        "appId": APP_ID,
        "OBJECT": "ITEM",
        "FORM": "",

    }
    response = requests.get(BASE_URL, json=payload)
    print(response.content)

    # # get selector data
    # payload = {
    #     "service": "getSelectorData",
    #     "clientID": login_resp['client_id'],
    #     "appId": APP_ID,
    #     "EDITOR": "1|TRDR|TRDR|SODTYPE=13 AND ISPROSP='0'|"
    # }
    # response = requests.get(BASE_URL, json=payload)
    # print(response.content)
