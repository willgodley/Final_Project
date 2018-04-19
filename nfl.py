import csv
import requests
import json
import sqlite3 as sqlite
from bs4 import BeautifulSoup
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from secrets import *

plotly.tools.set_credentials_file(username=plotly_username, api_key=plotly_key)

COMBINE_CSV = 'combine.csv'
DB_NAME = 'nfl.db'

class Player():

    def __init__(self, nm, n_id, ps, round_num, pick, clg, draft_yr, stats):
        self.name = nm
        self.name_id = n_id
        self.position = ps
        self.round = round_num
        self.pick = pick
        self.college = clg
        self.draft_year = draft_yr.split()[0]
        self.avg_yards = self.compute_stats(stats)[0]
        self.avg_td = self.compute_stats(stats)[1]
        self.preparedness = self.get_prep_score()

    def __str__(self):
        player_str = "{} ({}) was drafted in round {}, ".format(self.name, self.position, self.round)
        player_str += "{} overall in {}. ".format(self.pick, self.draft_year)
        player_str += "He averaged {} yards and {} ".format(self.avg_yards, self.avg_td)
        player_str += "TDs in a season in the 2001-2015 seasons. "
        player_str += "He went to {} ".format(self.college)
        player_str += "and had a preparedness score of {}.".format(self.preparedness)
        return player_str

    def compute_stats(self, stats):
        total_yards = 0
        total_td = 0
        total_years = len(stats)

        for year in stats:
            total_yards += int(year[0])
            total_td += int(year[1])

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


# TABLE SECTION

def make_draft_table():
    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    statement = "DROP TABLE IF EXISTS 'Draft'"
    cur.execute(statement)

    # Create new Combine table
    statement = """
        CREATE TABLE 'Draft' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Name' TEXT NOT NULL,
          'Position' TEXT NOT NULL,
          'College' TEXT NOT NULL,
          'Pick' INTEGER NOT NULL,
          'Round' INTEGER NOT NULL,
          'DraftYear' INTEGER NOT NULL
        );
        """
    cur.execute(statement)

def make_combine_table():
    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    statement = "DROP TABLE IF EXISTS 'Combine'"
    cur.execute(statement)

    # Create new Combine table
    statement = """
        CREATE TABLE 'Combine' (
          'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
          'Name' TEXT NOT NULL,
          'NameID' TEXT,
          'Position' TEXT NOT NULL,
          'College' TEXT NOT NULL,
          'FortyTime' FLOAT NOT NULL,
          'NflGrade' FLOAT NOT NULL,
          'Year' INTEGER NOT NULL
        );
        """
    cur.execute(statement)

def make_NFL_table():
    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

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


# CACHING

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

# CRAWLING PRO FOOTBALL REFERENCE

def crawl_draft_data():
    players = []
    table_contents = []
    page_cache_name = 'draft.json'
    raw_data_cache = 'draft_data.json'

    base_url = 'https://www.pro-football-reference.com'
    first_draft_url = '/years/2001/draft.htm'
    full_url = base_url + first_draft_url

    year = 2001
    while year < 2016:
        draft_cache = cacheOpen(page_cache_name)

        if full_url in draft_cache:
            page_text = draft_cache[full_url]
        else:
            page_resp = requests.get(full_url)
            page_text = page_resp.text
            draft_cache[full_url] = page_text
            cacheWrite(page_cache_name, draft_cache)

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
            current_year_draft = draft_data
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
                    cells.append(year)
                    current_year_draft.append(cells)

        raw_data_dict[key] = current_year_draft
        cacheWrite(raw_data_cache, raw_data_dict)

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])

def crawl_passing_data():
    passer_stats = []
    table_contents = []
    page_cache_name = 'stats.json'
    raw_data_cache = 'passing_data.json'

    base_url = 'https://www.pro-football-reference.com'
    first_draft_url = '/years/2001/passing.htm'
    full_url = base_url + first_draft_url

    # passer stats
    year = 2001
    while year < 2016:
        stats_cache = cacheOpen(page_cache_name)

        if full_url in stats_cache:
            page_text = stats_cache[full_url]
        else:
            page_resp = requests.get(full_url)
            page_text = page_resp.text
            stats_cache[full_url] = page_text
            cacheWrite(page_cache_name, stats_cache)

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
            current_year_stats = passing_data
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
                    current_year_stats.append(cells)

        raw_data_dict[key] = current_year_stats
        cacheWrite(raw_data_cache, raw_data_dict)

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])

