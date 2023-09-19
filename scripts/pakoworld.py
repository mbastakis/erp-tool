from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc

import pandas as pd
import xml.etree.ElementTree as ET

# Constants
XML_URL = "https://www.pakoworld.com/?route=extension/feed/csxml_feed&token=MTUzOTNMUDQwNQ==&lang=el"
XML_ROOT = "products/product"
XML_CODE = "model"
XML_AVAILABILITY = "availability"
XML_RETAIL = "retail_price_with_vat"
XML_WEBOFFER = "weboffer_price_with_vat"

SUP_CODE = 105


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


def parse_xml(xml_string, db_products):
    global db
    root = ET.fromstring(xml_string)

    output = []
    seen_sup_codes = set()

    for product in root.findall(XML_ROOT):
        sup_code = product.find(XML_CODE).text

        if sup_code in db_products:
            seen_sup_codes.add(sup_code)

            # Info from XML
            availability_xml = convert_xml_availability_to_enum(
                product.find(XML_AVAILABILITY).text)
            retail_xml = str(product.find(XML_RETAIL).text)
            weboffer_xml = str(product.find(XML_WEBOFFER).text)

            discount_xml = str(round(100 - (float(weboffer_xml) *
                                            100 / float(retail_xml)), 2))

            # Get availability from database
            availability = db.get_product_stock_status(
                db_products[sup_code]['MTRL'])
            if availability == '1':
                continue

            # Check if discount and retail are numbers
            try:
                discount = float(db_products[sup_code]['SODISCOUNT'])
                retail = float(db_products[sup_code]['PRICER'])

                discount = str(discount)
                retail = "{:.2f}".format(retail)
            except ValueError:
                output.append({
                    'CODE': db_products[sup_code]['CODE'],
                    'CODE1': sup_code,
                    'PRICE': 0,
                    'DISCOUNT': 0,
                    'STOCK': 4
                })
                continue

            # Check if it should be updated
            if (availability_xml != availability) or (discount_xml != discount) or (retail_xml != retail):
                output.append({
                    'CODE': db_products[sup_code]['CODE'],
                    'CODE1': sup_code,
                    'PRICE': retail_xml,
                    'DISCOUNT': discount_xml,
                    'STOCK': availability_xml
                })

            # Check product codes that were not found
            missing_product_codes = set(db_products.keys()) - seen_sup_codes
            for code in missing_product_codes:
                output.append({
                    'CODE': db_products[code]['CODE'],
                    'CODE1': code,
                    'PRICE': 0,
                    'DISCOUNT': 0,
                    'STOCK': '4'
                })


def create_xl(hobbo_data):
    from datetime import datetime
    import os

    # Calculate datetime
    now = datetime.now()
    datetime_str = now.strftime("%d-%m-%Y--%H-%M-%S")
    # Create Folder
    os.mkdir("output/" + datetime_str + " PakoWorld")
    # Create xl file
    df = pd.DataFrame(
        columns=['Κωδικός Hobbo', 'Τιμή Πώλησης', 'Ποσοστό έκπτωσης', 'Διαθεσιμότητα'])
    for index, data in enumerate(hobbo_data):
        df.loc[index+2] = pd.Series(
            {'Κωδικός Hobbo': data["hobbo_code"], 'Τιμή Πώλησης': data["retail"], 'Ποσοστό έκπτωσης': data["discount"], 'Διαθεσιμότητα': data["availability"]})
    df.to_excel("output/" + datetime_str + " PakoWorld/" + 'PakoWorld' +
                "_διαθεσιμοτητα_" + datetime_str + ".xlsx", index=False)
    print("XL file created!")


if __name__ == "__main__":
    db = dbc()
    xml = xc(XML_URL)

    # 1. Authenticate to the database
    if not db.login() or not db.authenticate():
        print("Authentication failed")
        exit()
    print("Authentication successful")

    # 2. Download the XML file
    print("Downloading XML file")
    if not xml.download_xml():
        print("XML download failed")
        exit()
    print("XML download successful")

    # 3. Get hobbo products from the database
    db_products = db.get_products(SUP_CODE)
    if not db_products:
        print("Failed to retrieve products from the database")
        exit()
    print("Successfully retrieved products from the database")

    # 4. Parse the XML file
    updated_products = parse_xml(xml.get_xml(), db_products)

    # 5. Create the XL file
    create_xl(updated_products)
