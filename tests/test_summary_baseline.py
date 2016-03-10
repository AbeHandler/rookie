"""
Unit tests for the summary baseline
"""

import unittest
from webapp.models import query, Parameters
from summarization.baseline import prepare_sentences


class TestStuff(unittest.TestCase):
    '''
    Tests
    '''

    def test_get_sentences_for_query(self):
        params = Parameters()
        params.q = "Mitch Landrieu"
        params.corpus = "lens"
        results = query("Mitch Landrieu", "lens")
        sss = prepare_sentences(results, params.q, params.f)
        sd = [i for i in sss if i["has_q"]]
        #print sd
        self.assertTrue(len(sents) > 0)

    def test_draw(self):
        self.assertEqual("returns the middle sentence from a pile", 4)

    def test_full_algo(self):
        self.assertEqual("the whole", "thing works")

if __name__ == '__main__':
    unittest.main()
