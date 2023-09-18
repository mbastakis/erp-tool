from db import DatabaseConnector as dbc

db = dbc()

if not db.login():
    print("Login failed")
    exit()

if not db.authenticate():
    print("Authentication failed")
    exit()

products, count = db.get_products(105)
print(products)
