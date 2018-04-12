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

class Player():

    def __init__(self, nm, n_id,  ps, round_num, pick, clg, draft_yr, stats):
        self.name = nm
        self.name_id = n_id
        self.position = ps
        self.round = round_num
        self.pick = pick
        self.college = clg
        self.draft_year = draft_yr
        self.avg_yards = self.compute_stats(stats)[0]
        self.avg_td = self.compute_stats(stats)[1]

    def __str__(self):
        return "{} ({}) was drafted in round {}, {} overall in {}. He averaged {} yards and {} TDs in a season in the 2010-2014 seasons. He went to {}.".format(self.name, self.position, self.round, self.pick, self.draft_year, self.avg_yards, self.avg_td, self.college)

    def compute_stats(self, stats):
        total_yards = 0
        total_td = 0
        total_years = len(stats)
        if self.position == 'QB':
            for year in stats:
                total_yards += int(year[11])
                total_td += int(year[12])

        elif self.position == 'RB':
            for year in stats:
                total_yards += int(year[8])
                total_td += int(year[9])

        elif self.position == 'WR':
            for year in stats:
                total_yards += int(year[10])
                total_td += int(year[12])


        avg_yards = str(total_yards / total_years)
        yards_split = avg_yards.split('.')
        yards = yards_split[0]
        yards_decimal = yards_split[1][0]
        avg_yards = float(yards + '.' + yards_decimal)

        avg_td = str(total_td / total_years)
        td_split = avg_td.split('.')
        tds = td_split[0]
        tds_decimal = td_split[1][0]
        avg_td = float(tds + '.' + tds_decimal)

        return(avg_yards, avg_td)

def make_combine_table():
    statement = "DROP TABLE IF EXISTS 'Combine'"
    cur.execute(statement)

    # Create new Combine table
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

    # Create new Draft table
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

    # Create new Stats table
    statement = """
        CREATE TABLE 'Stats' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Name' TEXT NOT NULL,
          'NameId' INTEGER,
          'Team' TEXT NOT NULL,
          'Postion' TEXT NOT NULL,
          'Yards' TEXT NOT NULL,
          'TD' INTEGER NOT NULL,
          'Seasons' TEXT NOT NULL
        );
        """
    cur.execute(statement)

def insert_combine_data():

    names_and_keys = {}
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

            names_and_keys[name] = round_num

            insertion = (None, name, position, college, forty, nfl_grade, year)
            statement = 'INSERT INTO "Combine" '
            statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)

            round_num += 1

    # Commit changes and close database connection
    conn.commit()
    conn.close()

    return names_and_keys

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
    raw_data_cache = 'raw_data.json'

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

        raw_data_dict = cacheOpen(raw_data_cache)
        split_url = full_url.split('/')
        current_year = int(split_url[4])
        key = str(current_year) + ' draft'
        if key in raw_data_dict:
            draft_data = raw_data_dict[key]
            table_contents.append(draft_data)
        else:
            current_year_draft = []
            drafted_table = page_soup.find('table', id = 'drafts')
            drafted_table_body = drafted_table.find('tbody')
            for row in drafted_table_body:
                cells = []
                for cell in row:
                    try:
                        cells.append(cell.text.strip())
                    except:
                        continue
                if len(cells) != 0:
                    current_year_draft.append(cells)
                    table_contents.append(cells)

            raw_data_dict[key] = current_year_draft
            cacheWrite(raw_data_cache, raw_data_dict)

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])


def crawl_passing_data():
    passer_stats = []
    table_contents = []
    cache_name = 'stats.json'
    raw_data_cache = 'raw_data.json'

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

        raw_data_dict = cacheOpen(raw_data_cache)
        split_url = full_url.split('/')
        current_year = int(split_url[4])
        key = str(current_year) + ' passing'

        if key in raw_data_dict:
            passing_data = raw_data_dict[key]
            table_contents.append(passing_data)
        else:
            current_year_stats = []
            passing_table = page_soup.find('table', id = 'passing')
            passing_table_body = passing_table.find('tbody')
            for row in passing_table_body:
                cells = []
                for cell in row:
                    try:
                        cells.append(cell.text.strip())
                    except:
                        continue
                if len(cells) != 0:
                    table_contents.append(cells)
                    current_year_stats.append(cells)

            raw_data_dict[key] = current_year_stats
            cacheWrite(raw_data_cache, raw_data_dict)

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])


