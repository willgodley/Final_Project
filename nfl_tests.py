import unittest
from nfl import *

class TestPlayerClass(unittest.TestCase):

    def testInit(self):
        # A lot of the stats info doesn't actually matter, so they are just copied
        # These stats are also made up, it just matters that the variables are set correctly
        name1 = "Michael Vick"
        name_id1 = 1
        position1 = "QB"
        d_r1 = 1
        d_p1 = 1
        college1 = "Virginia Tech"
        draft_year1 = 2001
        stats1 = [(3018, 21), (3303, 18)]
        name2 = "Jordy Nelson"
        name_id2 = 1825
        position2 = "WR"
        d_r2 = 2
        d_p2 = 36
        college2 = "Kansas St."
        draft_year2 = 2008
        stats2 = [(1519, 13), (1314, 8)]
        name3 = "Jeremy Hill"
        name_id3 = 3368
        position3 = "RB"
        d_r3 = 2
        d_p3 = 55
        college3 = "LSU"
        draft_year3 = 2014
        stats3 = [(1124, 9), (794, 11), (839, 10)]

        player1 = Player(name1,name_id1,position1,d_r1,d_p1,college1,draft_year1,stats1)
        player2 = Player(name2,name_id2,position2,d_r2,d_p2,college2,draft_year2,stats2)
        player3 = Player(name3,name_id3,position3,d_r3,d_p3,college3,draft_year3,stats3)

        # Many of these don't include computation and will always be true,
        # just making sure they are set correctly in class
        assert(player1.name == "Michael Vick")
        assert(player1.name_id == 1)
        assert(player1.position == "QB")
        assert(player1.round == 1)
        assert(player1.pick == 1)
        assert(player1.college == "Virginia Tech")
        assert(player1.draft_year == 2001)
        assert(player1.avg_yards == 3,160.5)
        assert(player1.avg_td == 19.5)
        assert(player1.preparedness == .67)
        assert(player2.avg_yards == 1,416.5)
        assert(player2.avg_td == 10.5)
        assert(player2.preparedness == .939)
        assert(player3.avg_yards == 919)
        assert(player3.avg_td == 10)
        assert(player3.preparedness == .763)

    def testStr(self):
        names_with_keys = insert_draft_data()
        players = initialize_player_data(names_with_keys)
        round_num = 0
        for player in players:
            if round_num == 3:
                player_instance1 = player
            if round_num == 115:
                player_instance2 = player
            if round_num == 215:
                player_instance3 = player
                break
            round_num += 1

        str1 = "Rod Gardner (WR) was drafted in round 1, 15 overall in 2001 draft. "
        str1 += "He averaged 527.5 yards and 3.8 TDs in a season in the 2001-2015 seasons. "
        str1 += "He went to Clemson and had a preparedness score of 0.552."
        str2 = "Dave Ragone (QB) was drafted in round 3, 88 overall in 2003 draft. "
        str2 += "He averaged 135.0 yards and 0.0 TDs in a season in the 2001-2015 seasons. "
        str2 += "He went to Louisville and had a preparedness score of 0.225."
        str3 = "Roscoe Parrish (WR) was drafted in round 2, 55 overall in 2005 draft. "
        str3 += "He averaged 214.5 yards and 1.0 TDs in a season in the 2001-2015 seasons. "
        str3 += "He went to Miami (FL) and had a preparedness score of 0.349."
        assert(player_instance1.__str__() == str1)
        assert(player_instance2.__str__() == str2)
        assert(player_instance3.__str__() == str3)


class TestDraftCommand(unittest.TestCase):
    pass

class TestStudsCommand(unittest.TestCase):
    pass

class TestSuccessCommand(unittest.TestCase):
    pass

class TestPreparednessCommand(unittest.TestCase):
    pass

unittest.main()
