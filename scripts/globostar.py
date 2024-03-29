from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://www.ledking.gr/catalog-export/xml/oRrR0RPd8v0F77EMhe9RWof6zJl2plljIvMfiBjLqe4"
XML_ROOT = "product"
XML_CODE = "code"
XML_AVAILABILITY = "availability"
XML_RETAIL = "price_with_vat"
XML_WEBOFFER = "price_internet_with_vat"

SUP_CODE = 1140
SUP_NAME = "Globostar"

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

    discount = "0.0"
    # discount = str(round(100 - (float(weboffer) * 100 / float(retail)), 2))
    # print(discount)
    # if discount == '-0.0':
    #     discount = '0.0'

    # Here I changed them place, the retail will be the web offer, we had an issue with the weboffer prices
    # Being higher than the retail prices. And as result we got negative discounts.
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