def crawl_rushing_data():
    rushing_stats = []
    table_contents = []
    cache_name = 'stats.json'
    raw_data_cache = 'raw_data.json'

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

        raw_data_dict = cacheOpen(raw_data_cache)
        split_url = full_url.split('/')
        current_year = int(split_url[4])
        key = str(current_year) + ' rushing'

        if key in raw_data_dict:
            rushing_data = raw_data_dict[key]
            table_contents.append(rushing_data)
        else:
            current_year_stats = []
            rushing_table = page_soup.find('table', id = 'rushing_and_receiving')
            rushing_table_body = rushing_table.find('tbody')
            for row in rushing_table_body:
                cells = []
                for cell in row:
                    try:
                        cells.append(cell.text.strip())
                    except:
                        continue
                if len(cells) != 0:
                    current_year_stats.append(cells)
                    table_contents.append(cells)

            raw_data_dict[key] = current_year_stats
            cacheWrite(raw_data_cache, raw_data_dict)

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])


def crawl_receiving_data():
    receiving_stats = []
    table_contents = []
    cache_name = 'stats.json'
    raw_data_cache = 'raw_data.json'

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

        raw_data_dict = cacheOpen(raw_data_cache)
        split_url = full_url.split('/')
        current_year = int(split_url[4])
        key = str(current_year) + ' receiving'
        if key in raw_data_dict:
            receiving_data = raw_data_dict[key]
            table_contents.append(receiving_data)
        else:
            current_year_stats = []
            receiving_table = page_soup.find('table', id = 'receiving')
            receiving_table_body = receiving_table.find('tbody')
            for row in receiving_table_body:
                cells = []
                for cell in row:
                    try:
                        cells.append(cell.text.strip())
                    except:
                        continue
                if len(cells) != 0:
                    current_year_stats.append(cells)
                    table_contents.append(cells)

            raw_data_dict[key] = current_year_stats
            cacheWrite(raw_data_cache, raw_data_dict)

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])


def initialize_player_data(foreign_keys_dict):
    raw_data_cache = 'raw_data.json'
    raw_data = cacheOpen(raw_data_cache)
    all_draft_data = []
    all_rushing_data = []
    all_receiving_data = []
    all_passing_data = []
    players = []

    for key in raw_data.keys():
        if 'draft' in key:
            year_drafted = key.split()[0]
            draft_info = raw_data[key]
            for player in draft_info:
                player.append(year_drafted)
            all_draft_data.append(raw_data[key])
        elif 'rushing' in key:
            all_rushing_data.append(raw_data[key])
        elif 'receiving' in key:
            all_receiving_data.append(raw_data[key])
        elif 'passing' in key:
            all_passing_data.append(raw_data[key])

    for draft_year in all_draft_data:
        for player in draft_year:
            name = player[3]
            draft_round = player[0]
            draft_pick = player[1]
            position = player[4]
            college = player[27]
            draft_year = player[29]
            stats = []

            if name in foreign_keys_dict:
                name_id = foreign_keys_dict[name]

            if 'QB' in position:
                for season in all_passing_data:
                    for player in season:
                        if name in player:
                            stats.append(player)

            elif 'RB' in position:
                for season in all_rushing_data:
                    for player in season:
                        if name in player:
                            stats.append(player)

            elif 'WR' in position:
                for season in all_receiving_data:
                    for player in season:
                        if name in player:
                            stats.append(player)

            else:
                continue

            if len(stats) == 0:
                continue

            new_player = Player(name, name_id, position, draft_round, draft_pick, college, draft_year, stats)
            players.append(new_player)

    return players

if __name__ == '__main__':
    make_combine_table()
    names_with_keys = insert_combine_data()
    crawl_draft_data()
    crawl_passing_data()
    crawl_rushing_data()
    crawl_receiving_data()
    players = initialize_player_data(names_with_keys)
    for player in players:
        print(player)
