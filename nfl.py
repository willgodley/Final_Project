import csv
import requests
import json
import sqlite3 as sqlite
from bs4 import BeautifulSoup

COMBINE_CSV = 'combine.csv'
DB_NAME = 'nfl.db'

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
        self.preparedness = self.get_prep_score()

    def __str__(self):
        return "{} ({}) was drafted in round {}, {} overall in {}. He averaged {} yards and {} TDs in a season in the 2011-2015 seasons. He went to {}.".format(self.name, self.position, self.round, self.pick, self.draft_year, self.avg_yards, self.avg_td, self.college)

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

        avg_yards = total_yards / total_years
        avg_yards_str = str(avg_yards)
        yards_split = avg_yards_str.split('.')
        yards = yards_split[0]
        yards_decimal = yards_split[1][0]
        avg_yards = float(yards + '.' + yards_decimal)

        avg_td = total_td / total_years
        avg_td_str = str(avg_td)
        td_split = avg_td_str.split('.')
        tds = td_split[0]
        tds_decimal = td_split[1][0]
        avg_td = float(tds + '.' + tds_decimal)

        return(avg_yards, avg_td)

    def get_prep_score(self):
        if int(self.round) == 1:
            score = 7
        elif int(self.round) == 2:
            score = 6
        elif int(self.round) == 3:
            score = 5
        elif int(self.round) == 4:
            score = 4
        elif int(self.round) == 5:
            score = 3
        elif int(self.round) == 6:
            score = 2
        elif int(self.round) == 7:
            score = 1

        yds = self.avg_yards
        td = self.avg_td

        if self.position == 'QB':
            preparedness = .3 * (score / 7) + .4 * (yds / 5000) + .3 * (td / 50)
            preparedness = round(preparedness, 3)

        elif self.position == 'RB' or self.position == "WR":
            preparedness = .3 * (score / 7) + .4 * (yds / 1200) + .3 * (td / 15)
            preparedness = round(preparedness, 3)

        return preparedness


def make_combine_table():
    statement = "DROP TABLE IF EXISTS 'Combine'"
    cur.execute(statement)

    # Create new Combine table
    statement = """
        CREATE TABLE 'Combine' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Name' TEXT NOT NULL,
          'Position' TEXT NOT NULL,
          'College' TEXT NOT NULL,
          'FortyTime' FLOAT NOT NULL,
          'NflGrade' FLOAT NOT NULL,
          'Year' INTEGER NOT NULL
        );
        """
    cur.execute(statement)

def make_draft_table():

    statement = "DROP TABLE IF EXISTS 'Draft'"
    cur.execute(statement)

    # Create new Combine table
    statement = """
        CREATE TABLE 'Draft' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Name' TEXT NOT NULL,
          'NameID' TEXT NOT NULL,
          'Position' TEXT NOT NULL,
          'College' TEXT NOT NULL,
          'Pick' INTEGER NOT NULL,
          'Round' INTEGER NOT NULL
        );
        """
    cur.execute(statement)


def make_NFL_table():
    statement = "DROP TABLE IF EXISTS 'NFLPlayer'"
    cur.execute(statement)

    # Create new NFLPlayer table
    statement = """
        CREATE TABLE 'NFLPlayer' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Name' TEXT NOT NULL,
          'NameId' INTEGER,
          'Position' TEXT NOT NULL,
          'YearDrafted' INTEGER NOT NULL,
          'College' TEXT NOT NULL,
          'AvgYards' FLOAT NOT NULL,
          'AvgTD' FLOAT NOT NULL,
          'Preparedness' FLOAT NOT NULL
        );
        """
    cur.execute(statement)

