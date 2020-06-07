from pymongo import MongoClient
import csv


def extract_csv(file_path,name_of_file):
    csvfile = open(file_path, 'r')
    reader = csv.DictReader( csvfile )
    mongo_client=MongoClient() 
    db=mongo_client.databaseFor2
    header = next(reader)
    for each in reader:
        row={}
        for field in header:
            row[field]=each[field]
            print("Inserting")

        db['data'].insert(row)