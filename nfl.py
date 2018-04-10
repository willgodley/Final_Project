import csv
import requests
import json
import sqlite3 as sqlite
from bs4 import BeautifulSoup

COMBINE_CSV = 'combine.csv'
DB_NAME = 'nfl.db'

# Connect to database
try:
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
except:
    print("Error occurred connecting to database")

def open_csv():

    try:
        combine = open(COMBINE_CSV, 'r')
        combine_data = combine.read()
        combine.close()
        return (combine_data)

    except:
        print("Error opening csv file.")
