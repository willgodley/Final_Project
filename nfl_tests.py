import unittest
from nfl import *

class TestPlayerClass(unittest.TestCase):

    def testInit(self):
        names_with_keys = insert_draft_data()
        players = initialize_player_data(names_with_keys)
        round_num = 0
        for player in players:
            if round_num == 3:
                player_instance1 = player
            elif round_num == 115:
                player_instance2 = player
            elif round_num == 215:
                player_instance3 = player
                break
            round_num += 1

        print(player_instance1)
        print(player_instance2)
        print(player_instance3)

        assert(round_num == 215)

    def testStr(self):
        pass

    def testComputeStats(self):
        pass

class TestDraftCommand(unittest.TestCase):
    pass

class TestStudsCommand(unittest.TestCase):
    pass

class TestSuccessCommand(unittest.TestCase):
    pass

class TestPreparednessCommand(unittest.TestCase):
    pass 

unittest.main()
