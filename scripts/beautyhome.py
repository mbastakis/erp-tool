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


def parse_xml(xml_string, db_products, db_products_extras):
    global db
    root = ET.fromstring(xml_string)

    output = []
    seen_sup_codes = set()

    for product in root.findall(XML_ROOT):
        sup_code = product.find(XML_CODE).text

        if sup_code in db_products:
            print("Checking product " + db_products[sup_code]['CODE'])
            seen_sup_codes.add(sup_code)

            # Info from XML
            availability_xml = convert_xml_availability_to_enum(
                product.find(XML_AVAILABILITY).text)
            if availability_xml == None:
                logger.log("Product " + db_products[sup_code]
                           ['CODE'] + " has invalid availability in XML file. Not updating.")
                continue

            retail_xml = str(product.find(XML_RETAIL).text)
            if retail_xml == 'None':
                logger.log("Product " + db_products[sup_code]
                           ['CODE'] + " has invalid retail price in XML file. Not updating.")
                continue

            weboffer_xml = str(product.find(XML_WEBOFFER).text)
            if weboffer_xml == 'None':
                discount_xml = '0.0'
            else:
                discount_xml = str(round(100 - (float(weboffer_xml) *
                                                100 / float(retail_xml)), 2))

            # Get availability from database
            extras = db_products_extras[db_products[sup_code]['MTRL']]
            if not extras:
                logger.log("Product " + db_products[sup_code]
                           ['CODE'] + " has no extras (availability, Webactive) in Hobbo Database. Not updating.")
                continue

            web_active = extras["BOOL01"]
            if web_active == None:
                logger.log("Product " + db_products[sup_code]
                           ['CODE'] + " has no Webactive in Hobbo Database. Not updating.")
                continue
            availability = extras["UTBL04"]
            if availability == None:
                logger.log("Product " + db_products[sup_code]
                           ['CODE'] + " has no availability in Hobbo Database. Not updating.")
                continue

            if availability == '1':
                logger.log("Product " + db_products[sup_code]
                           ['CODE'] + " has availability 1 in Hobbo Database. Not updating.")
                continue

            # Check if discount and retail are numbers
            try:
                discount = float(db_products[sup_code]['SODISCOUNT'])
                retail = float(db_products[sup_code]['PRICER'])

                discount = str(discount)
                retail = "{:.2f}".format(retail)
            except ValueError:
                logger.log("Product " + db_products[sup_code]
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
                logger.log("Product " + db_products[sup_code]['CODE'] + " updated from " + availability + "/" +
                           discount + "/" + retail + " to " + availability_xml + "/" + discount_xml + "/" + retail_xml)

    # Check product codes that were not found
    missing_product_codes = set(db_products.keys()) - seen_sup_codes
    for code in missing_product_codes:
        if db_products[code]['ISACTIVE'] == '0':
            continue
        logger.log("Product " + db_products[code]['CODE'] +
                   " was not found in the XML file. Setting it to availability=4.")
        output.append({
            'CODE': db_products[code]['CODE'],
            'CODE1': code,
            'PRICE': 0,
            'DISCOUNT': 0,
            'STOCK': '4',
            'KEY': db_products[code]['MTRL'],
            'ISACTIVE': '0',
            'WEBACTIVE': '0'
        })

    return output


if __name__ == "__main__":
    db = dbc()
    xml = xc(XML_URL)
    logger = Logger(SUP_NAME)

    # 1. Authenticate to the database
    if not db.login() or not db.authenticate():
        print("Authentication failed")
        logger.log("Authentication failed")
        exit()
    print("Authentication successful")

    # 2. Download the XML file
    print("Downloading XML file")
    if not xml.download_xml():
        print("XML download failed")
        logger.log("XML download failed")
        exit()
    print("XML download successful")

    # 3. Get hobbo products from the database
    db_products = db.get_products(SUP_CODE)
    if not db_products:
        print("Failed to retrieve products from the database")
        logger.log("Failed to retrieve products from the database")
        exit()
    print("Successfully retrieved products from the database")

    # 3.5 Get the extras for each product
    db_products_extras = db.get_product_extras(COMPANY)
    if not db_products_extras:
        print("Failed to retrieve products extras from the database")
        logger.log("Failed to retrieve products extras from the database")
        exit()
    print("Successfully retrieved products extras from the database")

    # 4. Parse the XML file
    updated_products = parse_xml(
        xml.get_xml(), db_products, db_products_extras)

    # 5. Create the XL file
    create_xl(updated_products, SUP_NAME, logger.get_datetime_str())
    print("XL file created successfully")

    # 6. Update the database
    print("Updating the database")
    if not db.update_products(updated_products):
        print("Failed to update the database")
        logger.log("Failed to update the database")
        exit()
    print("Database updated successfully")

    print("Finished successfully!")
    logger.log("Finished successfully!")
