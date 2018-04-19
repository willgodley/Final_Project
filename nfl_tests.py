import unittest
from nfl import *

class TestPlayerClass(unittest.TestCase):

    def testInit(self):

        round_num = 1
        for player in PLAYERS:
            if round_num == 1:
                player_instance1 = player
            if round_num == 362:
                player_instance2 = player
            if round_num == 699:
                player_instance3 = player
                break
            round_num += 1

        assert(player_instance1.name == "Michael Vick")
        assert(player_instance1.name_id == 1)
        assert(player_instance1.position == "QB")
        assert(player_instance1.round == "1")
        assert(player_instance1.pick == "1")
        assert(player_instance1.college == "Virginia Tech")
        assert(player_instance1.draft_year == "2001")
        assert(player_instance1.avg_yards == 1728.0)
        assert(player_instance1.avg_td == 10.2)
        assert(player_instance1.preparedness == .499)
        assert(player_instance2.avg_yards == 872.7)
        assert(player_instance2.avg_td ==7.0)
        assert(player_instance2.preparedness == .688)
        assert(player_instance3.avg_yards == 959.0)
        assert(player_instance3.avg_td == 10.0)
        assert(player_instance3.preparedness == .777)

    def testStr(self):
        round_num = 0
        for player in PLAYERS:
            if round_num == 3:
                player_instance1 = player
            if round_num == 115:
                player_instance2 = player
            if round_num == 215:
                player_instance3 = player
                break
            round_num += 1

        str1 = "Rod Gardner (WR) was drafted in round 1, 15 overall in 2001. "
        str1 += "He averaged 527.5 yards and 3.8 TDs in a season in the 2001-2015 seasons. "
        str1 += "He went to Clemson and had a preparedness score of 0.552."
        str2 = "Dave Ragone (QB) was drafted in round 3, 88 overall in 2003. "
        str2 += "He averaged 135.0 yards and 0.0 TDs in a season in the 2001-2015 seasons. "
        str2 += "He went to Louisville and had a preparedness score of 0.225."
        str3 = "Roscoe Parrish (WR) was drafted in round 2, 55 overall in 2005. "
        str3 += "He averaged 214.5 yards and 1.0 TDs in a season in the 2001-2015 seasons. "
        str3 += "He went to Miami (FL) and had a preparedness score of 0.349."
        assert(player_instance1.__str__() == str1)
        assert(player_instance2.__str__() == str2)
        assert(player_instance3.__str__() == str3)


class TestDraftCommand(unittest.TestCase):

    def testDraftCommand(self):
        colleges_test = top_colleges_command()

        college1 = colleges_test[0][0]
        college_count1 = colleges_test[0][1]
        college2 = colleges_test[4][0]
        college_count2 = colleges_test[4][1]
        college3 = colleges_test[10][0]
        college_count3 = colleges_test[10][1]

        assert(college1 == "Ohio St.")
        assert(college2 == "LSU")
        assert(college3 == "Average of all other schools")
        print(college_count1)
        assert(college_count1 == 90)
        assert(college_count2 == 87)
        assert(college_count3 == 11.29)

class TestStudsCommand(unittest.TestCase):

    def testStudsDefault(self):
        results = studs_command("studs")
        studs = results[0]
        success = results[1]
        busts = results[2]
        school = results[3]
        assert(school == 'all')
        assert(studs == 114)
        assert(success == 162)
        assert(busts == 503)

    def testStudsMichigan(self):
        results1 = studs_command("studs Michigan")
        studs1 = results1[0]
        success1 = results1[1]
        busts1 = results1[2]
        school1 = results1[3]
        assert(school1 == 'Michigan')
        assert(studs1 == 0)
        assert(success1 == 6)
        assert(busts1 == 8)

    def testStudsAlabama(self):
        results2 = studs_command("studs Alabama ")
        studs2 = results2[0]
        success2 = results2[1]
        busts2 = results2[2]
        school2 = results2[3]
        assert(school2 == 'Alabama')
        assert(studs2 == 4)
        assert(success2 == 2)
        assert(busts2 == 9)

    def testStudsBadSchool(self):
        results3 = studs_command("studs dfsf")
        assert(results3 is None)

class TestSuccessCommand(unittest.TestCase):

    def testSuccessDefault(self):
        results1 = success_command("success")

        draft_round_data1 = results1[0]
        avg_yards_data1 = results1[1]

        assert(results1[2] == 'QB')
        assert(draft_round_data1[1] == 2)
        assert(draft_round_data1[27] == 6)
        assert(avg_yards_data1[1] == 4060.2)
        assert(avg_yards_data1[27] == 49.0)

    def testSuccessWR(self):
        results2 = success_command("success wr")

        draft_round_data2 = results2[0]
        avg_yards_data2 = results2[1]

        assert(results2[2].upper() == 'WR')
        assert(draft_round_data2[12] == 4)
        assert(draft_round_data2[0] == 1)
        assert(avg_yards_data2[12] == 69.0)
        assert(avg_yards_data2[0] == 400.5)

    def testSuccessRB(self):
        results3 = success_command("success RB")

        draft_round_data3 = results3[0]
        avg_yards_data3 = results3[1]

        assert(results3[2] == 'RB')
        assert(draft_round_data3[10] == 4)
        assert(draft_round_data3[40] == 6)
        assert(avg_yards_data3[10] == 420.5)
        assert(avg_yards_data3[40] == 122.0)

class TestPreparednessCommand(unittest.TestCase):

    def testPreparedness(self):
        results = preparedness_command()

        schools = results[0]
        prep_scores = results[1]

        assert(schools[1] == 'Florida International')
        assert(schools[7] == 'Vanderbilt')
        assert(schools[9] == 'Baylor')
        assert(prep_scores[1] == 0.702)
        assert(prep_scores[7] == 0.539)
        assert(prep_scores[9] == 0.52125)

unittest.main()
