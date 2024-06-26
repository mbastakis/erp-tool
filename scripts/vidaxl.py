from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://transport.productsup.io/f500c29c85ad4b7d500c/channel/188081/vidaXL_gr_dropshipping.xml"
XML_ROOT = "product"
XML_CODE = "SKU"
XML_AVAILABILITY = "Stock"
XML_RETAIL = "retail_price_with_vat"
XML_WEBOFFER = "Webshop_price"

SUP_CODE = 2356
SUP_NAME = "VidaXL"
COMPANY = "900"


def convert_xml_availability_to_enum(availability):
    if availability == "0":
        return '4'
    return '3'


def create_sup_product_dict(availability, retail, weboffer):
    availability = convert_xml_availability_to_enum(availability.text)

    if weboffer is not None:
        weboffer = str(weboffer.text)
    else:
        weboffer = "0.0"
        availability = '4'

    return {
        "AVAILABILITY": availability,
        "RETAIL": weboffer,
        "DISCOUNT": "0.0"
    }


def create_hobbo_product_dict(product):
    return {
        "RETAIL": "{:.2f}".format(float(product['PRICER'])),
        "DISCOUNT": str(float(product['SODISCOUNT']))
    }
