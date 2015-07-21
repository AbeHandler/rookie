import unittest
import json
import pickle
import pdb
from rookie.utils import calculate_pmi, get_picked
from rookie.scripts.counter3 import mergeable, get_json, compute_jaccard_index


class GenericTestCase(unittest.TestCase):

    def test_aliasing(self):
        one = 'Mayor-elect Mitch Landrieus'
        two = 'Mayor-elect Mitch Landrieu'
        test = mergeable(one, two)  # we want this to be true
        # pdb.set_trace()

    def test_aliasing2(self):
        one = 'Baton Rouge Parish'
        two = 'East Baton Rouge Parish'
        onejson = get_json(one)
        twojson = get_json(two)
        jac = compute_jaccard_index(onejson, twojson)
        test = mergeable(one, two)

    def test_aliasing3(self):
        #  to do: I don't like this. But..
        one = 'New Orleans Police Department'
        two = 'New Orleans Recreation Department'
        onejson = get_json(one)
        twojson = get_json(two)
        jac = compute_jaccard_index(onejson, twojson)
        test = mergeable(one, two)

    def test_aliasing4(self):
        #  to do: I don't like this. But..Karr High into Edna Karr High
        one = 'Karr High'
        two = 'Edna Karr High'
        counts = pickle.load(open("counts.p", "rb"))
        joint_counts = pickle.load(open("joint_counts.p", "rb"))
        pmi = calculate_pmi(one, two, counts, joint_counts)
        self.assertTrue(isinstance(pmi, float))

    def test_aliasing5(self):
        #  to do: I don't like this. But..Karr High into Edna Karr High
        one = 'New Orleans Recreation'
        two = 'New Orleans Recreation Department'
        counts = pickle.load(open("counts.p", "rb"))
        joint_counts = pickle.load(open("joint_counts.p", "rb"))
        pmi = calculate_pmi(one, two, counts, joint_counts)
        print "\n"
        print one + " " + two
        print "\npmi: " + str(pmi)
        self.assertTrue(isinstance(pmi, float))

    def test_aliasing6(self):
        #  to do: I don't like this. But..Karr High into Edna Karr High
        one = 'Paul Vallas'
        two = 'Superintendent Paul Vallas'
        counts = pickle.load(open("counts.p", "rb"))
        joint_counts = pickle.load(open("joint_counts.p", "rb"))
        pmi = calculate_pmi(one, two, counts, joint_counts)
        print "\n"
        print one + " " + two
        print "\npmi: " + str(pmi)
        self.assertTrue(isinstance(pmi, float))

    def test_aliasing7(self):
        #  to do: I don't like this. But..Karr High into Edna Karr High
        one = 'annual budget'
        two = 'annual budget hearing'
        counts = pickle.load(open("counts.p", "rb"))
        joint_counts = pickle.load(open("joint_counts.p", "rb"))
        pmi = calculate_pmi(one, two, counts, joint_counts)
        print "\n"
        print one + " " + two
        print "\npmi: " + str(pmi)
        self.assertTrue(isinstance(pmi, float))

    def test_aliasing8(self):
        #  to do: I don't like this. But..Karr High into Edna Karr High
        one = 'reform advocates'
        two = 'justice reform advocates'
        counts = pickle.load(open("counts.p", "rb"))
        joint_counts = pickle.load(open("joint_counts.p", "rb"))
        pmi = calculate_pmi(one, two, counts, joint_counts)
        print "\n"
        print one + " " + two
        print "\npmi: " + str(pmi)
        self.assertTrue(isinstance(pmi, float))

    def test_aliasing9(self):
        #  to do: I don't like this. But..Karr High into Edna Karr High
        one = 'executive session'
        two = '10-minute executive session'
        counts = pickle.load(open("counts.p", "rb"))
        joint_counts = pickle.load(open("joint_counts.p", "rb"))
        pmi = calculate_pmi(one, two, counts, joint_counts)
        print "\n"
        print one + " " + two
        print "\npmi: " + str(pmi)
        self.assertTrue(isinstance(pmi, float))

    def test_aliasing10(self):
        #  to do: I don't like this. But..Karr High into Edna Karr High
        one = 'police chief'
        two = 'new police chief'
        counts = pickle.load(open("counts.p", "rb"))
        joint_counts = pickle.load(open("joint_counts.p", "rb"))
        pmi = calculate_pmi(one, two, counts, joint_counts)
        print "\n"
        print one + " " + two
        print "pmi: " + str(pmi)
        self.assertTrue(isinstance(pmi, float))

    def test_aliasing11(self):
        #  to do: I don't like this. But..Karr High into Edna Karr High
        one = 'Landrieu administration'
        two = 'Landrieu administration officials'
        counts = get_picked("counts.p")
        joint_counts = pickle.load(open("joint_counts.p", "rb"))
        pmi = calculate_pmi(one, two, counts, joint_counts)
        print "\n"
        print one + " " + two
        print "pmi: " + str(pmi)
        self.assertTrue(isinstance(pmi, float))


# teachers union
# teachers unions

if __name__ == '__main__':
    unittest.main()