def crawl_rushing_data():
    rushing_stats = []
    table_contents = []
    page_cache_name = 'stats.json'
    raw_data_cache = 'rushing_data.json'

    base_url = 'https://www.pro-football-reference.com'
    first_draft_url = '/years/2001/rushing.htm'
    full_url = base_url + first_draft_url

    #passer stats
    year = 2001
    while year < 2016:
        stats_cache = cacheOpen(page_cache_name)

        if full_url in stats_cache:
            page_text = stats_cache[full_url]
        else:
            page_resp = requests.get(full_url)
            page_text = page_resp.text
            stats_cache[full_url] = page_text
            cacheWrite(page_cache_name, stats_cache)

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
            current_year_stats = rushing_data
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

        raw_data_dict[key] = current_year_stats
        cacheWrite(raw_data_cache, raw_data_dict)

        full_url = next_url
        split_url = full_url.split('/')
        year = int(split_url[4])

def crawl_receiving_data():
    receiving_stats = []
    table_contents = []
    page_cache_name = 'stats.json'
    raw_data_cache = 'receiving_data.json'

    base_url = 'https://www.pro-football-reference.com'
    first_draft_url = '/years/2001/receiving.htm'
    full_url = base_url + first_draft_url

    #passer stats
    year = 2001
    while year < 2016:
        stats_cache = cacheOpen(page_cache_name)

        if full_url in stats_cache:
            page_text = stats_cache[full_url]
        else:
            page_resp = requests.get(full_url)
            page_text = page_resp.text
            stats_cache[full_url] = page_text
            cacheWrite(page_cache_name, stats_cache)

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
            current_year_stats = receiving_data
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


# INSERTING DATA INTO TABLES

def insert_draft_data():
    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    draft_cache_name = 'draft_data.json'
    draft_data_dict = cacheOpen(draft_cache_name)

    player_id = 1
    names_and_keys_dict = {}
    for draft_year in draft_data_dict.keys():
        for player in draft_data_dict[draft_year]:
            name = player[3]
            if name == "Player":
                continue
            position = player[4]
            draft_pick = player[1]
            draft_round = player[0]
            college = player[27]
            year = player[29]

            names_and_keys_dict[name] = player_id
            player_id += 1

            insertion = (None, name, position, college, draft_pick, draft_round, year)
            statement = 'INSERT INTO "Draft" '
            statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)

            conn.commit()

    return names_and_keys_dict

def insert_combine_data(foreign_keys_dict):

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

            if name in foreign_keys_dict:
                name_id = foreign_keys_dict[name]
            else:
                continue

            college = player[20]
            forty = player[11]
            nfl_grade = player[25]
            year = player[0]

            names_and_keys[name] = round_num

            insertion = (None, name, name_id, position, college, forty, nfl_grade, year)
            statement = 'INSERT INTO "Combine" '
            statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)

            round_num += 1

    # Commit changes and close database connection
    conn.commit()


# INITIALIZE PLAYER CLASSES TO BE INSERTED INTO NFLPlayer TABLE

def initialize_player_data(foreign_keys_dict):
    draft_data_cache = 'draft_data.json'
    draft_dict = cacheOpen(draft_data_cache)
    rushing_data_cache = 'rushing_data.json'
    rushing_dict = cacheOpen(rushing_data_cache)
    receiving_data_cache = 'receiving_data.json'
    receiving_dict = cacheOpen(receiving_data_cache)
    passing_data_cache = 'passing_data.json'
    passing_dict = cacheOpen(passing_data_cache)
    players = []

    for draft_year in draft_dict.keys():
        for player_drafted in draft_dict[draft_year]:
            stats = []
            draft_round = player_drafted[0]
            draft_pick = player_drafted[1]
            name = player_drafted[3]
            position = player_drafted[4]
            # Only initialize players who are QB, WR, or RB
            player_stats = []
            if 'QB' in position:
                for season in passing_dict:
                    for player in passing_dict[season]:
                        if name in player:
                            yards = int(player[11])
                            tds = int(player[12])
                            yards_and_tds = (yards, tds)
                            player_stats.append(yards_and_tds)

            elif 'RB' in position:
                for season in rushing_dict:
                    for player in rushing_dict[season]:
                        if name in player:
                            yards = int(player[8])
                            tds = int(player[9])
                            yards_and_tds = (yards, tds)
                            player_stats.append(yards_and_tds)

            elif 'WR' in position:
                for season in receiving_dict:
                    for player in receiving_dict[season]:
                        if name in player:
                            yards = int(player[10])
                            tds = int(player[12])
                            yards_and_tds = (yards, tds)
                            player_stats.append(yards_and_tds)
            else:
                continue
            year_drafted = player_drafted[29]
            college = player_drafted[27]

            # Remove players who didn't participate in combine
            if name in foreign_keys_dict:
                name_id = foreign_keys_dict[name]
            else:
                continue

            if len(player_stats) == 0:
                continue

            # Did this to shorten Player initialization line
            a = name
            b = name_id
            c = position
            d = draft_round
            e = draft_pick
            f = college
            g = draft_year
            h = player_stats
            new_player = Player(a, b, c, d, e, f, g, h)
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

