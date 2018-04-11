import csv
import requests
import json
import sqlite3 as sqlite
from bs4 import BeautifulSoup

COMBINE_CSV = 'combine.csv'
DB_NAME = 'nfl.db'

# Connect to database
try:
    conn = sqlite.connect(DB_NAME)
    cur = conn.cursor()
except:
    print("Error occurred connecting to database")

def make_combine_table():
    statement = "DROP TABLE IF EXISTS 'Combine'"
    cur.execute(statement)

    # Create new Countries table
    statement = """
        CREATE TABLE 'Combine' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Name' TEXT NOT NULL,
          'Position' TEXT NOT NULL,
          'College' FLOAT NOT NULL,
          'FortyTime' TEXT NOT NULL,
          'NflGrade' FLOAT NOT NULL,
          'Year' INTEGER NOT NULL
        );
        """
    cur.execute(statement)

def make_draft_table():
    statement = "DROP TABLE IF EXISTS 'Draft'"
    cur.execute(statement)

    # Create new Countries table
    statement = """
        CREATE TABLE 'Draft' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Name' TEXT NOT NULL,
          'NameId' INTEGER,
          'Position' TEXT NOT NULL,
          'DraftRound' INTEGER NOT NULL,
          'DraftPick' INTEGER NOT NULL,
          'College' TEXT NOT NULL
        );
        """
    cur.execute(statement)

def make_stats_table():
    statement = "DROP TABLE IF EXISTS 'Stats'"
    cur.execute(statement)

    # Create new Countries table
    statement = """
        CREATE TABLE 'Stats' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Name' TEXT NOT NULL,
          'NameId' INTEGER,
          'Team' TEXT NOT NULL,
          'Postion' TEXT NOT NULL,
          'Games' TEXT NOT NULL,
          'Yards' TEXT NOT NULL,
          'TD' INTEGER NOT NULL
        );
        """
    cur.execute(statement)

def insert_combine_data():

    # MAKE SURE YOU FIX THIS
    pass

    round_num = 0
    with open(COMBINE_CSV) as combine_csv:
        combine_data = csv.reader(combine_csv)
        for player in combine_data:
            if round_num == 0:
                round_num += 1
                continue

            name = player[1]
            position = player[4]
            college = player[20]
            forty = player[11]
            nfl_grade = player[25]
            year = player[0]

            insertion = (None, name, position, college, forty, nfl_grade, year)
            statement = 'INSERT INTO "Combine" '
            statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)

            round_num += 1

    # Commit changes and close database connection
    conn.commit()
    conn.close()

def cacheOpen(name):

    try:
        cache_file = open(name, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}

    return cache_dict

def cacheWrite(name, cache_dict):

    dumped_json_cache = json.dumps(cache_dict)
    fw = open(name, "w")
    fw.write(dumped_json_cache)
    fw.close()

def crawl_draft_data():
    players = []
    table_contents = []
    cache_name = 'draft.json'

    base_url = 'https://www.pro-football-reference.com'
    first_draft_url = '/years/2010/draft.htm'
    full_url = base_url + first_draft_url

    year = 2010
    while year < 2015:
        draft_cache = cacheOpen(cache_name)

        if full_url in draft_cache:
            page_text = draft_cache[full_url]
        else:
            page_resp = requests.get(full_url)
            page_text = page_resp.text
            draft_cache[full_url] = page_text
            cacheWrite(cache_name, draft_cache)

        page_soup = BeautifulSoup(page_text, 'html.parser')

        next_button = page_soup.find(class_ = 'button2 next')
        next_draft_url = next_button['href']
        next_url = base_url + next_draft_url

        drafted_table = page_soup.find('table', id = 'drafts')
        drafted_table_body = drafted_table.find('tbody')
        cells = []
        for row in drafted_table_body:
            for cell in row:
                try:
                    cells.append(cell.text.strip())
                    table_contents.append(cells)
                except:
                    continue
        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])

    print(type(table_contents))

def crawl_passing_data():
    passer_stats = []
    cache_name = 'stats.json'

    base_url = 'https://www.pro-football-reference.com'
    first_draft_url = '/years/2010/passing.htm'
    full_url = base_url + first_draft_url

    #passer stats
    year = 2010
    while year < 2015:
        stats_cache = cacheOpen(cache_name)

        if full_url in stats_cache:
            page_text = stats_cache[full_url]
        else:
            page_resp = requests.get(full_url)
            page_text = page_resp.text
            stats_cache[full_url] = page_text
            cacheWrite(cache_name, stats_cache)

        page_soup = BeautifulSoup(page_text, 'html.parser')

        next_button = page_soup.find(class_ = 'button2 next')
        next_year_url = next_button['href']
        next_url = base_url + next_year_url

        passing_table = page_soup.find('table', id = 'passing')
        passing_table_body = passing_table.find('tbody')
        cells = []
        for row in passing_table_body:
            for cell in row:
                try:
                    cells.append(cell.text.strip())
                    table_contents.append(cells)
                except:
                    continue

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])

    print(type(table_contents))

def crawl_rushing_data():
    rushing_stats = []
    cache_name = 'stats.json'

    base_url = 'https://www.pro-football-reference.com'
    first_draft_url = '/years/2010/rushing.htm'
    full_url = base_url + first_draft_url

    #passer stats
    year = 2010
    while year < 2015:
        stats_cache = cacheOpen(cache_name)

        if full_url in stats_cache:
            page_text = stats_cache[full_url]
        else:
            page_resp = requests.get(full_url)
            page_text = page_resp.text
            stats_cache[full_url] = page_text
            cacheWrite(cache_name, stats_cache)

        page_soup = BeautifulSoup(page_text, 'html.parser')

        next_button = page_soup.find(class_ = 'button2 next')
        next_year_url = next_button['href']
        next_url = base_url + next_year_url

        rushing_table = page_soup.find('table', id = 'rushing')
        rushing_table_body = rushing_table.find('tbody')
        cells = []
        for row in rushing_table_body:
            for cell in row:
                try:
                    cells.append(cell.text.strip())
                    table_contents.append(cells)
                except:
                    continue

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])

    print(type(table_contents))

def crawl_receiving_data():
    receiving_stats = []
    cache_name = 'stats.json'

    base_url = 'https://www.pro-football-reference.com'
    first_draft_url = '/years/2010/receiving.htm'
    full_url = base_url + first_draft_url

    #passer stats
    year = 2010
    while year < 2015:
        stats_cache = cacheOpen(cache_name)

        if full_url in stats_cache:
            page_text = stats_cache[full_url]
        else:
            page_resp = requests.get(full_url)
            page_text = page_resp.text
            stats_cache[full_url] = page_text
            cacheWrite(cache_name, stats_cache)

        page_soup = BeautifulSoup(page_text, 'html.parser')

        next_button = page_soup.find(class_ = 'button2 next')
        next_year_url = next_button['href']
        next_url = base_url + next_year_url

        receiving_table = page_soup.find('table', id = 'receiving')
        receiving_table_body = receiving_table.find('tbody')
        cells = []
        for row in receiving_table_body:
            for cell in row:
                try:
                    cells.append(cell.text.strip())
                    table_contents.append(cells)
                except:
                    continue

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])

    print(type(table_contents))

make_combine_table()
insert_combine_data()
crawl_draft_data()
crawl_passing_data()
crawl_rushing_data()
crawl_receiving_data()
