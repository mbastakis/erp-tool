from database_connector import DatabaseConnector as dbc
import requests
import pandas as pd
from io import BytesIO
from logger import Logger
from utilities import create_xl

logger = Logger("Viopros")


SUP_CODE = 1250

def convert_xml_availability_to_enum(availability):
    if (availability == 'ΑΚΥΡΟ'):
        return '4'
    elif (availability == 'ΑΝΑΜΟΝΗ'):
        return '4'
    elif (availability == 'ΔΙΑΘΕΣΙΜΟ'):
        return '2'
    elif (availability == 'ΕΞΑΝΤΛΗΘΗΚΕ'):
        return '4'
    elif (availability == 'ΚΑΤΑΡΓΗΘΗΚΕ'):
        return '4'
    elif (availability == 'ΜΗ ΔΙΑΘΕΣΙΜΟ'):
        return '4'

def get_new_products():
    # URL for direct download from Google Drive
    google_drive_url = 'https://drive.google.com/u/0/uc?id=17blC2Uif-AusV3Iqo5Ch582VYqBXhbv1&export=download'

    response = requests.get(google_drive_url)
    if response.status_code == 200:
        file_in_memory = BytesIO(response.content)
    else:
        print(f"Failed to download file: status code {response.status_code}")
        return None

    # Define the columns to scrape for each sheet with their specific names
    common_columns = ['ΚΩΔΙΚΟΣ', 'ΛΙΑΝΙΚΗ ΤΙΜΗ ΚΑΤΑΛΟΓΟΥ', 'ΚΑΤΩΤΕΡΗ ΤΙΜΗ ΠΩΛΗΣΗΣ', 'ΔΙΑΘΕΣΙΜΟΤΗΤΑ']  # Assuming 'ΦΩΤΟΓΡΑΦΙΕΣ' appears twice and both need to be read
    viopros_columns = ['ΚΩΔΙΚΟΣ', 'ΛΙΑΝΙΚΗ ΤΙΜΗ ΚΑΤΑΛΟΓΟΥ', 'ΚΑΤΩΤΕΡΗ ΤΙΜΗ ΠΩΛΗΣΗΣ', 'ΔΙΑΘΕΣΙΜΟΤΗΤΑ']  # Assuming 'ΦΩΤΟΓΡΑΦΙΕΣ' appears twice and both need to be read

    # Read the sheets 'AnnaRiska' and 'Viopros' with their respective column names
    anna_riska_df = pd.read_excel(file_in_memory, sheet_name='AnnaRiska', usecols=common_columns, dtype={'ΚΩΔΙΚΟΣ': str})
    viopros_df = pd.read_excel(file_in_memory, sheet_name='Viopros', usecols=viopros_columns, dtype={'ΚΩΔΙΚΟΣ': str})

    # Combine data from both sheets
    combined_df = pd.concat([anna_riska_df, viopros_df])

    if combined_df['ΚΩΔΙΚΟΣ'].duplicated().any():
        print("Duplicate 'ΚΩΔΙΚΟΣ' values found. Keeping the first occurrence.")
        combined_df.drop_duplicates(subset='ΚΩΔΙΚΟΣ', keep='first', inplace=True)

    # Convert DataFrame to a dictionary
    products_dict = combined_df.set_index('ΚΩΔΙΚΟΣ').to_dict('index')

    return products_dict
    
def check_product_updates(new_products, products, products_extra):
    output = []
    seen_sup_codes = set()
    missing_product_codes = set()

    for product_code, product in products.items():
        if product_code not in new_products:
            missing_product_codes.add(product_code)
            continue

        seen_sup_codes.add(product_code)
        print("Checking product " + products[product_code]['CODE'])

        # 1. Get the product's availability from the XL
        availability = new_products[product_code]['ΔΙΑΘΕΣΙΜΟΤΗΤΑ']
        availability = convert_xml_availability_to_enum(availability)

        retail = new_products[product_code]['ΛΙΑΝΙΚΗ ΤΙΜΗ ΚΑΤΑΛΟΓΟΥ']

        weboffer = new_products[product_code]['ΚΑΤΩΤΕΡΗ ΤΙΜΗ ΠΩΛΗΣΗΣ']

        discount = str(round(100 - (float(weboffer) * 100 / float(retail)), 2))

        # 2. Get the product's availability from the database
        product_extras = products_extra[product['MTRL']]
        if not product_extras:
            print("Failed to get product extras for " + product['CODE'])
            exit()
        
        hobbo_availability = product_extras['UTBL04']
        hobbo_webactive = product_extras['BOOL01']

        hobbo_retail = "{:.2f}".format(float(product['PRICER']))
        hobbo_discount = str(float(product['SODISCOUNT']))

        # 3. Check if the product needs to be updated
        if availability == hobbo_availability and discount == hobbo_discount and retail == hobbo_retail and (hobbo_webactive == '1' if availability != '4' else hobbo_webactive == '0'):
            continue
            
        # 4. Update the database
        output.append({
            'CODE': product['CODE'],
            'CODE1': product_code,
            'PRICE': retail,
            'DISCOUNT': discount,
            'STOCK': availability,
            'KEY': product['MTRL'],
            'ISACTIVE': '1',
            'WEBACTIVE': '1' if availability != '4' else '0'
        })

    for code in missing_product_codes:
        if products[code]['ISACTIVE'] == '0':
            continue
        logger.log("Product " + products[code]['CODE'] +
                            " was not found in the XML file. Setting it to availability=4.")
        output.append({
            'CODE': products[code]['CODE'],
            'CODE1': code,
            'PRICE': 0,
            'DISCOUNT': 0,
            'STOCK': '4',
            'KEY': products[code]['MTRL'],
            'ISACTIVE': '0',
            'WEBACTIVE': '0'
        })

    return output

def main():
    db = dbc()

    if not db.login() or not db.authenticate():
        logger.log("Authentication failed")
        return

    new_products = get_new_products()
    if new_products is None:
        print("Failed to get new products from Google Drive")
        return
    
    # Get all products from the database
    products = db.get_products(SUP_CODE)
    products_extra = db.get_product_extras(900)

    # Find updates to existing products
    updated_products = check_product_updates(new_products, products, products_extra)

    # Create an Excel file with the updates
    create_xl(updated_products, "Viopros", logger.get_datetime_str())

    # Update the database
    print("Updating the database")
    if not db.update_products(updated_products):
        print("Failed to update the database")
        logger.log("Failed to update the database")
    print("Done")

    logger.log("Script finished")

if __name__ == '__main__':
    main()