# USED TO GET LIST OF COLLEGES AND THEIR TOTAL NUMBER OF DRAFT PICKS,
# EITHER ALL OR A SINGLE COLLEGE
def get_colleges(kind, school=''):
    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    all_colleges_statement = "SELECT College, COUNT(*) FROM Draft "

    all_colleges = []

    if kind == 'single':
        all_colleges_statement += "WHERE College = '{}'".format(school)
    elif kind == 'all':
        all_colleges_statement += "GROUP BY College"

    cur.execute(all_colleges_statement)
    conn.commit()

    for pair in cur:
        all_colleges.append(pair)

    return all_colleges


# DIFFERENT COMMAND FUNCTIONS THAT COLLECT DATA AND LAUNCH PLOTLY GRAPHS

def top_colleges_command():

    colleges = get_colleges("all")

    sorted_colleges = sorted(colleges, key = lambda x: int(x[1]), reverse = True)
    top_colleges = sorted_colleges[:10]
    all_other_colleges = sorted_colleges[10:]
    all_other_count = 0
    total_colleges = 0
    for college in all_other_colleges:
        all_other_count += int(college[1])
        total_colleges += 1
    avg = all_other_count/total_colleges
    other = ('Average of all other schools', round(avg, 2))
    top_colleges.append(other)

    return top_colleges

def top_colleges_graph(best_colleges):
    labels = []
    values = []

    for college in best_colleges:
        labels.append(college[0])
        values.append(college[1])

    fig = {
        "data": [
            {
          "values": values,
          "labels": labels,
          "name": "Number of Draft Picks",
          "hoverinfo":"label+name+value",
          "type": "pie"
        }],
        "layout": {
            "title":"Top 10 Colleges For Number of Players Drafted"
            }
    }
    py.plot(fig, filename = 'Top 10 Colleges')

def studs_command(command):

    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    try:
        school = command.split()[1]
    except:
        school = 'all'

    if school.lower() != "all":
        colleges = get_colleges("single", school)
        good_college = False
        for university in colleges:
            if university[0] == school:
                good_college = True

        if good_college == False:
            print("{} has not sent any players to the 2001-2015 drafts".format(school))
            return

        picks_statement = "SELECT Position, AvgYards, AvgTD FROM NFLPlayer "
        picks_statement += "WHERE College = '{}'".format(school)
        cur.execute(picks_statement)
        conn.commit()

    else:

        picks_statement = "SELECT Position, AvgYards, AvgTD FROM NFLPlayer"
        cur.execute(picks_statement)
        conn.commit()

    studs = 0
    successful = 0
    busts = 0

    for player in cur:
        if player[0] == 'QB':
            if float(player[1]) >= 3200.0 or float(player[2]) >= 20.0:
                studs += 1
            elif float(player[1]) >= 2000.0 or float(player[2]) >= 10.0:
                successful += 1
            else:
                busts += 1
        else:
            if float(player[1]) >= 700.0 or float(player[2]) >= 7.0:
                studs += 1
            elif float(player[1]) >= 400.0 or float(player[2]) >= 3.0:
                successful += 1
            else:
                busts += 1


    if studs == 0 and successful == 0 and busts == 0:
        print("No player from this school has accumulated offensive stats in the 2001-2015 seasons")
        print("Be sure to capitalize the first letter of the school!")
        return

    return [studs, successful, busts, school]

def studs_graph(studs_data):

    studs = studs_data[0]
    successful = studs_data[1]
    busts = studs_data[2]
    university = studs_data[3]

    # DO PLOTLY STUFF
    data = [go.Bar(
        x=['Studs', 'Successful', 'Busts'],
        y=[studs, successful, busts]
    )]

    if university.lower() == 'all':
        # DO PLOTLY STUFF
        data = [go.Bar(
            x=['Studs', 'Successful', 'Busts'],
            y=[studs, successful, busts],
            name = 'Bar Chart of Stud, Successful, and Bust Players From All Colleges'
        )]
        layout = go.Layout(
            title='Bar Chart of Stud, Successful, and Bust Players From All Colleges',
            xaxis=dict(title=''),yaxis=dict(title='Number Players'))
        fig = go.Figure(data=data, layout=layout)
        py.plot(fig, filename = 'Bar Chart')
    else:
        data = [go.Bar(
            x=['Studs', 'Successful', 'Busts'],
            y=[studs, successful, busts],
            name = 'Bar Chart of Stud, Successful, and Bust Players From {}'.format(university)
        )]
        layout = go.Layout(
            title='Bar Chart of Stud, Successful, and Bust Players From {}'.format(university),
            xaxis=dict(title=''),yaxis=dict(title='Number Players'))
        fig = go.Figure(data=data, layout=layout)
        py.plot(fig, filename = 'Bar Chart')

