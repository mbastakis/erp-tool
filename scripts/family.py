from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl
from utilities import str_to_int

import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://malamashop.gr/wp-content/uploads/rex-feed/feed-200541.xml"
XML_ROOT = "product"
XML_CODE = "ean"
XML_AVAILABILITY = "availability"
XML_RETAIL = "price"
XML_WEBOFFER = "SalePrice"

SUP_CODE = 668
SUP_NAME = "Family"
COMPANY = "900"


# Logic
def convert_xml_availability_to_enum(availability):
    if (availability == 'in_stock'):
        return '2'
    else:
        return '4'


def create_sup_product_dict(availability, retail, weboffer):
    availability = convert_xml_availability_to_enum(availability.text)
    retail = "{:.2f}".format(str_to_int(retail.text))
    weboffer = str(str_to_int(weboffer.text))
    if weboffer == '0':
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
