"""
Unit tests for the summary baseline
"""

import unittest
from webapp.models import query, Parameters
from summarization.baseline import * 
BUFFERCHARS = 4

def params_setup():
    '''get some params for q'''
    params = Parameters()
    params.q = "Mitch Landrieu"
    params.corpus = "lens"
    return params

class TestStuff(unittest.TestCase):
    '''
    Tests
    '''

    def test_get_sentences_for_query(self):
        """test get sentences"""
        params = params_setup()
        results = query("Mitch Landrieu", "lens")
        sss = prepare_sentences(results, params.q, params.f)
        sd = [i for i in sss if i["has_q"]]
        self.assertTrue(len(sd) > 0)

    def test_empty_token_span(self):
        """test mid way cut"""
        params = params_setup()
        results = query(params.q, params.corpus)
        sents = prepare_sentences(results, params.q, params.f)
        sent = select_mid([sen for sen in sents if sen["has_q"] == False])
        blank_to = pluck_tokens(params.q, sent, BUFFERCHARS)
        self.assertEqual(len(blank_to), 0)

    def test_nonempty_token_span(self):
        """test mid way cut"""
        params = params_setup()
        results = query(params.q, params.corpus)
        sents = prepare_sentences(results, params.q, params.f)
        sent = select_mid([sen for sen in sents if sen["has_q"] == True])
        summary = pluck_tokens(params.q, sent, BUFFERCHARS)
        self.assertTrue(len(summary) > len(params.q))

    def test_full_algo(self):
        """test full algo"""
        self.assertEqual("the whole", "thing works")

if __name__ == '__main__':
    unittest.main()
