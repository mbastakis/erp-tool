from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://showood.gr/modules/skroutzxml/feed.xml"
XML_ROOT = "product"
XML_CODE = "id"
XML_AVAILABILITY = "availability"
XML_RETAIL = "price_with_vat"
XML_WEBOFFER = "not_used"

SUP_CODE = 1059
SUP_NAME = "Showood"
COMPANY = "900"


def convert_xml_availability_to_enum(availability):
    if (availability == 'Μη διαθέσιμο'):
        return '4'
    elif (availability == 'Άμεση παραλαβή / Παράδοση 1 έως 10 ημέρες'):
        return '2'


def create_sup_product_dict(availability, retail, weboffer):
    availability = convert_xml_availability_to_enum(availability.text)
    retail = "{:.2f}".format(float(str(retail.text)))
    discount = "0.0"

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
