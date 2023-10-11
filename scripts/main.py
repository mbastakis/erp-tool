from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl

import argparse
import importlib
import xml.etree.ElementTree as ET


def get_product_extras(product, product_extras):
    # Check if product has extras
    if not product_extras:
        logger.log(
            "Product " + product['CODE'] + " has no extras (availability, Webactive) in Hobbo Database. Not updating.")
        return False

    # Get product webactive
    web_active = product_extras["BOOL01"]
    if web_active == None:
        logger.log(
            "Product " + product['CODE'] + " has no Webactive in Hobbo Database. Not updating.")
        return False

    # Get product availability
    availability = product_extras["UTBL04"]
    if availability == None:
        logger.log(
            "Product " + product['CODE'] + " has no availability in Hobbo Database. Not updating.")
        return False
    elif availability == '1':
        logger.log(
            "Product " + product['CODE'] + " has availability 1 in Hobbo Database. Not updating.")
        return False

    return {
        'WEBACTIVE': web_active,
        'AVAILABILITY': availability
    }


def check_product_update(sup_dict, hobbo_dict, product_extras):
    return (sup_dict["AVAILABILITY"] != product_extras["AVAILABILITY"]) or \
        (sup_dict["DISCOUNT"] != hobbo_dict["DISCOUNT"]) or \
        (sup_dict["RETAIL"] != hobbo_dict["RETAIL"]) or \
        (product_extras["WEBACTIVE"] == '0'
         and sup_dict["AVAILABILITY"] != '4')


def parse_xml(xml_string, db_products, db_products_extras):
    global db
    global module
    global logger

    root = ET.fromstring(xml_string)

    output = []
    seen_sup_codes = set()

    for product in root.findall(module.XML_ROOT):
        sup_code = product.find(module.XML_CODE).text

        # 1.Check if the product exists in the xml
        if sup_code not in db_products:
            continue

        # 2.Get Product info from XML
        print("Checking product " + db_products[sup_code]['CODE'])
        seen_sup_codes.add(sup_code)

        availability_element = product.find(module.XML_AVAILABILITY)
        retail_element = product.find(module.XML_RETAIL)
        weboffer_element = product.find(module.XML_WEBOFFER)

        sup_dict = module.create_sup_product_dict(
            availability_element, retail_element, weboffer_element)

        # 3.Get Product info from Database
        product_extras = get_product_extras(
            db_products[sup_code], db_products_extras[db_products[sup_code]['MTRL']])
        if not product_extras:
            continue

        hobbo_dict = module.create_hobbo_product_dict(db_products[sup_code])

        # 4.Check if the product needs to be updated
        if not check_product_update(sup_dict, hobbo_dict, product_extras):
            continue
        # 5.Update the database
        output.append({
            'CODE': db_products[sup_code]['CODE'],
            'CODE1': sup_code,
            'PRICE': sup_dict["RETAIL"],
            'DISCOUNT': sup_dict["DISCOUNT"],
            'STOCK': sup_dict["AVAILABILITY"],
            'KEY': db_products[sup_code]['MTRL'],
            'ISACTIVE': '1',
            'WEBACTIVE': '1' if sup_dict["AVAILABILITY"] != '4' else '0'
        })
        # 6.Log the updates that happened
        logger.log("Product " + db_products[sup_code]['CODE'] + " updated from " + product_extras["AVAILABILITY"] + "/" +
                   hobbo_dict["DISCOUNT"] + "/" + hobbo_dict["RETAIL"] + "/" + product_extras["WEBACTIVE"] + " to " + sup_dict["AVAILABILITY"] + "/" + sup_dict["DISCOUNT"] + "/" + sup_dict["RETAIL"] + "/" + ('1' if sup_dict["AVAILABILITY"] != '4' else '0') + " (Availability/Discount/Retail/WebActive)")

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
    # 0. Find the supplier name
    parser = argparse.ArgumentParser()
    parser.add_argument("supplier", help="The supplier to update")
    args = parser.parse_args()

    try:
        module = importlib.import_module(args.supplier)
    except ImportError:
        print("Supplier not found")
        exit()

    # 0.5 Init
    db = dbc()
    xml = xc(module.XML_URL)
    logger = Logger(module.SUP_NAME)

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
    db_products = db.get_products(module.SUP_CODE)
    if not db_products:
        print("Failed to retrieve products from the database")
        logger.log("Failed to retrieve products from the database")
        exit()
    print("Successfully retrieved products from the database")

    # 3.5 Get the extras for each product
    db_products_extras = db.get_product_extras(module.COMPANY)
    if not db_products_extras:
        print("Failed to retrieve products extras from the database")
        logger.log("Failed to retrieve products extras from the database")
        exit()
    print("Successfully retrieved products extras from the database")

    # 4. Parse the XML file
    updated_products = parse_xml(
        xml.get_xml(), db_products, db_products_extras)

    # 5. Create the XL file
    create_xl(updated_products, module.SUP_NAME, logger.get_datetime_str())
    print("XL file created successfully")

    # 6. Update the database
    # print("Updating the database")
    # if not db.update_products(updated_products):
    #     print("Failed to update the database")
    #     logger.log("Failed to update the database")
    #     exit()
    # print("Database updated successfully")

    print("Finished successfully!")
    logger.log("Finished successfully!")
