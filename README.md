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

From those links, I scrape from years 2011 to 2015 using the link found in
the "Next Season" button in the html file. Because I am scraping, no keys
are needed, but you must have installed Requests and BeautifulSoup4
on your computer. You also need to have SQLite3 installed on your computer.
The following are the commands that you enter into terminal to install.

Install Requests:
    pip3 install requests

Install BeautifulSoup:
    pip3 install beautifulsoup4

To install SQLite on your computer:
    Go to https://www.sqlite.org/download.html and download the version for your OS

To install plotly (for visualizations):
    pip3 install plotly

You must then create a username and an api key for plotly. On the website,
https://plot.ly/python/getting-started/, you can create a free account and
get an api key. You will then need to create a file named secrets.py,
that will be formated as:

plotly_key = 'your key'
plotly_username = 'your username'


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~Code Structure~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~User Guide~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

To run the program, clone my git repository, create the secrets.py file as
described before, then use the following command in your command line:

python3 nfl.py

Once the program is running, there are two commands that can help you work
with the interactive prompts. One is 'help', which will print the available
commands for creating each visualization. You can also type 'colleges' to
print out a list of all colleges that have sent a player to the NFL draft
in the years 2011-2015. This is useful for adding a college to the 'studs'
command. Because this command only uses data from QB, WR, and RB positions,
some of the schools that are printed by the 'colleges' command may not have
sent players of those positions, and a graph won't be created.

For an in depth description of the commands for visualizations, please use the
'help' command.
