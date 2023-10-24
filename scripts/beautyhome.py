from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://www.beautyhome.gr/products_list.xml"
XML_ROOT = "products/product"
XML_CODE = "Sku"
XML_AVAILABILITY = "StockStatus"
XML_RETAIL = "RegularPrice"
XML_WEBOFFER = "SalePrice"

SUP_CODE = 645
SUP_NAME = "BeautyHome"

COMPANY = "900"


# Logic
def convert_xml_availability_to_enum(availability):
    if (availability == 'instock'):
        return '2'
    elif (availability == 'outofstock'):
        return '4'
    return None


def create_sup_product_dict(availability, retail, weboffer):
    availability = convert_xml_availability_to_enum(availability.text)
    retail = str(retail.text)
    weboffer = str(weboffer.text)
    if weboffer == 'None':
        discount = '0.0'
    else:
        discount = str(round(100 - (float(weboffer) * 100 / float(retail)), 2))

    retail = "{:.2f}".format(float(retail))

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
