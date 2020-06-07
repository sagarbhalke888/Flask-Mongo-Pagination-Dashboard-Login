from pymongo import MongoClient
import csv


def extract_csv1(file_path,name_of_file):
    csvfile = open(file_path, 'r')
    reader = csv.DictReader( csvfile )
    mongo_client=MongoClient() 
    db=mongo_client.DataExtracted
    db[name_of_file].drop()
    header = next(reader)
    for each in reader:
        row={}
        for field in header:
            row[field]=each[field]

        db[name_of_file].insert(row)