def insert_combine_data():

    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

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

            # Only insert combine data from QB, WR, and RB
            if position == "QB" or position == "WR" or position == "RB":
                pass
            else:
                continue

            college = player[20]
            forty = player[11]
            nfl_grade = player[25]
            year = player[0]

            # Stop inserting any data before the 2010 season
            if year == '2010':
                break

            names_and_keys[name] = round_num

            insertion = (None, name, position, college, forty, nfl_grade, year)
            statement = 'INSERT INTO "Combine" '
            statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)

            round_num += 1

    # Commit changes and close database connection
    conn.commit()

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
    first_draft_url = '/years/2011/draft.htm'
    full_url = base_url + first_draft_url

    year = 2011
    while year < 2016:
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
                        cell_str = cell.text.strip()
                        if "*" in cell_str:
                            fixed_cell = cell_str.replace('*', '')
                            if '+' in fixed_cell:
                                fixed_cell = fixed_cell.replace('+', '')
                            cells.append(fixed_cell)
                        elif '+' in cell_str:
                            fixed_cell = cell_str.replace('+', '')
                            cells.append(fixed_cell)
                        else:
                            cells.append(cell_str)
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
    first_draft_url = '/years/2011/passing.htm'
    full_url = base_url + first_draft_url

    #passer stats
    year = 2010
    while year < 2016:
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
                        cell_str = cell.text.strip()
                        if "*" in cell_str:
                            fixed_cell = cell_str.replace('*', '')
                            if '+' in fixed_cell:
                                fixed_cell = fixed_cell.replace('+', '')
                            cells.append(fixed_cell)
                        elif '+' in cell_str:
                            fixed_cell = cell_str.replace('+', '')
                            cells.append(fixed_cell)
                        else:
                            cells.append(cell_str)
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
    first_draft_url = '/years/2011/rushing.htm'
    full_url = base_url + first_draft_url

    #passer stats
    year = 2011
    while year < 2016:
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
                        cell_str = cell.text.strip()
                        if "*" in cell_str:
                            fixed_cell = cell_str.replace('*', '')
                            if '+' in fixed_cell:
                                fixed_cell = fixed_cell.replace('+', '')
                            cells.append(fixed_cell)
                        elif '+' in cell_str:
                            fixed_cell = cell_str.replace('+', '')
                            cells.append(fixed_cell)
                        else:
                            cells.append(cell_str)
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
    first_draft_url = '/years/2011/receiving.htm'
    full_url = base_url + first_draft_url

    #passer stats
    year = 2011
    while year < 2016:
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
                        cell_str = cell.text.strip()
                        if "*" in cell_str:
                            fixed_cell = cell_str.replace('*', '')
                            if '+' in fixed_cell:
                                fixed_cell = fixed_cell.replace('+', '')
                            cells.append(fixed_cell)
                        elif '+' in cell_str:
                            fixed_cell = cell_str.replace('+', '')
                            cells.append(fixed_cell)
                        else:
                            cells.append(cell_str)
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

def insert_draft_data(foreign_keys_dict):
    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    data_cache_name = 'raw_data.json'
    data_dict = cacheOpen(data_cache_name)
    draft_data = []
    for key in data_dict.keys():
        if "draft" in key:
            draft_data.append(data_dict[key])

    for draft in draft_data:
        for player in draft:
            name = player[3]
            if name == "Player":
                continue
            position = player[4]
            college = player[27]
            draft_pick = player[1]
            draft_round = player[0]

            if name in foreign_keys_dict:
                name_id = foreign_keys_dict[name]
            else:
                continue

            insertion = (None, name, name_id, position, college, draft_pick, draft_round)
            statement = 'INSERT INTO "Draft" '
            statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)

            conn.commit()

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
            else:
                continue

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


def insert_nfl_data(players):

    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    for player in players:

        name = player.name
        name_id = player.name_id
        pos = player.position
        rnd = player.round
        pick = player.pick
        draft_yr = player.draft_year
        college = player.college
        if "A&M" in college:
            college = college[:-1]
        yards = player.avg_yards
        td = player.avg_td
        prep = player.preparedness

        insertion = (None, name, name_id, pos, draft_yr, college, yards, td, prep)
        statement = 'INSERT INTO "NFLPlayer" '
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)

        conn.commit()

def get_colleges(kind):
    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    all_colleges_statement = "SELECT College FROM Draft"

    cur.execute(all_colleges_statement)
    conn.commit()

    all_colleges = []
    if kind == 'all':
        for college in cur:
            if college[0].strip() == '':
                continue
            all_colleges.append(college[0])
    elif kind == 'single':
        for college in cur:
            if college[0] not in all_colleges:
                if college[0].strip() == '':
                    continue
                all_colleges.append(college[0])

    return all_colleges

