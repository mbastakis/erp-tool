from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://ws.artelibre.gr/feeds/61600dbBxsTcGXvxOMJ7ZKrqZ5I9HWV3zS3pPzQrH/1"
XML_ROOT = "Product"
XML_CODE = "sku"
XML_AVAILABILITY = "inventory"
XML_RETAIL = "not_used"
XML_WEBOFFER = "eshop_price"

SUP_CODE = 806
SUP_NAME = "Artelibre"
COMPANY = "900"


# Logic
def convert_xml_availability_to_enum(availability):
    if availability == "0":
        return '4'
    else:
        return '2'


def get_retail_price(final_price: float, discount_percentage: float) -> float:
    if discount_percentage >= 1 or discount_percentage < 0:
        raise ValueError(
            "Discount percentage should be between 0 and 1 (exclusive).")

    starting_price = final_price / (1 - discount_percentage)
    return starting_price


def create_sup_product_dict(availability, retail, weboffer):
    availability = convert_xml_availability_to_enum(availability.text)
    weboffer = str(weboffer.text)
    retail = "{:.2f}".format(get_retail_price(float(weboffer), 0.4))

    discount = '40.0'

    return {
        "AVAILABILITY": availability,
        "RETAIL": retail,
        "DISCOUNT": discount
    }


def create_hobbo_product_dict(product):
    return {
        "RETAIL": "{:.2f}".format(float(product['PRICER'])),
        "DISCOUNT": str(float(product['SODISCOUNT']))
    }
