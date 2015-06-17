import unittest
import time
import collections
from rookie.utils import query_elasticsearch
from rookie.utils import query_results_to_bag_o_words
from rookie.utils import clean_punctuation


class GenericTestCase(unittest.TestCase):

    def test_clean_punctuation(self):
        string = "I think . this should clean all ? of the ! punctuation"
        new_string = clean_punctuation(string)
        target = "I think  this should clean all  of the  punctuation"
        self.assertEqual(new_string, target)

    def test_len_result(self):
        results = query_elasticsearch("OPSB")
        result = results.results.pop()
        self.assertTrue(len(result.headline) > 0)

if __name__ == '__main__':
    unittest.main()
