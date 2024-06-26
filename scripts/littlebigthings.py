from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://www.littlebigthings.gr/feed/lbt-b2b.xml"
XML_ROOT = "item"
XML_CODE = "model"
XML_AVAILABILITY = "quantity"
XML_RETAIL = "price"
XML_WEBOFFER = "sale_price"

SUP_CODE = 898
SUP_NAME = "LittleBigThings"
COMPANY = "900"


def convert_xml_availability_to_enum(availability):
    if availability == '0':
        return '4'
    else:
        return '2'


def create_sup_product_dict(availability, retail, weboffer):
    availability = convert_xml_availability_to_enum(availability.text)
    retail = str(retail.text)
    weboffer = str(weboffer.text)
    if weboffer == 'None':
        discount = '0.0'
    else:
        discount = str(round(100 - (float(weboffer) * 100 / float(retail)), 2))

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
