import unittest
import time
import collections
from rookie.utils import query_elasticsearch
from rookie.utils import query_results_to_bag_o_words
from rookie.utils import clean_punctuation
from rookie.utils import penn_to_wordnet


class GenericTestCase(unittest.TestCase):

    def test_query_wrapper(self):
        results = query_elasticsearch("OPSB")
        dummylist = []
        self.assertEqual(type(results), type(dummylist))

    def test_clean_punctuation(self):
        string = "I think . this should clean all ? of the ! punctuation"
        new_string = clean_punctuation(string)
        target = "I think  this should clean all  of the  punctuation"
        self.assertEqual(new_string, target)

    def test_len_result(self):
        results = query_elasticsearch("OPSB")
        result = results.pop()
        self.assertTrue(len(result.headline) > 0)

    def test_links(self):
        results = query_elasticsearch("OPSB")
        result = results.pop()
        dummylist = []
        self.assertTrue(type(result.links), dummylist)

    def test_node_degrees(self):
        results = query_elasticsearch("OPSB")
        result = results.pop()
        self.assertTrue(len(result.entities.keys()) > 0)

    def test_penn_to_wordnet(self):
        wn_tag = penn_to_wordnet('WRB')
        self.assertEqual("o", wn_tag)

    def test_penn_to_wordnet_2(self):
        wn_tag = penn_to_wordnet('NNP')
        self.assertEqual("n", wn_tag)

    def test_word_split(self):
        start_time = time.time()
        results = query_elasticsearch("sheriff")
        bag_o_query_words = query_results_to_bag_o_words(results)
        words = collections.Counter(bag_o_query_words)
        print("--- %s seconds ---" % (time.time() - start_time))
        for letter, count in words.most_common(9):
            print '%s: %7d' % (letter, count)


if __name__ == '__main__':
    unittest.main()
