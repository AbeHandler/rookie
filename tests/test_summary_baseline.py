"""
Unit tests for the summary baseline
"""

import unittest
from webapp.models import query
from summarization.baseline import get_sentences_for_query

class TestStuff(unittest.TestCase):
    '''
    Tests
    '''

    def test_get_sentences_for_query(self):
        self.assertEqual("a query yields sentences", 3)

    def test_draw(self):
        self.assertEqual("returns the middle sentence from a pile", 4)

    def test_full_algo(self):
        self.assertEqual("the whole", "thing works")

if __name__ == '__main__':
    unittest.main()
