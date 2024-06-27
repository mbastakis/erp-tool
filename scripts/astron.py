from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://www.astron-home.gr/wp-load.php?security_token=367782cc2dd25e50&export_id=10&action=get_data"
XML_ROOT = "product"
XML_CODE = "Sku"
XML_AVAILABILITY = "StockStatus"
XML_RETAIL = "SuggestedRetailPrice"
XML_WEBOFFER = "SuggestedRetailOfferPrice"

SUP_CODE = 2723
SUP_NAME = "Astron"
COMPANY = "900"


def convert_xml_availability_to_enum(availability):
    if (availability == 'instock'):
        return '2'
    else:
        return '4'


def create_sup_product_dict(availability, retail, weboffer):
    availability = convert_xml_availability_to_enum(availability.text)
    retail = str(retail.text).replace(',', '.')
    weboffer = str(weboffer.text).replace(',', '.')
    if weboffer == None or weboffer == '0.0' or weboffer == 'None':
        weboffer = retail
    
    if float(retail) > float(weboffer):
        discount = str(round(100 - (float(weboffer) * 100 / float(retail)), 2))
        weboffer = retail
    else:
        discount = '0.0'

    return {
        "AVAILABILITY": availability,
        "RETAIL": weboffer,
        "DISCOUNT": discount
    }


def create_hobbo_product_dict(product):
    return {
        "RETAIL": "{:.2f}".format(float(product['PRICER'])),
        "DISCOUNT": str(float(product['SODISCOUNT']))
    }
