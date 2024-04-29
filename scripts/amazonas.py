from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://aiora-amazonas.gr/modules/skroutz/xml-desc.php"
XML_ROOT = "product"
XML_CODE = "mpn"
XML_AVAILABILITY = "InStock"
XML_RETAIL = "price"
XML_WEBOFFER = "none"

SUP_CODE = 2526
SUP_NAME = "Amazonas"
COMPANY = "900"


def convert_xml_availability_to_enum(availability):
    if availability == "Y":
        return '2'
    elif availability == "N":
        return '4'
    else:
        Logger.error("Unknown availability: " + availability)
        exit(-1)


def create_sup_product_dict(availability, retail, weboffer):
    availability = convert_xml_availability_to_enum(availability.text)
    retail = str(retail.text)   
    discount = '0.0'

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
