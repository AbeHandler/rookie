import unittest
from rookie.utils import query_elasticsearch
from rookie.utils import query_results_to_bag_o_words
from rookie.utils import POS_tag
from rookie.utils import penn_to_wordnet
from rookie.datamanagement.lensloader import extract_article_entities

import pdb
import time
import collections


class GenericTestCase(unittest.TestCase):

    def test_query_wrapper(self):
        results = query_elasticsearch("OPSB")
        dummylist = []
        self.assertEqual(type(results), type(dummylist))

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

    def test_POS_tag(self):
        tags = POS_tag("Hello operator, please give me number nine")
        self.assertEqual(tags[1][1], "NN")  # operator is noun in PENN tbank

    def test_penn_to_wordnet(self):
        wn_tag = penn_to_wordnet('WRB')
        self.assertEqual("o", wn_tag)

    def test_penn_to_wordnet_2(self):
        wn_tag = penn_to_wordnet('NNP')
        self.assertEqual("n", wn_tag)

    def test_extrat_article_entities(self):
        sentence = "Professor James Duncan teaches at the Univerisity of Utah"
        entities = extract_article_entities([sentence])
        self.assertEqual("n", wn_tag)

    def test_word_split(self):
        start_time = time.time()
        results = query_elasticsearch(stem("sheriff"))
        bag_o_query_words = query_results_to_bag_o_words(results)
        words = collections.Counter(bag_o_query_words)
        print("--- %s seconds ---" % (time.time() - start_time))
        for letter, count in words.most_common(9):
            print '%s: %7d' % (letter, count)


if __name__ == '__main__':
    unittest.main()
