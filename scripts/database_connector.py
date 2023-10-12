import json
import requests
import time
import utilities as utils

# Constants
BASE_URL = 'http://hobbo.oncloud.gr/s1services'
USERNAME = 'hobboweb'
PASSWORD = 'Ab12345!'
APP_ID = '1000'
COMPANY = 900


class DatabaseConnector:
    def __init__(self, url=BASE_URL, username=USERNAME, password=PASSWORD, app_id=APP_ID, company=COMPANY):
        self.url = url
        self.username = username
        self.password = password
        self.app_id = app_id
        self.company = COMPANY
        self.client_id = None

    def login(self):
        # Define the request payload
        payload = {
            "service": "login",
            "username": self.username,
            "password": self.password,
            "appId": self.app_id
        }

        # Making the request
        response = requests.post(self.url, json=payload)

        # Check the response
        if response.status_code == 200:
            response_data = response.json()
            if response_data['success']:
                client_id = response_data['clientID']
                resp_obj = response_data['objs'][0]

                company = resp_obj['COMPANY']
                branch = resp_obj['BRANCH']
                module = resp_obj['MODULE']
                ref_id = resp_obj['REFID']

                self.client_id = client_id
                self.company = company
                self.branch = branch
                self.module = module
                self.ref_id = ref_id

                return True
            else:
                return False
        else:
            return False

    def authenticate(self):
        # Define the request payload
        payload = {
            "service": "authenticate",
            "clientID": self.client_id,
            "COMPANY": self.company,
            "BRANCH": self.branch,
            "MODULE": self.module,
            "REFID": self.ref_id
        }

        # Making the request
        response = requests.post(self.url, json=payload)

        # Check the response
        if response.status_code == 200:
            response_data = response.json()
            if response_data['success']:
                self.client_id = response_data['clientID']
                return True
            else:
                return False
        else:
            return False

    def get_products(self, supplier_code):
        payload = {
            "service": "selectorFields",
            "clientID": self.client_id,
            "appId": self.app_id,
            "TABLENAME": "ITEM",
            "KEYNAME": "MTRSUP",
            "KEYVALUE": supplier_code,
            "RESULTFIELDS": "CODE,CODE1,PRICER,SODISCOUNT,MTRL,ISACTIVE"
        }
        response = requests.post(self.url, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            if response_data['success']:
                excluded_codes = utils.get_excluded_codes()
                result = {
                    d['CODE1']: {k: v for k, v in d.items() if k != 'CODE1'}
                    for d in response_data['rows'] if 'CODE1' in d and d['CODE'] not in excluded_codes
                }
                return result
            else:
                return False
        else:
            return False

    def update_products(self, updated_products):
        MAX_RETRIES = 5  # Set the max number of retries
        RETRY_WAIT = 5   # Time (in seconds) to wait between retries

        for product in updated_products:
            payload = {
                "service": "setData",
                "clientID": self.client_id,
                "appId": self.app_id,
                "object": "ITEM",
                "key": product['KEY'],
                "data": {
                    "ITEM": {
                        "PRICER": product['PRICE'],
                        "SODISCOUNT": product['DISCOUNT'],
                        "ISACTIVE": product['ISACTIVE'],
                    },
                    "ITEEXTRA": {
                        "UTBL04": product['STOCK'],
                        "BOOL01": product['WEBACTIVE']
                    }
                }
            }

            retries = 0
            while retries <= MAX_RETRIES:
                response = requests.post(self.url, json=payload)
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data['success']:
                        break  # exit the while loop, move on to the next product
                    else:
                        retries += 1
                        print(
                            f"Failed to update product {product['KEY']}. Retry #{retries}")
                        time.sleep(RETRY_WAIT)
                else:
                    retries += 1
                    print(
                        f"Failed to update product {product['KEY']} with status code {response.status_code}. Retry #{retries}")
                    time.sleep(RETRY_WAIT)

            # Check if we exited the loop due to max retries
            if retries > MAX_RETRIES:
                print(
                    f"Failed to update product {product['KEY']} after {MAX_RETRIES} retries.")
                return False

        return True

    def get_product_extras(self, COMPANY_VALUE):
        payload = {
            "service": "selectorFields",
            "clientID": self.client_id,
            "appId": self.app_id,
            "TABLENAME": "ITEEXTRA",
            "KEYNAME": "COMPANY",
            "KEYVALUE": COMPANY_VALUE,
            "RESULTFIELDS": "MTRL,UTBL04,BOOL01"
        }
        response = requests.post(self.url, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            if response_data['success']:
                result = {item['MTRL']: {'UTBL04': item.get(
                    'UTBL04', None), 'BOOL01': item.get('BOOL01', None)} for item in response_data['rows']}
                return result
            else:
                return False
        else:
            return False

    def get_product_quantity(self):
        payload = {
            "service": "selectorFields",
            "clientID": self.client_id,
            "appId": self.app_id,
            "TABLENAME": "ITEMTRDATA",
            "KEYNAME": "COMPANY",
            "KEYVALUE": 900,
            "RESULTFIELDS": "MTRL, QTY1"
        }
        response = requests.post(self.url, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            if response_data['success']:
                result_dict = {item['MTRL']: item['QTY1']
                               for item in response_data['rows']}
                return result_dict
            else:
                return False
        else:
            return False
