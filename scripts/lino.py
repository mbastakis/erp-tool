from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl


import xml.etree.ElementTree as ET

# Constants
XML_URL = ""
XML_ROOT = ""
XML_CODE = ""
XML_AVAILABILITY = ""
XML_RETAIL = ""
XML_WEBOFFER = ""

SUP_CODE = 47
SUP_NAME = "Lino"
COMPANY = "900"


# Logic
def convert_xml_availability_to_enum(availability):
    if (availability == 'Διαθέσιμο'):
        return '2'
    elif (availability == 'Εξαντλήθηκε'):
        return '4'
    elif (availability == 'Αναμένεται'):
        return '4'
    elif (availability == 'Άμεση παραλαβή | Παράδοση σε 1 έως 3 ημέρες εργάσιμες'):
        return '2'
    elif (availability == 'Κατόπιν Παραγγελίας (30 Ημέρες)'):
        return '5'
    elif (availability == 'Παραλαβή ή Παράδοση, σε 4-10 εργάσιμες ημέρες'):
        return '2'


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
