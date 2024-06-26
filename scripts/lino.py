from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://www.linohome.gr/wp-load.php?security_token=xml"
XML_ROOT = "item"
XML_CODE = "mpn"
XML_AVAILABILITY = "stock_status"
XML_RETAIL = "regular_price_with_vat"
XML_WEBOFFER = "sale_price_with_vat"

SUP_CODE = 47
SUP_NAME = "Lino"
COMPANY = "900"


# Logic
def convert_xml_availability_to_enum(availability):
    if (availability == 'instock'):
        return '2'
    elif (availability == 'outofstock'):
        return '4'


def create_sup_product_dict(availability, retail, weboffer):
    availability = convert_xml_availability_to_enum(availability.text)
    retail = str(retail.text)
    weboffer = str(weboffer.text)

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
