from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc

import pandas as pd
import os
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


def initLogs():
    from datetime import datetime

    # Calculate datetime
    now = datetime.now()
    datetime_str = now.strftime("%d-%m-%Y--%H-%M-%S")
    # Create Folder
    os.mkdir("output/" + datetime_str + " PakoWorld")
    # Create log file
    with open("output/" + datetime_str + " PakoWorld/" + "log.txt", "w") as log:
        log.write("Log file created at " + datetime_str + "\n")

    return datetime_str


def log(message):
    global datetime_str
    with open("output/" + datetime_str + " PakoWorld/" + "log.txt", "a") as log:
        log.write(message + "\n")


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
            extras = db.get_product_extras(
                db_products[sup_code]['MTRL'])

            web_active = extras[1]
            availability = extras[0]
            print(availability)
            print(web_active)
            if availability == '1':
                log("Product " + db_products[sup_code]
                    ['CODE'] + " has availability 1 in Hobbo Database. Not updating.")
                continue

            # Check if discount and retail are numbers
            try:
                discount = float(db_products[sup_code]['SODISCOUNT'])
                retail = float(db_products[sup_code]['PRICER'])

                discount = str(discount)
                retail = "{:.2f}".format(retail)
            except ValueError:
                log("Product " + db_products[sup_code]
                    ['CODE'] + " has invalid discount or retail price in Hobbo Database. Setting it to availability=4.")
                output.append({
                    'CODE': db_products[sup_code]['CODE'],
                    'CODE1': sup_code,
                    'PRICE': 0,
                    'DISCOUNT': 0,
                    'STOCK': 4,
                    'KEY': db_products[sup_code]['MTRL'],
                    'ISACTIVE': '0',
                    'WEBACTIVE': '0'
                })
                continue

            # Check if it should be updated
            if (availability_xml != availability) or (discount_xml != discount) or (retail_xml != retail):
                # Update the database
                output.append({
                    'CODE': db_products[sup_code]['CODE'],
                    'CODE1': sup_code,
                    'PRICE': retail_xml,
                    'DISCOUNT': discount_xml,
                    'STOCK': availability_xml,
                    'KEY': db_products[sup_code]['MTRL'],
                    'ISACTIVE': '1',
                    'WEBACTIVE': '1' if availability_xml != '4' else '0'
                })
                # Log the updates that happened
                log("Product " + db_products[sup_code]['CODE'] + " updated from " + availability + "/" +
                    discount + "/" + retail + " to " + availability_xml + "/" + discount_xml + "/" + retail_xml)

    # Check product codes that were not found
    missing_product_codes = set(db_products.keys()) - seen_sup_codes
    for code in missing_product_codes:
        log("Product " + db_products[code]['CODE'] +
            " was not found in the XML file. Setting it to availability=4.")
        output.append({
            'CODE': db_products[code]['CODE'],
            'CODE1': code,
            'PRICE': 0,
            'DISCOUNT': 0,
            'STOCK': '4',
            'KEY': db_products[sup_code]['MTRL'],
            'ISACTIVE': '0',
            'WEBACTIVE': '0'
        })

    return output


def create_xl(hobbo_data):
    import os

    global datetime_str
    # Create xl file
    df = pd.DataFrame(
        columns=['Κωδικός Hobbo', 'Τιμή Πώλησης', 'Ποσοστό έκπτωσης', 'Διαθεσιμότητα'])
    for index, data in enumerate(hobbo_data):
        df.loc[index+2] = pd.Series(
            {'Κωδικός Hobbo': data["CODE"], 'Τιμή Πώλησης': data["PRICE"], 'Ποσοστό έκπτωσης': data["DISCOUNT"], 'Διαθεσιμότητα': data["STOCK"]})
    df.to_excel("output/" + datetime_str + " PakoWorld/" + 'PakoWorld' +
                "_διαθεσιμοτητα_" + datetime_str + ".xlsx", index=False)
    print("XL file created!")


if __name__ == "__main__":
    db = dbc()
    xml = xc(XML_URL)
    datetime_str = initLogs()

    # 1. Authenticate to the database
    if not db.login() or not db.authenticate():
        print("Authentication failed")
        log("Authentication failed")
        exit()
    print("Authentication successful")

    # 2. Download the XML file
    print("Downloading XML file")
    if not xml.download_xml():
        print("XML download failed")
        log("XML download failed")
        exit()
    print("XML download successful")

    # 3. Get hobbo products from the database
    db_products = db.get_products(SUP_CODE)

    if not db_products:
        print("Failed to retrieve products from the database")
        log("Failed to retrieve products from the database")
        exit()
    print("Successfully retrieved products from the database")

    # 4. Parse the XML file
    updated_products = parse_xml(xml.get_xml(), db_products)

    # 5. Create the XL file
    create_xl(updated_products)

    # 6. Update the database
    if not db.update_products(updated_products):
        print("Failed to update the database")
        log("Failed to update the database")
        exit()

    print("Finished successfully!")
    log("Finished successfully!")
