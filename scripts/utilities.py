import os
import pandas as pd


def create_xl(hobbo_data, sup_name, datetime_str):
    # Create xl file
    df = pd.DataFrame(
        columns=['Κωδικός Hobbo', 'Τιμή Πώλησης', 'Ποσοστό έκπτωσης', 'Διαθεσιμότητα', 'IsActive', 'WebActive'])
    for index, data in enumerate(hobbo_data):
        df.loc[index+2] = pd.Series({
                'Κωδικός Hobbo': data["CODE"], 
                'Τιμή Πώλησης': data["PRICE"], 
                'Ποσοστό έκπτωσης': data["DISCOUNT"], 'Διαθεσιμότητα': data["STOCK"],
                'IsActive': data["ISACTIVE"],
                'WebActive': data["WEBACTIVE"]
            })
    df.to_excel("output/" + datetime_str + " " + sup_name + "/" + sup_name +
                "_διαθεσιμοτητα_" + datetime_str + ".xlsx", index=False)

    return True


def get_excluded_codes():
    words = []
    with open('./.excluded_codes.conf', 'r') as file:
        for line in file:
            word = line.strip()
            words.append(word)
    return words


def str_to_int(item):
    if item == None:
        return 0
    elif type(item) == float and math.isnan(item):
        return 0
    else:
        return float(item.split(' ')[0])

    return