def top_colleges_command():

    colleges = get_colleges("all")

    college_count = {}

    for college in colleges:
        if college not in college_count:
            college_count[college] = 0
        college_count[college] += 1

    sorted_colleges = sorted(college_count.items(), key = lambda x: x[1], reverse = True)
    top_colleges = sorted_colleges[:10]
    all_other_colleges = sorted_colleges[10:]
    all_other_count = 0
    total_colleges = 0
    for college in all_other_colleges:
        all_other_count += college[1]
        total_colleges += 1
    avg = all_other_count/total_colleges
    other = ('Average of all other schools', round(avg, 2))
    top_colleges.append(other)

    print(top_colleges)

    # MAKE PLOT FROM HERE


def NFL_grade_command(command):

    school = command.split()[1]

    colleges = get_colleges("single")

    good_college = False
    for university in colleges:
        if university == school:
            good_college = True

    if good_college == False:
        print("This school has not sent any players to the 2011-2015 drafts")
        return

    picks_statement = "SELECT Position, College, AvgYards, AvgTD FROM NFLPlayer"
    cur.execute(picks_statement)
    conn.commit()

    studs = 0
    successful = 0
    busts = 0

    for player in cur:
        if school == str(player[1]):
            if player[0] == 'QB':
                if float(player[2]) >= 3200.0 or float(player[3]) >= 20.0:
                    studs += 1
                elif float(player[2]) >= 2000.0 or float(player[3]) >= 10.0:
                    successful += 1
                else:
                    busts += 1
            else:
                if float(player[2]) >= 700.0 or float(player[3]) >= 7.0:
                    studs += 1
                elif float(player[2]) >= 400.0 or float(player[3]) >= 3.0:
                    successful += 1
                else:
                    busts += 1

    if studs == 0 and successful == 0 and busts == 0:
        print("No player from this school has accumulated offensive stats in the 2011-2015 seasons")
        return

    print("Studs: {}. Successful: {}. Busts {}.".format(studs, successful, busts))

    # DO PLOTLY STUFF

def draft_round_command(command):

    position = command.split()[1]
    if position.upper() == "QB" or position.upper() == "WR" or position.upper() == "RB":
        pass
    else:
        print("Not a valid position. Use 'QB', 'WR', or 'RB'.")
        return

    draft_statement = "SELECT Round, AvgYards FROM NFLPlayer "
    draft_statement += "JOIN Draft on NFLPlayer.NameId = Draft.NameID "
    draft_statement += "WHERE NFLPlayer.Position = '{}'".format(position)
    cur.execute(draft_statement)
    conn.commit()

    average_yards_and_round = []
    for player in cur:
        pair = (player[0], player[1])
        average_yards_and_round.append(pair)

    print(average_yards_and_round)

    # PLOTY

def preparedness_command(command):

    prep_statement = "SELECT College, AVG(Preparedness) FROM NFLPlayer "
    prep_statement += "GROUP BY College ORDER BY AVG(Preparedness) "
    prep_statement += "DESC LIMIT 10"
    cur.execute(prep_statement)
    conn.commit()

    for a in cur:
        print(a)

def handle_command(command):

    if command.lower() == "draft":
        top_colleges_command()

    elif "studs" in command.lower():
        NFL_grade_command(command)

    elif "success" in command.lower():
        draft_round_command(command)

    elif command.lower() == "preparedness":
        preparedness_command(command)

    else:
        print()
        print("Invalid command.")


def interactive_prompt():
    help_text = load_help_text()
    colleges_text = load_colleges_text()
    command = ''

    print()
    print("Type 'help' for list of commands.")
    print("Type 'colleges' for list of colleges that have sent players to the 2011-2015 drafts.")
    while command != 'exit':

        print()
        command = input("Enter a command: ")

        if command.lower() == 'exit':
            print("Bye!")
            continue

        elif command.lower() == 'help':
            print(help_text)
            continue

        elif command.lower() == 'colleges':
            print(colleges_text)
            continue

        else:
            handle_command(command)

def load_help_text():
    with open('help.txt') as f:
        return f.read()

def load_colleges_text():
    with open('colleges.txt') as f:
        return f.read()

if __name__ == '__main__':
    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    # Initializing functions
    make_combine_table()
    make_draft_table()
    make_NFL_table()
    names_with_keys = insert_combine_data()
    crawl_draft_data()
    crawl_passing_data()
    crawl_rushing_data()
    crawl_receiving_data()
    players = initialize_player_data(names_with_keys)
    insert_nfl_data(players)
    insert_draft_data(names_with_keys)

    # Interactive prompt
    interactive_prompt()

    # Commit any changes and close connection to database
    conn.commit()
    conn.close()
