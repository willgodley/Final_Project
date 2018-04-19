##########################################
####   Interactive NFL Data Program   ####
##########################################
###########    Will Godley    ############
##########################################

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~Getting Started/Data Gathering~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

My source for both draft and NFL season statistical data is:
https://www.pro-football-reference.com/

Specifically, my crawling for data begins at:

DRAFT
https://www.pro-football-reference.com/years/2011/draft.htm

PASSING STATS
https://www.pro-football-reference.com/years/2011/passing.htm

RUSHING STATS
https://www.pro-football-reference.com/years/2011/rushing.htm

RECEIVING STATS
https://www.pro-football-reference.com/years/2011/receiving.htm

From those links, I scrape from years 2001 to 2015 using the link found in
the "Next Season" button in the html file. Because I am scraping, no keys
are needed, but you must have installed Requests and BeautifulSoup4
on your computer. You also need to have SQLite3 installed on your computer.
The following are the commands that you enter into terminal to install.

You must then create a username and an api key for plotly. On the website,
https://plot.ly/python/getting-started/, you can create a free account and
get an api key. You will then need to create a file named secrets.py,
that will be formated as:

plotly_key = 'your key'
plotly_username = 'your username'

Additionally, I used a CSV file [from http://nflsavant.com/about.php].
It is already in my github repository, but to get it, just click the link
'1999 to 2015 Combine Data', located under 'Other Data Sets'.
My program gets the combine data from 2001-2015 and inserts it into a table of
my database, but I do not work with it further.


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~Code Structure~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

The most important parts of my code are the data crawling, inserting, and
pulling from database functions, as well as my Player class.

My 4 crawling functions, crawl_draft_data, crawl_passing_data,
crawl_rushing_data, and crawl_receiving_data are all self explanatory
for what they do. They crawl different parts of pro-football-reference.com.
Their code is pretty repetitive, but I did this because the different
tables had a few different attributes and I wanted to keep the data separated.
This is also why I cached the dictionaries that I got from the data separately.

Next are my insertion functions. insert_draft_data is used to parse through
all the tables that I got back from the website and create a dictionary, which
has lists of lists as its values. This is then inserted into the table,
Draft. The attributes for each of these rows are name, position, college,
draft_pick, draft_round, and year drafted. insert_nfl_data uses the player class
to combine some of the draft data with the statistics gathered for each player.
In this function, player instances are created using name, name id (which is
based off of the primary id for the draft table, linked by player name),
position, college, draft year, as well as a list of lists containing yardage
and touchdown totals from scraped data. The data from the player class is then
inserted into the NFL player table.

The Player class does a significant amount of computations in relation to the
grand scheme of the program. The two class functions that aren't init and str are
compute_stats and get_prep_score. compute_stats takes the list of lists to
average out all the yardage and touchdown totals over the seasons that were
scraped for each player. get_prep_score uses these totals, along with draft round
to compute a score of how well a college prepared a player. A perfect score
would be at or slightly above 1, which only one player, Odell Beckham has (1.009).
It is decided by adding 30% of the score from draft position divided by total possible draft points (first round -> 7 points -> 7/7 = 1 -> 1*.3 = .3, seventh round -> 1 point, and 40% of A player’s average yards per season from the 2011 to 2015 seasons divided by extremely good seasonal yardage totals. For quarterbacks, it will be 5,000, and 1,000 for wide receivers and running backs. It will also include 30% from average TDs over those seasons, divided by 50 for QBs and 15 for WRs and RBs.

* Note: insert_combine_data uses the csv to insert name, name_id, position, college,
forty time, nfl grade, and year to the

Little data manipulation happens in the command functions, where I make SQL
calls to my database.  
    In top_colleges_command, the get_colleges function is used to get
all colleges and their number of draft picks. I then parse this list of tuples
into one of the top 10, and one with all the rest. I then average all the
other schools, and use that value as the 11th portion of my pie chart.
    In the studs_command, I grab position along with average yards and tds
for all players from a specific school, or all schools. If it is one school,
the get_colleges function is usedto make sure that the school the user enters has sent a
player to the draft during the years that I scraped by ensuring one school
is returned. I then accumulate the number of studs, successful players,
and busts based on the player's avg yards and tds. For a QB, they must
average at least 3200 yards or 20 tds to be considered a stud, and 2000
yards or 10 tds to be successful. Otherwise they are a bust. For WRs and RBs,
if they average 700 yards or 7 tds, they're a stud. They need to average 400 yards or 3 tds to be successful, or they are a bust. I use these 3 accumulated numbers
to make a bar graph.
    In the success_command, I use the SQL statement to get the draft round and
average yards for all players at a specified position. I use this data to make a
scatter plot.
    In the preparedness_command, I use my statement to get the top 10 schools
and their average preparedness score, ranking them by highest score. I use
the returned data to form a bar chart. 



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~User Guide~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

To run the program, clone my git repository to a local repo. Then, navigate
to that repository in terminal and create the secrets.py file as
described before, then use the following command in your command line:

python3 nfl.py

Once the program is running, for an in depth description
of the commands for visualizations, please use the 'help' command.

Quit the program using 'exit'
