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