def success_command(command):

    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    try:
        position = command.split()[1]
    except:
        position = 'QB'

    if position.upper() == "QB" or position.upper() == "WR" or position.upper() == "RB":
        pass
    else:
        print("Not a valid position. Use 'QB', 'WR', or 'RB'.")
        return

    draft_statement = "SELECT Round, AvgYards FROM NFLPlayer "
    draft_statement += "JOIN Draft on NFLPlayer.NameId = Draft.Id "
    draft_statement += "WHERE NFLPlayer.Position = '{}'".format(position.upper())
    cur.execute(draft_statement)
    conn.commit()

    draft_round = []
    avg_yards = []
    success_data = []
    for player in cur:
        draft_round.append(player[0])
        avg_yards.append(player[1])

    success_data.append(draft_round)
    success_data.append(avg_yards)
    success_data.append(position)

    return success_data

def success_graph(success_data):

    draft_round_data = success_data[0]
    avg_yards_data = success_data[1]
    player_position = success_data[2]

    # Create traces
    trace0 = go.Scatter(
        x = draft_round_data,
        y = avg_yards_data,
        mode = 'markers',
        name = 'Scatter Plot of Draft Round vs Avg Yards for {}s'.format(player_position.upper())
    )

    layout = go.Layout(
        title='Scatter Plot of Draft Round vs Avg Yards for {}s'.format(player_position.upper()),
        xaxis=dict(title='Draft Round'),yaxis=dict(title='Average Yards per Season'))

    data = [trace0]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename = 'Scatter Plot')

def preparedness_command():

    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")

    prep_statement = "SELECT College, AVG(Preparedness) FROM NFLPlayer "
    prep_statement += "GROUP BY College ORDER BY AVG(Preparedness) "
    prep_statement += "DESC LIMIT 10"
    cur.execute(prep_statement)
    conn.commit()

    schools = []
    avg_prep = []
    prep_data = []
    for school in cur:
        schools.append(school[0])
        avg_prep.append(school[1])

    prep_data.append(schools)
    prep_data.append(avg_prep)
    return prep_data

def preparedness_graph(preparedness_data):

    school_data = preparedness_data[0]
    avg_data = preparedness_data[1]

    data = [go.Bar(
        x = school_data,
        y = avg_data,
        name = 'Bar Chart of Top 10 Schools for Average Preparedness Score'
    )]

    layout = go.Layout(
        title='Bar Chart of Top 10 Schools for Average Preparedness Score',
        xaxis=dict(title='Schools'),yaxis=dict(title='Preparedness Scale'))

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename = 'Bar Chart')

def handle_command(command):

    if command.lower() == "draft":
        top_colleges_data = top_colleges_command()
        top_colleges_graph(top_colleges_data)

    elif "studs" in command.lower():
        studs_data = studs_command(command)
        if studs_data is None:
            return
        studs_graph(studs_data)

    elif "success" in command.lower():
        success_data = success_command(command)
        if success_data is None:
            return
        success_graph(success_data)

    elif command.lower() == "preparedness":
        prep_data = preparedness_command()
        preparedness_graph(prep_data)

    else:
        print()
        print("Invalid command.")


def interactive_prompt():
    help_text = load_help_text()
    command = ''

    print()
    print("Type 'help' for list of commands.")
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

# Initializing functions, I did this to avoid overpopulating db during testing
make_combine_table()
make_draft_table()
make_NFL_table()
crawl_draft_data()
crawl_passing_data()
crawl_rushing_data()
crawl_receiving_data()
names_with_keys = insert_draft_data()
insert_combine_data(names_with_keys)
PLAYERS = initialize_player_data(names_with_keys)
insert_nfl_data(PLAYERS)

if __name__ == '__main__':
    # Connect to database
    try:
        conn = sqlite.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Error occurred connecting to database")


    # Interactive prompt
    interactive_prompt()

    # Commit any changes and close connection to database
    conn.commit()
    conn.close()
