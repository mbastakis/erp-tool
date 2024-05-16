from database_connector import DatabaseConnector as dbc
from xml_connector import XmlConnector as xc
from logger import Logger
from utilities import create_xl

import argparse
import importlib
import xml.etree.ElementTree as ET

import tempfile


class ProductUpdater:

    def __init__(self, module):
        self.db = dbc()
        self.xml = xc(module.XML_URL)
        self.logger = Logger(module.SUP_NAME)
        self.module = module

    def get_product_extras(self, product, product_extras):
        # Check if product has extras
        if not product_extras:
            self.logger.log(
                "Product " + product['CODE'] + " has no extras (availability, Webactive) in Hobbo Database. Not updating.")
            return False

        # Get product webactive
        web_active = product_extras["BOOL01"]
        if web_active == None:
            self.logger.log(
                "Product " + product['CODE'] + " has no Webactive in Hobbo Database. Not updating.")
            return False

        # Get product availability
        availability = product_extras["UTBL04"]
        if availability == None:
            self.logger.log(
                "Product " + product['CODE'] + " has no availability in Hobbo Database. Not updating.")
            return False
        elif availability == '1':
            self.logger.log(
                "Product " + product['CODE'] + " has availability 1 in Hobbo Database. Not updating.")
            return False

        return {
            'WEBACTIVE': web_active,
            'AVAILABILITY': availability
        }

    def check_product_update(self, sup_dict, hobbo_dict, product_extras):
        return (sup_dict["AVAILABILITY"] != product_extras["AVAILABILITY"]) or \
            (sup_dict["DISCOUNT"] != hobbo_dict["DISCOUNT"]) or \
            (sup_dict["RETAIL"] != hobbo_dict["RETAIL"]) or \
            (product_extras["WEBACTIVE"] == '0'
             and sup_dict["AVAILABILITY"] != '4')

    def parse_xml(self, xml_string, db_products, db_products_extras):
        # create temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='wb')
        temp_file.write(xml_string)
        temp_file.close()
        if not temp_file:
            self.logger.log("Could not create xml file")
            return
        
        # root = ET.fromstring(xml_string)

        output = []
        seen_sup_codes = set()

        for event, product in ET.iterparse(temp_file.name, events=("end",)):
            if product.tag == self.module.XML_ROOT:
                sup_code = product.find(self.module.XML_CODE).text

                # 1.Check if the product exists in the xml
                if sup_code not in db_products:
                    continue

                # 2.Get Product info from XML
                print("Checking product " + db_products[sup_code]['CODE'])
                seen_sup_codes.add(sup_code)

                availability_element = product.find(self.module.XML_AVAILABILITY)
                retail_element = product.find(self.module.XML_RETAIL)
                weboffer_element = product.find(self.module.XML_WEBOFFER)
                
                product.clear()
                
                sup_dict = self.module.create_sup_product_dict(
                    availability_element, retail_element, weboffer_element)

                # 3.Get Product info from Database
                product_extras = self.get_product_extras(
                    db_products[sup_code], db_products_extras[db_products[sup_code]['MTRL']])
                if not product_extras:
                    continue

                hobbo_dict = self.module.create_hobbo_product_dict(
                    db_products[sup_code])

                # 4.Check if the product needs to be updated
                if not self.check_product_update(sup_dict, hobbo_dict, product_extras):
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
                self.logger.log("Product " + db_products[sup_code]['CODE'] + " updated from " + product_extras["AVAILABILITY"] + "/" +
                                hobbo_dict["DISCOUNT"] + "/" + hobbo_dict["RETAIL"] + "/" + product_extras["WEBACTIVE"] + " to " + sup_dict["AVAILABILITY"] + "/" + sup_dict["DISCOUNT"] + "/" + sup_dict["RETAIL"] + "/" + ('1' if sup_dict["AVAILABILITY"] != '4' else '0') + " (Availability/Discount/Retail/WebActive)")

        # Check product codes that were not found
        missing_product_codes = set(db_products.keys()) - seen_sup_codes
        for code in missing_product_codes:
            if db_products[code]['ISACTIVE'] == '0':
                continue
            if db_products_extras[db_products[code]['MTRL']]['UTBL04'] == '1':
                print("Product " + db_products[code]['CODE'] + " has availability 1. Not updating.")
                continue
            self.logger.log("Product " + db_products[code]['CODE'] +
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

    def main(self):
        if not self.db.login() or not self.db.authenticate():
            self.logger.log("Authentication failed")
            return

        print("Downloading XML...")
        if not self.xml.download_xml():
            self.logger.log("XML download failed")
            return

        db_products = self.db.get_products(self.module.SUP_CODE)
        db_products_extras = self.db.get_product_extras(self.module.COMPANY)

        updated_products = self.parse_xml(
            self.xml.get_xml(), db_products, db_products_extras)

        create_xl(updated_products, self.module.SUP_NAME,
                  self.logger.get_datetime_str())

        # print("Updating the database")
        # if not self.db.update_products(updated_products):
        #     print("Failed to update the database")
        #     self.logger.log("Failed to update the database")
        #     exit(-1)
        # print("Database updated successfully")

        self.logger.log("Finished successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("supplier", help="The supplier to update")
    args = parser.parse_args()

    try:
        module = importlib.import_module(args.supplier)
    except ImportError:
        print("Supplier not found")
        exit(-1)

    updater = ProductUpdater(module)
    updater.main()
    exit(0)
